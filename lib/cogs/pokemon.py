from discord.ext.commands import Cog, command, has_permissions
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
    @functions.is_in_channel(805615557088378930)
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
                      colour=16711680,
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        pokeEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(pokeEmbed, "◀️")
        await Message.add_reaction(pokeEmbed, "▶️")
        await Message.add_reaction(pokeEmbed, "❌")
        await functions.embed_cycler(self, embed, pokeEmbed, desc)

    @command(name="leaderboard", aliases=["lb"])
    @functions.is_in_channel(805615557088378930)
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

    @command(name="grouppokedex", aliases=["gpd"])
    @functions.is_in_channel(805615557088378930)
    async def grouppokedex(self, ctx):
        desc = [""]
        leg_count = 0
        mythical_count = 0
        x = 0
        y = 15
        pd = db.records("SELECT PokeID, PokeName, SUM(Legendary), SUM(Mythical), SUM(Amount) FROM pokemon GROUP BY PokeID")
        pd.sort(key=lambda x: x[0])
        counter = 0
        for record in pd:
            counter += 1
            if record[0] != counter:
                print(counter)
                counter = record[0]
            if record[2]:
                leg_count += 1
            if record[3]:
                mythical_count += 1
            desc.append(f"{record[0]} - {record[1]} - {record[4]}x")
            if counter != record[0]:
                pass

        desc.insert(0, f"**Pokemon: {len(pd)}/386\nLegendaries: {leg_count}/17\nMythicals: {mythical_count}/4**")
        embed = Embed(title="Group Pokedex",
                      description="\n".join(desc[x:y]),
                      colour=16711680,
                      )
        embed.set_thumbnail(url="https://cdn.bulbagarden.net/upload/9/9f/Key_Pok%C3%A9dex_m_Sprite.png")
        pokeEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(pokeEmbed, "◀️")
        await Message.add_reaction(pokeEmbed, "▶️")
        await Message.add_reaction(pokeEmbed, "❌")
        await functions.embed_cycler(self, embed, pokeEmbed, desc)

    @command(name="pokestats", hidden=True)
    @functions.is_in_channel(805615557088378930)
    async def pokestats(self, ctx):
        pddata = db.records("SELECT PokeID, PokeName, SUM(Amount) FROM pokemon GROUP BY PokeID")
        pddata.sort(key=lambda x: x[2])
        mostdupesserver = pddata[-1]
        mostpkmn = db.records("SELECT TrainerID, count(*) FROM pokemon GROUP BY TrainerID")
        mostpkmn.sort(key=lambda x: x[1])
        mostpokemon = mostpkmn[-1]
        totalpokemon = len(pddata)
        totalrolls = len(db.records("SELECT TrainerID FROM pokemon"))
        mostdupesplayer = db.record("SELECT TrainerID, PokeID, PokeName, MAX(Amount) FROM Pokemon")
        mostrolls = db.record("SELECT TrainerID, MAX(Pokemon) from leaderboard")
        mostshinies = db.record("SELECT TrainerID, MAX(Shinies) from leaderboard")
        mostlegendaries = db.record("SELECT TrainerID, MAX(Total) from leaderboard")
        embed = Embed(title="Everyone loves statistics",
                      description="Stats for the feburary event of Poggemon",
                      colour=ctx.author.colour)
        fields = [("Total rolls:", totalrolls, True),
                  ("Total Pokemon:", f"{totalpokemon}/386", True),
                  ("Most rolls:", f"<@{mostrolls[0]}> with {mostrolls[1]}! ", False),
                  ("Most Unique pokemon:", f"<@{mostpokemon[0]}> with {mostpokemon[1]}! ", True),
                  ("Most dupes (server):", f"Together the server caught {mostdupesserver[1]} {mostdupesserver[2]} times!", False),
                  ("Most dupes (player):", f"<@{mostdupesplayer[0]}> with {mostdupesplayer[3]}x {mostdupesplayer[2]} ", True),
                  ("Most Shinies:", f"<@{mostshinies[0]}> with {mostshinies[1]} Shinies!", False),
                  ("Most Legendaries:", f"<@{mostlegendaries[0]}> with {mostlegendaries[1]} legendaries!", True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="clearpokemon", hidden=True)
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
