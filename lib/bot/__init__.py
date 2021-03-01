import os
from asyncio import sleep
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context, BadArgument, MissingRequiredArgument, CommandOnCooldown, CheckFailure
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import Intents, DMChannel, Embed
from discord.errors import Forbidden


from ..db import db


PREFIX = ">"
OWNER_IDS = [114656846664564740]
COGS = []

for _, _, files in os.walk(os.path.join('lib', 'cogs')):
    COGS.extend([file.split(".py")[0] for file in files if file.endswith('.py') and not file.startswith('__')])

IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        self.scheduler = AsyncIOScheduler()
        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

    def run(self, VERSION):
        self.VERSION = VERSION
        print(f"Running setup... V-{VERSION}")
        self.setup()
        with open("./lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running bot..")
        super().run(self.TOKEN)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)
            else:
                await ctx.send("I'm not ready to recieve commands wait a sec m8")

    async def on_connect(self):
        print("connected")

    async def on_disconnect(self):
        print("disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong")

        await self.stdout.send("An error occured.")
        raise

    async def on_command_error(self, ctx, exc):
        if any(isinstance(exc, error) for error in IGNORE_EXCEPTIONS):
            pass

        elif isinstance(exc, CheckFailure):
            await ctx.send("You don't have permission to do this.\nNaughty naughty")

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("One or more required arguments missing")

        elif isinstance(exc, CommandOnCooldown):
            m, s = divmod(exc.retry_after, 60)
            h, m = divmod(m, 60)
            if h:
                await ctx.send(f"You can use this command again in **{int(h)} hrs {int(m)} mins** and **{int(s)} secs.**")
            elif m:
                await ctx.send(f"You can use this command again in **{int(m)} mins** and **{int(s)} secs.**")
            else:
                await ctx.send(f"You can use this command again in **{int(s)} secs.**")

        elif hasattr(exc, "original"):

            if isinstance(exc.original, Forbidden):
                await ctx.send("I can't do that.")
            else:
                raise exc.original
        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.scheduler.start()
            self.guild = self.get_guild(696423795128402023)
            self.stdout = self.get_channel(772882328979636234)
            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send("Online!")
            self.ready = True
            print("bot ready")

        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if message.content.startswith(">secret"):
                    finalmessage = message.content[7:]
                    message_channel = bot.get_channel(778792559668625478)
                    embed = Embed(title="Confession...",
                                  description=finalmessage,
                                  colour=0xFF69B4,)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/784183505625415700/815993484489523230/unknown.png")
                    embed.set_footer(text="From: Secret")
                    await message_channel.send(embed=embed)
                else:
                    await message.channel.send("Sorry, I don't understand what you want.\nIf you want to send a secret please start your message with >secret.")
            await self.process_commands(message)


bot = Bot()
