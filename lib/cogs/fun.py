from typing import Optional
from discord.ext.commands import Cog, command, BadArgument
# from discord.ext.commands import BucketType, cooldown
from discord import Embed, Member
from random import randint, choice
# import pokebase as pb
from aiohttp import request


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="love", aliases=["7b"])
    async def love(self, ctx):
        await ctx.send(f"I love you {ctx.author.mention} :heart:")

    @command(name="roll")
    # @cooldown(1, 15, BucketType.default)
    async def roll(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))
        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("Too many dice pick 25 or lower!")

    @command(name="slap")
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        await ctx.send(f"{ctx.author.display_name} slapped {member.mention} for {reason}")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("That guy isn't here")

    @command(name="echo", aliases=["say"])
    async def echo_message(self, ctx, *, message):
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="nana")
    async def nana(self, ctx):
        await ctx.send(f'Did you know Nana is awesome, {ctx.author.mention} ?')

    @command(name="mowafak")
    async def mowafak(self, ctx):
        mowafak_list = ["a life", "a wife", "a job", "a game partner", "his dick", "someone to bother",
                        "someone to love", "someone to care", "a friend", "Samih to give a fuck",
                        "his shirt", "a pound coin", "an open gym", "someone to make him a sandwich",
                        "a drink", "a business plan"]
        await ctx.send(f'Mowafak is looking for {choice(mowafak_list)}, can anyone help?')

    @command(name="saoie")
    async def saoie(self, ctx):
        await ctx.send("Nana's wife <:saoiePeek:759791733490843648>")

    @command(name="joke")
    async def joke(self, ctx):
        URL = "https://some-random-api.ml/joke"
        async with request("GET", URL) as response:
            if response.status == 200:
                joke = await response.json()
                await ctx.send(joke["joke"])
            else:
                await ctx.send(f"Error: {response.status}")

    @command(name="fact")
    async def animal_fact(self, ctx, animal: str):
        if (animal := animal.lower()) in ["cat", "dog", "panda", "fox", "bird", "koala"]:
            fact_url = f"https://some-random-api.ml/facts/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"
            async with request("GET", image_url) as response:
                if response.status == 200:
                    data = await response.json()
                    image_link = data["link"]
                else:
                    image_link = None

            async with request("GET", fact_url, headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    embed = Embed(title=f"{animal.title().capitalize()} Fact",
                                  description=data["fact"],
                                  colour=0xF6AE2D)
                    if image_link is not None:
                        embed.set_image(url=image_link)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"Oops didn't work: {response.status}")
        else:
            await ctx.send("Oops didn't work: Pick from cat, dog, panda, fox, koala and bird")

    @command(name="pikachu")
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

    @command(name="doggo")
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

    @command(name="charizard")
    async def charizard(self, ctx):
        URL = "https://play.pokemonshowdown.com/sprites/ani/charizard.gif"
        embed = Embed(title="charizard",
                      colour=0xF6AE2D)
        embed.set_image(url=URL)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
