from discord.ext.commands import Cog, command
from discord import Embed
from ..db import db
from aiohttp import request
from random import  randint


class Pokemon(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pokeroll", aliases=["pr", "poke", "pokemon"])
    async def pokeroll (self, ctx):
        URL = f"https://pokeapi.glitch.me/v1/pokemon/{randint(1,386)}"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                name = data[0]["name"]
                sprite = data[0]["sprite"]
                embed=Embed(description=f"{ctx.author.mention} rolled a {name}",
                            colour=ctx.author.colour)
                embed.set_image(url = sprite)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Oh no something went wrong, {response.status}")
            


    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("pokemon")


def setup(bot):
    bot.add_cog(Pokemon(bot))