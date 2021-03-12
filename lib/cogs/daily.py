from discord.ext.commands import Cog
from aiohttp import request
from discord import Embed
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime


class Daily(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    async def NASA_DAILY(self):
        with open("./lib/cogs/NASAapikey", "r", encoding="utf-8") as nak:
            API_KEY = nak.read()
        message_channel = self.bot.get_channel(800693456015589376)
        URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"
        async with request("GET", URL) as response:
            if response.status == 200:
                data = await response.json()
                title = data["title"]
                description = data["explanation"]
                date = data["date"]
                if data["media_type"] == "video":
                    video_url = data["url"]
                    if "youtube" in video_url:
                        video_url = video_url.replace("embed/", "watch?v=")
                    description += f"\n{video_url}"
                embed = Embed(title=title, description=description, colour=0xF6AE2D)
                if data["media_type"] == "image":
                    image_url = data["hdurl"]
                    embed.set_image(url=image_url)
                embed.add_field(name="Date: ", value=date, inline=False)
                await message_channel.send(embed=embed)
            else:
                await message_channel.send(f"Oops didn't work: {response.status}")

    async def FACT_DAILY(self):
        URL = "https://uselessfacts.jsph.pl/random.json?language=en"
        message_channel = self.bot.get_channel(496397986226634765)
        async with request("GET", URL) as response:
            if response.status == 200:
                fact = await response.json()
                embed = Embed(title="Daily Fact",
                              description=fact["text"],
                              colour=0xF6AE2D)
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/774393693926064129/819297346956820490/H63a7683c84234f498c4dabb89c14b542N.png")
                embed.set_footer(text=datetime.utcnow().strftime("%m/%d/%y"))
                await message_channel.send(embed=embed)
            else:
                await message_channel.send(f"Error: {response.status}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.scheduler.add_job(self.NASA_DAILY, CronTrigger(hour=12, minute=0, second=0))
            self.scheduler.add_job(self.FACT_DAILY, CronTrigger(hour=13, minute=0, second=0))
            self.scheduler.start()
            self.bot.cogs_ready.ready_up("daily")


def setup(bot):
    bot.add_cog(Daily(bot))
