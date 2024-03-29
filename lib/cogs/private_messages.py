from discord.ext.commands import Cog
from discord import DMChannel, Embed
from asyncio import sleep
from random import randint
from datetime import datetime


class Private_messages(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_message")
    async def confession(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if message.content.startswith(">secret"):
                    finalmessage = message.content[7:]
                    message_channel = self.bot.get_channel(778792559668625478)
                    embed = Embed(title="Confession...",
                                  description=finalmessage,
                                  colour=0xFF69B4,)
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/784183505625415700/815993484489523230/unknown.png")
                    embed.set_footer(text="From: Secret")
                    await sleep(randint(30, 600))
                    await message_channel.send(embed=embed)
                else:
                    await message.channel.send("Sorry, I don't understand what you want.\nIf you want to send a secret please start your message with >secret.")

    @Cog.listener("on_message_delete")
    async def cave(self, message):
        if message.author.bot or message.content.startswith(">"):
            return
        cave = self.bot.get_channel(822834005388689499)
        general = self.bot.get_channel(778792559668625478)
        if message.channel == general:
            when = datetime.utcnow().strftime("%H:%M:%S")
            embed = Embed(title=f"Pepega message by: {message.author}",
                          description=f"Message: {message.content}\nDeleted in: {message.channel}",
                          colour=0xFF9B4)
            embed.set_footer(text=f"deleted at {when}")
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/778792559668625478/822838338863890432/pepega.png")
            await cave.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("private_messages")


def setup(bot):
    bot.add_cog(Private_messages(bot))
