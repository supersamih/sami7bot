from discord.ext.commands import Cog, command
from discord import Embed
from ..db import db
from aiohttp import request
from random import randint
from discord.ext.commands import BucketType, cooldown
# from typing import Optional
# from discord import Member


class Pokemon(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pokeroll", aliases=["pr", "poke", "pokemon"])
    @cooldown(1, 1800, type=BucketType.default)
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
                db.execute("INSERT INTO pokemon (TrainerID, PokeID, PokeName, PokeSprite, Legendary, Mythical) VALUES(?, ?, ?, ?, ?, ?)",
                           ctx.author.id, number, name, sprite, legendary, mythical)
            else:
                await ctx.send(f"Oh no something went wrong, {response.status} Its probably not my fault tho...")

    # @command(name="pokedex", aliases=["pd"])
    # async def pokedex(self, ctx, target: Optional[Member]):
    #     target = target or ctx.author
    #     PokeID, PokeName, Legendary, Mythical = db.execute("SELECT PokeID, PokeName, Legendary, Mythical FROM pokemon WHERE TrainerID = ?", target.id )
    #     await ctx.send(PokeID, PokeName, Legendary, Mythical)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("pokemon")


def setup(bot):
    bot.add_cog(Pokemon(bot))
