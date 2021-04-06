from typing import Optional
from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Member
from random import choice, randint
from aiohttp import request
from ..bot import functions
from datetime import datetime
import json


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @functions.in_philosophy()
    @command(name="love", aliases=["7b", "ashk"])
    async def love(self, ctx):
        await ctx.send(f"I love you {ctx.author.mention} :heart:")

    @functions.in_philosophy()
    @command(name="echo", aliases=["say"], hidden=True, brief="Not for you")
    @has_permissions(manage_messages=True)
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="nana", brief="Nuh Nuh")
    async def nana(self, ctx):
        await ctx.send(f'Did you know Nana is awesome, {ctx.author.mention} ?')

    @command(name="morning", brief="")
    async def morning(self, ctx):
        await ctx.send('Good morning all!\nEspecially Rangemer <:KEKW:809385265608785950>')

    @command(name="moka", brief="ok")
    async def moka(self, ctx):
        await ctx.send(':regional_indicator_m: <:OmegaLUL:808348998519881728> :regional_indicator_k: :regional_indicator_a:')

    @command(name="pogge", brief="old man")
    async def pogge(self, ctx):
        await ctx.send('Old man stop stalling pleaseeeee <:residentsleeper:799712435267043428>')

    @functions.in_philosophy()
    @command(name="mowafak", brief="Some guy I know")
    async def mowafak(self, ctx):
        mowafak_list = ["a life", "a wife", "a job", "a game partner", "his dick", "someone to bother",
                        "someone to love", "someone to care", "a friend", "Samih to give a fuck",
                        "his shirt", "a pound coin", "an open gym", "someone to make him a sandwich",
                        "a drink", "a business plan"]
        await ctx.send(f'Mowafak is looking for {choice(mowafak_list)}, can anyone help?')

    @command(name="saoie",)
    async def saoie(self, ctx):
        await ctx.send("Nana's wife <:saoiePeek:759791733490843648>")

    @functions.in_philosophy()
    @command(name="joke", brief="Get a random joke, haha!")
    async def joke(self, ctx):
        """Gets a random joke"""
        URL = "https://some-random-api.ml/joke"
        async with request("GET", URL) as response:
            if response.status == 200:
                joke = await response.json()
                await ctx.send(joke["joke"])
            else:
                await ctx.send(f"Error: {response.status}")

    @functions.in_philosophy()
    @command(name="fact", hidden=True)
    @has_permissions(manage_messages=True)
    async def fact(self, ctx):
        URL = "https://uselessfacts.jsph.pl/random.json?language=en"
        async with request("GET", URL) as response:
            if response.status == 200:
                fact = await response.json()
                embed = Embed(title="Daily Fact",
                              description=fact["text"],
                              colour=0xF6AE2D)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/774393693926064129/819297346956820490/H63a7683c84234f498c4dabb89c14b542N.png")
                embed.set_footer(text=datetime.utcnow().strftime("%m/%d/%y"))
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Error: {response.status}")

    @functions.in_philosophy()
    @command(name="pikachu", brief="Pikachuuuuuuuu")
    async def pikachu(self, ctx):
        URL = "https://some-random-api.ml/img/pikachu"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                pika = Embed(title="Random Pikachu pic",
                             colour=0xF6AE2D)
                pika.set_image(url=data["link"])
                await ctx.send(embed=pika)
            else:
                await ctx.send(f"Oops didn't work: {response.status}")

    @functions.in_philosophy()
    @command(name="doggo", brief="Apparantly, Everybody loves dogs.")
    async def doggo(self, ctx, breed: Optional[str]):
        if breed:
            URL = f"https://dog.ceo/api/breed/{breed}/images/random"
        else:
            URL = "https://dog.ceo/api/breeds/image/random"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                if breed:
                    dog = Embed(title=f"Here is a cute {breed}",
                                colour=0xF6AE2D)
                else:
                    dog = Embed(title="Here is a cute doggo",
                                colour=0xF6AE2D)
                dog.set_image(url=data["message"])
                await ctx.send(embed=dog)
            else:
                await ctx.send(f"Oops didn't work: {response.status}")

    @functions.in_philosophy()
    @command(name="cat", brief="cats > dogs")
    async def cat(self, ctx):
        headers = {"x-api-key": "5c4ac683-365f-4b78-bd75-d583b173bb70"}
        URL = "https://api.thecatapi.com/v1/images/search"
        async with request("GET", URL, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                embed = Embed(title="Here is a cute cat",
                              colour=0xF6AE2D)
                embed.set_image(url=data[0]["url"])
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Oops didn't work: {response.status}")

    @functions.in_philosophy()
    @command(name="ac", brief="random animal crossing character")
    async def animal_crossing(self, ctx, num: Optional[int]):
        if not num:
            num = randint(1, 391)
        if num >= 1 and num <= 391:
            URL = f"https://acnhapi.com/v1/villagers/{num}"
            async with request("GET", URL) as response:
                if response.status == 200:
                    data = await response.json()
                    embed = Embed(title=data["name"]["name-EUen"],
                                  colour=0xF6AE2D)
                    fields = [("Species:", data["species"], True),
                              ("Gender:", data["gender"], True),
                              ("Birthday:", data["birthday-string"], True),
                              ("Catch Phrase:", data["catch-phrase"], False),
                              ("Saying:", data["saying"], False)]
                    embed.set_thumbnail(url=data["icon_uri"])
                    embed.set_image(url=data["image_uri"])
                    embed.set_footer(text=data["id"])
                    for name, value, inline in fields:
                        embed.add_field(name=name, value=value, inline=inline)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Oops didn't work: {response.status}")
        else:
            await ctx.send("Oops didn't work: Pick a number between 1 and 391")

    @functions.in_philosophy()
    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        URL = "https://g.tenor.com/v1/search?q=slap&key=6NBB1TAZTYHW&limit=40"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                url = data["results"][randint(0, 39)]["media"][0]["gif"]["url"]
                embed = Embed(title=f"**{ctx.author.display_name}** slapped **{member.display_name}** for **{reason}**",
                              colour=ctx.author.colour)
                embed.set_image(url=url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Oops didn't work: {response.status}")

    @functions.in_philosophy()
    @command(name="hug")
    async def hug_member(self, ctx, member: Member):
        URL = "https://g.tenor.com/v1/search?q=wholesome_hug&key=6NBB1TAZTYHW&limit=40"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                url = data["results"][randint(0, 39)]["media"][0]["gif"]["url"]
                embed = Embed(title=f"**{ctx.author.display_name}** hugs **{member.display_name}**",
                              colour=ctx.author.colour)
                embed.set_image(url=url)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Oops didn't work: {response.status}")

    @command(name="regionalindicatorify", aliases=["rify"])
    async def rify(self, ctx, *, text: str):
        with open("./data/rifyDict.json", encoding="utf8") as json_file:
            rifyDict = json.load(json_file)
        textList = list(text.lower())
        finalMessage = ""
        try:
            for char in textList:
                finalMessage += rifyDict[char]
        except KeyError:
            finalMessage = "Pogge broke the bot, actually i thought of a way to fix this issue but ill do it later i cba\nLove from Samih"
        await ctx.send(finalMessage)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
