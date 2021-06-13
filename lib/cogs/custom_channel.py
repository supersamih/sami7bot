from discord.ext.commands import Cog


class Custom_channel(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener("on_voice_state_update")
    async def joined_trigger_channel(self, member, before, after):
        if member.bot:
            return
        if after.channel is not None:
            # CHANNEL ID
            if after.channel.id == 804814480370171926:
                channel = await self.create_special_channel(after.channel.guild, f"{member.name}'s channel".capitalize())
                if channel is not None:
                    await member.move_to(channel)
        if before.channel is not None:
            # CATEGORY ID
            if before.channel.category.id == 847160948363231232:
                try:
                    if len(before.channel.members) == 0:
                        await before.channel.delete()
                except Exception as e:
                    print(e)

    async def create_special_channel(ctx, guild, channel_name, user_limit=None):
        for c in guild.categories:
            # CATEGORY ID
            if c.id == 847160948363231232:
                category = c
        return await guild.create_voice_channel(channel_name, category=category, user_limit=user_limit)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("custom_channel")


def setup(bot):
    bot.add_cog(Custom_channel(bot))
