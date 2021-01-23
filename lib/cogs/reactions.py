from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Message


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
            self.reaction_message = await self.bot.get_channel(802135054771945472).fetch_message(802154728175042560)
            self.bot.cogs_ready.ready_up("reactions")

    @Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.reaction_message.id:
            current_colours = filter(lambda r: r in self.colours.values(), payload.member.roles)
            await payload.member.remove_roles(*current_colours, reason="Colour role react")
            await payload.member.add_roles(self.colours[payload.emoji.name], reason="Colour role react")
            await self.reaction_message.remove_reaction(payload.emoji, payload.member)


def setup(bot):
    bot.add_cog(Reactions(bot))
