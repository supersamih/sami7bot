from discord.ext.commands import check
from discord import Embed
import asyncio


def is_in_channel(channel_id):
    async def predicate(ctx):
        return ctx.channel and ctx.channel.id == channel_id
    return check(predicate)


def in_philosophy():
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == 696423795128402023
    return check(predicate)


async def embed_cycler(self, embed, message, listDescription):
    embedInfo = embed.to_dict()
    if "thumbnail" in embedInfo:
        embedURL = embedInfo["thumbnail"]["url"]
    else:
        embedURL = ""
    if "title" in embedInfo:
        embedTitle = embedInfo["title"]
    else:
        embedTitle = ""
    if "color" in embedInfo:
        embedColor = embedInfo["color"]
    else:
        embedColor = 0
    x = 0
    y = 15

    def check(reaction, user):
        return str(reaction.emoji) in ["◀️", "▶️", "❌"] and user != self.bot.user

    loop = 1
    while loop:
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
        except asyncio.TimeoutError:
            embed.set_footer(text="Session finished")
            await message.edit(embed=embed)
            loop = 0
        else:
            if str(reaction.emoji) == "◀️":
                if x - 15 >= 0:
                    x -= 15
                    y -= 15
                    embed = Embed(title=embedTitle,
                                  description="\n".join(listDescription[x:y]),
                                  colour=embedColor)
                    embed.set_thumbnail(url=embedURL)
                    await message.edit(embed=embed)
            if str(reaction.emoji) == "▶️":
                if y + 15 <= len(listDescription) + 15:
                    x += 15
                    y += 15
                    embed = Embed(title=embedTitle,
                                  description="\n".join(listDescription[x:y]),
                                  colour=embedColor)
                    embed.set_thumbnail(url=embedURL)
                    await message.edit(embed=embed)
            if str(reaction.emoji) == "❌":
                embed.set_footer(text="Session finished")
                await message.edit(embed=embed)
                loop = 0
