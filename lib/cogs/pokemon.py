from discord.ext.commands import Cog, command, has_permissions, CommandOnCooldown
from discord import Embed, Message
from ..db import db
from aiohttp import request
from random import randint
from discord.ext.commands import BucketType, cooldown
from typing import Optional
from discord import Member
from ..bot import functions


class Pokemon(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="pokeroll", aliases=["pr", "poke", "pokemon"])
    @functions.is_in_channel(811239328415350805)
    @cooldown(1, 10800, type=BucketType.member)
    async def pokeroll(self, ctx):
        URL = f"https://pokeapi.glitch.me/v1/pokemon/{randint(1,386)}"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                name, sprite, number, legendary, mythical = data[0]["name"], data[0]["sprite"], data[0]["number"], data[0]["legendary"], data[0]["mythical"]
                if randint(1, 10000) <= 100:
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

    @pokeroll.error
    async def pokeroll_error(self, ctx, exc):
        if isinstance(exc, CommandOnCooldown):
            m, s = divmod(exc.retry_after, 60)
            h, m = divmod(m, 60)
            if h:
                await ctx.send(f"You can catch another pokemon in **{int(h)} hrs {int(m)} mins** and **{int(s)} secs.**")
            elif m:
                await ctx.send(f"You can catch another pokemon in **{int(m)} mins** and **{int(s)} secs.**")
            else:
                await ctx.send(f"You can catch another pokemon in **{int(s)} secs.**")

    @command(name="pokedex", aliases=["pd"])
    @functions.is_in_channel(811239328415350805)
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
                      colour=16711680,
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        pokeEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(pokeEmbed, "◀️")
        await Message.add_reaction(pokeEmbed, "▶️")
        await Message.add_reaction(pokeEmbed, "❌")
        await functions.embed_cycler(self, embed, pokeEmbed, desc)

    @command(name="leaderboard", aliases=["lb"])
    async def leaderboard(self, ctx, _type: Optional[str]):
        _type = _type or "l"
        if (_type := _type.lower()) in ["l", "legendary", "s", "shiny", "p", "pokemon"]:
            if (_type := _type.lower()) in ["l", "legendary"]:
                x = 0
                y = 15
                lbDescrption = ["Trainer - Legendaries\n"]
                lb = db.records("SELECT TrainerID, Total from leaderboard")
                lb.sort(key=lambda x: x[1], reverse=True)
                for record in lb:
                    rank = lb.index(record) + 1
                    lbDescrption.append(f"**{rank}.** <@{record[0]}> - {record[1]}")
                embed = Embed(title="Leaderboard",
                              description="\n".join(lbDescrption[x:y]),
                              colour=ctx.author.colour)
            elif (_type := _type.lower()) in ["p", "pokemon"]:
                x = 0
                y = 15
                lbDescrption = ["Trainer - Pokemon\n"]
                lb = db.records("SELECT TrainerID, Pokemon from leaderboard")
                lb.sort(key=lambda x: x[1], reverse=True)
                for record in lb:
                    rank = lb.index(record) + 1
                    lbDescrption.append(f"**{rank}.** <@{record[0]}> - {record[1]}")
                embed = Embed(title="Leaderboard",
                              description="\n".join(lbDescrption[x:y]),
                              colour=ctx.author.colour)
            elif (_type := _type.lower()) in ["s", "shiny"]:
                x = 0
                y = 15
                lbDescrption = ["Trainer - Shinies\n"]
                lb = db.records("SELECT TrainerID, Shinies from leaderboard")
                lb.sort(key=lambda x: x[1], reverse=True)
                for record in lb:
                    rank = lb.index(record) + 1
                    lbDescrption.append(f"**{rank}.** <@{record[0]}> - {record[1]}")
                embed = Embed(title="Leaderboard",
                              description="\n".join(lbDescrption[x:y]),
                              colour=ctx.author.colour)
            lbEmbed = await ctx.send(embed=embed)
            await Message.add_reaction(lbEmbed, "◀️")
            await Message.add_reaction(lbEmbed, "▶️")
            await Message.add_reaction(lbEmbed, "❌")
            await functions.embed_cycler(self, embed, lbEmbed, lbDescrption)
        else:
            await ctx.send("To access the leaderboards do >lb with either p, s or l as the command.\n```Like this >lb p```")

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
