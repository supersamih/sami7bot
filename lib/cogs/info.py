from discord.ext.commands import Cog, command
from discord import Embed, Member
from typing import Optional
from datetime import datetime
from ..bot import functions


class Info(Cog):
    def __init__(self, bot):
        self.bot = bot

    @functions.in_philosophy()
    @command(name="userinfo")
    async def user_info(self, ctx, target: Optional[Member]):
        target = target or ctx.author
        if target.activity:
            activity = f"{str(target.activity.type).split('.')[-1].title()}: {target.activity.name}"
        else:
            activity = "N/A"
        embed = Embed(title="User information",
                      colour=target.colour,
                      timestamp=datetime.utcnow())
        embed.set_thumbnail(url=target.avatar_url)
        fields = [("ID", target.id, False),
                  ("Name", str(target), True),
                  ("Bot?", target.bot, True),
                  ("Status", str(target.status).capitalize(), True),
                  ("Activity", f"{activity}", True),
                  ("Created on:", target.created_at.strftime("%d/%m/%y %H:%M:%S"), True),
                  ("Joined on:", target.joined_at.strftime("%d/%m/%y %H:%M:%S"), True),
                  ("Boosted?", bool(target.premium_since), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @functions.in_philosophy()
    @command(name="serverinfo")
    async def server_info(self, ctx):
        embed = Embed(title="Server Information",
                      colour=ctx.guild.owner.colour,
                      timestamp=datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        fields = [("ID", ctx.guild.id, False),
                  ("Owner", ctx.guild.owner, True),
                  ("Region", str(ctx.guild.region).capitalize(), True),
                  ("Created on", ctx.guild.created_at.strftime("%d/%m/%y %H:%M:%S"), False),
                  ("Number of members", len(ctx.guild.members), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("info")


def setup(bot):
    bot.add_cog(Info(bot))
