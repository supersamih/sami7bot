from discord.ext.commands import Cog
from aiohttp import request
from discord import Embed
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


class Space(Cog):
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
                if data["media_type"] == "image":
                    image_url = data["hdurl"]
                else:
                    video_url = data["url"]
                    description += f"\n{video_url}"
                embed = Embed(title=title, description=description, colour=0xF6AE2D)
                embed.add_field(name="Date: ", value=date, inline=False)
                embed.set_image(url=image_url)
                await message_channel.send(embed=embed)
            else:
                await message_channel.send(f"Oops didn't work: {response.status}")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.scheduler.add_job(self.NASA_DAILY, CronTrigger(hour=12, minute=0, second=0))
            self.scheduler.start()
            self.bot.cogs_ready.ready_up("space")


def setup(bot):
    bot.add_cog(Space(bot))
