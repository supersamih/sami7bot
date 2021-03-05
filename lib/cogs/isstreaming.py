from discord.ext.commands import Cog
from discord import ActivityType


class isStreaming(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_member_update(self, before, after):
        if after.id == 115104854573056002 and after.guild.id == 724338025902899351:
            if before.activity == after.activity:
                return
            stream_channel = self.bot.get_channel(732174002361204746)
            async for message in stream_channel.history(limit=200):
                if before.mention and "is streaming on" in message.content:
                    if after.activity:
                        if after.activity.type == ActivityType.streaming:
                            return
            if after.activity:
                if after.activity.type == ActivityType.streaming:
                    stream_url = after.activity.url
                    stream_service = stream_url.split(".")[1].capitalize()
                    await stream_channel.send(f"<@&817016825761103924> Hey guys! {before.mention} is streaming on {stream_service}:\n{stream_url}")
            if before.activity:
                if before.activity.type == ActivityType.streaming:
                    async for message in stream_channel.history(limit=200):
                        if before.mention and "is streaming on" in message.content:
                            await message.delete()
        else:
            return

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("isstreaming")


def setup(bot):
    bot.add_cog(isStreaming(bot))
