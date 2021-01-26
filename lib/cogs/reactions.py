from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Message
from datetime import datetime
from ..db import db


class Reactions(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="roles")
    @has_permissions(administrator=True)
    async def roles(self, ctx):
        await ctx.message.delete()
        emojis = ['🟡', '⚫', '🔵', '🟢', '🟠', '🔴', '🟣', '⚪']
        embed = Embed(title="React for roles",
                      description="Everybody loves colours! React to these messages to change your display colour!",
                      colour=ctx.guild.owner.colour)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        sent = await ctx.send(embed=embed)
        for emoji in emojis:
            await Message.add_reaction(sent, emoji)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.colours = {'🟡': self.bot.guild.get_role(802312232033583104),
                            '⚫': self.bot.guild.get_role(802312788663336990),
                            '🔵': self.bot.guild.get_role(802312998261751858),
                            '🟢': self.bot.guild.get_role(802313156445601812),
                            '🟠': self.bot.guild.get_role(802313301962915842),
                            '🔴': self.bot.guild.get_role(802313455998074920),
                            '🟣': self.bot.guild.get_role(802313541582716949),
                            '⚪': self.bot.guild.get_role(802313677898252288)
                            }
            self.reaction_message = await self.bot.get_channel(802135054771945472).fetch_message(802329518722908170)
            self.starboard_channel = self.bot.get_channel(803393663832293406)
            self.bot.cogs_ready.ready_up("reactions")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Colour role react")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role react")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)
        # picking the emoji that will trigger this code
        elif payload.emoji.name == "🌟":
            # get channel and then message from that channel
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            # if not bot or the same person who made the message create this to send to starboard
            if not message.author.bot and payload.member.id != message.author.id:
                msg_id, stars = db.record("SELECT StarMessageID, Stars FROM starboard WHERE RootMessageID = ?",
                                          message.id) or (None, 0)
                embed = Embed(title="Starred message",
                              colour=message.author.colour,
                              timestamp=datetime.utcnow())
                fields = [("Author", message.author.mention, False),
                          ("Content", message.content or "See attachment", False),
                          ("Stars", stars + 1, False)]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                if len(message.attachments):
                    # if message has any attatchments add the first one as an image
                    embed.set_image(url=message.attachments[0].url)
                if not stars:
                    star_message = await self.starboard_channel.send(embed=embed)
                    db.execute("INSERT INTO starboard (RootMessageID, StarMessageID) VALUES(?, ?)",
                               message.id, star_message.id)
                else:
                    star_message = await self.starboard_channel.fetch_message(msg_id)
                    await star_message.edit(embed=embed)
                    db.execute("UPDATE starboard SET Stars = Stars + 1 WHERE RootMessageID = ?",
                               message.id)
            else:
                # else remove the reaction
                await message.remove_reaction(payload.emoji, payload.member)


def setup(bot):
    bot.add_cog(Reactions(bot))
