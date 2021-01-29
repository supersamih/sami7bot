from discord.ext.commands import Cog, command
from discord import Embed, Message
from ..db import db
from aiohttp import request
from random import randint
from discord.ext.commands import BucketType, cooldown
from typing import Optional
from discord import Member
import asyncio


class Pokemon(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pokeroll", aliases=["pr", "poke", "pokemon"])
    @cooldown(1, 3600, type=BucketType.member)
    async def pokeroll(self, ctx):
        URL = f"https://pokeapi.glitch.me/v1/pokemon/{randint(1,386)}"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                name = data[0]["name"]
                sprite = data[0]["sprite"]
                number = data[0]["number"]
                legendary = data[0]["legendary"]
                mythical = data[0]["mythical"]
                embed = Embed(description=f"{ctx.author.mention} just caught a {name}! Added to pokedex.",
                              colour=ctx.author.colour)
                embed.set_image(url=sprite)
                if legendary or mythical:
                    embed.add_field(name="WOW you caught a rare pokemon!", value=f"{name.upper()}!!", inline=False)
                await ctx.send(embed=embed)
                checkID = db.record("SELECT PokeID FROM pokemon WHERE TrainerID = ? AND PokeID = ?", ctx.author.id, number) or 0
                if checkID != 0:
                    db.execute("UPDATE pokemon SET Amount = Amount + 1 WHERE TrainerID=? AND PokeID=?", ctx.author.id, number)
                else:
                    db.execute("INSERT INTO pokemon (TrainerID, PokeID, PokeName, PokeSprite, Legendary, Mythical, Amount) VALUES(?, ?, ?, ?, ?, ?, ?)",
                               ctx.author.id, number, name, sprite, legendary, mythical, 1)

            else:
                await ctx.send(f"Oh no something went wrong, {response.status} Its probably not my fault tho...")

    @command(name="pokedex", aliases=["pd"])
    async def pokedex(self, ctx, target: Optional[Member]):
        target = target or ctx.author
        desc = []
        separator = "\n"
        leg_count = 0
        mythical_count = 0
        x = 0
        y = 25
        pd = db.records("SELECT PokeID, PokeName, Legendary, Mythical, Amount FROM pokemon WHERE TrainerID = ?", target.id)
        pd.sort(key=lambda x: x[0])
        for record in pd:
            if record[2]:
                leg_count += 1
            if record[3]:
                mythical_count += 1
            desc.append(f"{record[0]} - {record[1]} - {record[4]}x")
        desc.insert(0, f"**Uniques: {len(pd)}\nLegendaries: {leg_count}\nMythicals: {mythical_count}**")
        embed = Embed(title=f"{target.name}'s Pokedex",
                      description=separator.join(desc[x:y]),
                      colour=ctx.author.colour
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        pokeEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(pokeEmbed, "◀️")
        await Message.add_reaction(pokeEmbed, "▶️")

        def check(reaction, user):
            return str(reaction.emoji) in ["◀️", "▶️"] and user != self.bot.user
        loop = 1
        while loop:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                await ctx.channel.send(f"{target.name}'s Session expired", delete_after=5)
                loop = 0
            else:
                if str(reaction.emoji) == "◀️":
                    if x - 25 >= 0:
                        x -= 25
                        y -= 25
                        embed = Embed(title=f"{target.name}'s Pokedex",
                                      description=separator.join(desc[x:y]))
                        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
                        await pokeEmbed.edit(embed=embed)
                if str(reaction.emoji) == "▶️":
                    if y + 25 <= len(pd) + 25:
                        x += 25
                        y += 25
                        embed = Embed(title=f"{target.name}'s Pokedex",
                                      description=separator.join(desc[x:y]))
                        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
                        await pokeEmbed.edit(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("pokemon")


def setup(bot):
    bot.add_cog(Pokemon(bot))
