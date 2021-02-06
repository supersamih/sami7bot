from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Message
from ..db import db
from aiohttp import request
from random import randint
from discord.ext.commands import BucketType, cooldown
from typing import Optional
from discord import Member
import asyncio
from ..bot import functions


class Pokemon(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pokeroll", aliases=["pr", "poke", "pokemon"])
    @functions.is_in_channel(805615557088378930)
    @cooldown(1, 15800, type=BucketType.member)
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
                if randint(1, 15000) <= 150:
                    shiny = "Shiny"
                    shinydb = True
                else:
                    shiny = ""
                    shinydb = False

                embed = Embed(description=f"{ctx.author.mention} just caught a {shiny} {name}! Added to pokedex.",
                              colour=ctx.author.colour)
                if shiny:
                    shinyurl = f"https://play.pokemonshowdown.com/sprites/ani-shiny/{name.lower()}.gif"
                    embed.set_image(url=shinyurl)
                else:
                    embed.set_image(url=sprite)
                if legendary or mythical:
                    embed.add_field(name="\u200b", value=f"**WOW!** You caught a **LEGENDARY {name.upper()}!**", inline=False)
                await ctx.send(embed=embed)
                checkID = db.record("SELECT PokeID FROM pokemon WHERE TrainerID = ? AND PokeID = ?", ctx.author.id, number) or 0
                if checkID != 0:
                    db.execute("UPDATE pokemon SET Amount = Amount + 1 WHERE TrainerID=? AND PokeID=?", ctx.author.id, number)
                else:
                    db.execute("INSERT INTO pokemon (TrainerID, PokeID, PokeName, PokeSprite, Legendary, Mythical) VALUES(?, ?, ?, ?, ?, ?)",
                               ctx.author.id, number, name, sprite, legendary, mythical)
                checkLB = db.record("SELECT Pokemon, Shinies, Legendaries, Mythicals from leaderboard where TrainerID = ?", ctx.author.id) or 0
                if not checkLB:
                    db.execute("INSERT INTO leaderboard (TrainerID, Pokemon, Shinies, Legendaries, Mythicals, total) VALUES(?, ?, ?, ?, ?, ?)",
                               ctx.author.id, 1, int(shinydb), int(legendary), int(mythical), (int(mythical) + int(legendary)))
                else:
                    db.execute("UPDATE leaderboard SET Pokemon = Pokemon + 1, Shinies = Shinies + ?, Legendaries = Legendaries + ?, Mythicals = Mythicals + ?, Total = Total + ? WHERE TrainerID = ?",
                               int(shinydb), int(legendary), int(mythical), int(legendary) + int(mythical), ctx.author.id)
            else:
                await ctx.send(f"Oh no something went wrong, {response.status} Its Glimpee's fault")

    @command(name="pokedex", aliases=["pd"])
    @functions.is_in_channel(805615557088378930)
    async def pokedex(self, ctx, target: Optional[Member]):
        target = target or ctx.author
        desc = []
        leg_count = 0
        mythical_count = 0
        x = 0
        y = 15
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
                      description="\n".join(desc[x:y]),
                      colour=ctx.author.colour
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        pokeEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(pokeEmbed, "◀️")
        await Message.add_reaction(pokeEmbed, "▶️")
        await Message.add_reaction(pokeEmbed, "❌")

        def check(reaction, user):
            return str(reaction.emoji) in ["◀️", "▶️", "❌"] and user != self.bot.user
        loop = 1
        while loop:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                embed.set_footer(text="Session finished")
                await pokeEmbed.edit(embed=embed)
                loop = 0
            else:
                if str(reaction.emoji) == "◀️":
                    if x - 15 >= 0:
                        x -= 15
                        y -= 15
                        embed = Embed(title=f"{target.name}'s Pokedex",
                                      description="\n".join(desc[x:y]))
                        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
                        await pokeEmbed.edit(embed=embed)
                if str(reaction.emoji) == "▶️":
                    if y + 15 <= len(pd) + 15:
                        x += 15
                        y += 15
                        embed = Embed(title=f"{target.name}'s Pokedex",
                                      description="\n".join(desc[x:y]))
                        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
                        await pokeEmbed.edit(embed=embed)
                if str(reaction.emoji) == "❌":
                    embed.set_footer(text="Session finished")
                    await pokeEmbed.edit(embed=embed)
                    loop = 0

    @command(name="leaderboard", aliases=["lb"])
    @functions.is_in_channel(805615557088378930)
    async def leaderboard(self, ctx):
        x = 0
        y = 15
        lbDescrption = ["Trainer - Legendaries+\n"]
        lb = db.records("SELECT TrainerID, Legendaries, Mythicals, Total from leaderboard")
        lb.sort(key=lambda x: x[3], reverse=True)
        for record in lb:
            lbDescrption.append(f"<@{record[0]}> - {record[3]}")
        embed = Embed(title="Leaderboard",
                      description="\n".join(lbDescrption[x:y]))
        lbEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(lbEmbed, "◀️")
        await Message.add_reaction(lbEmbed, "▶️")
        await Message.add_reaction(lbEmbed, "❌")

        def check(reaction, user):
            return str(reaction.emoji) in ["◀️", "▶️", "❌"] and user != self.bot.user

        loop = 1
        while loop:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except asyncio.TimeoutError:
                embed.set_footer(text="Session finished")
                await lbEmbed.edit(embed=embed)
                loop = 0
            else:
                if str(reaction.emoji) == "◀️":
                    if x - 15 >= 0:
                        x -= 15
                        y -= 15
                        embed = Embed(title="Leaderboard",
                                      description="\n".join(lbDescrption[x:y]))
                        await lbEmbed.edit(embed=embed)
                if str(reaction.emoji) == "▶️":
                    if y + 15 <= len(lb) + 15:
                        x += 15
                        y += 15
                        embed = Embed(title="Leaderboard",
                                      description="\n".join(lbDescrption[x:y]))
                        await lbEmbed.edit(embed=embed)
                if str(reaction.emoji) == "❌":
                    embed.set_footer(text="Session finished")
                    await lbEmbed.edit(embed=embed)
                    loop = 0

    @command(name="clearpokemon")
    @has_permissions(manage_messages=True)
    @functions.is_in_channel(803393663832293406)
    async def clearpokemon(self, ctx):
        db.execute("DELETE FROM pokemon")
        db.execute("DELETE FROM leaderboard")
        await ctx.send("Pokemon database cleared")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("pokemon")


def setup(bot):
    bot.add_cog(Pokemon(bot))
