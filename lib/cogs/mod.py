from discord.ext.commands import Cog, command, has_permissions, bot_has_permissions
from typing import Optional


class Mod(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="clear", aliases=["purge"])
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, limit: Optional[int] = 1):
        with ctx.channel.typing():
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=limit)
            await ctx.send(f"Deleted {len(deleted):,} messages", delete_after=5)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("mod")


def setup(bot):
    bot.add_cog(Mod(bot))
