
from discord.ext.commands import Cog, command
from discord import Embed
from ..db import db
from aiohttp import request
from random import randint
from discord.ext.commands import BucketType, cooldown
from typing import Optional
from discord import Member


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
                embed = Embed(description=f"{ctx.author.mention} rolled a {name}",
                              colour=ctx.author.colour)
                embed.set_image(url=sprite)
                await ctx.send(embed=embed)
                number = data[0]["number"]
                legendary = data[0]["legendary"]
                mythical = data[0]["mythical"]
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
        desc = ""
        leg_count = 0
        mythical_count = 0
        target = target or ctx.author
        pd = db.records("SELECT PokeID, PokeName, Legendary, Mythical, Amount FROM pokemon WHERE TrainerID = ?", target.id)
        pd.sort(key=lambda x: x[0])
        for record in pd:
            if record[2]:
                leg_count += 1
            if record[3]:
                mythical_count += 1
            desc += f"\n{record[0]} - {record[1]} - {record[4]}x"
        embed = Embed(title=f"{ctx.author.name}'s Pokedex",
                      description=desc,
                      colour=ctx.author.colour
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        embed.insert_field_at(0, name="Uniques: ", value=len(pd), inline=True)
        embed.insert_field_at(1, name="Legendaries: ", value=leg_count, inline=True)
        embed.insert_field_at(2, name="Mythicals: ", value=mythical_count, inline=True)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("pokemon")


def setup(bot):
    bot.add_cog(Pokemon(bot))
