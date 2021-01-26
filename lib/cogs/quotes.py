from discord.ext.commands import Cog, command
from discord import Embed
from ..db import db


class Quotes(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name="wisdom", aliases=["quotes"])
    async def wisdom(self, ctx):
        quote, author, user_id = db.record("SELECT Quote, Author, UserID FROM quotes order by RANDOM() LIMIT 1")
        embed = Embed(title="Wisdom",
                      description=quote,
                      colour=0xF6AE2D)
        fields = [("Author", author, False),
                  ("Submitted by", f"<@{user_id}>", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)

    @command(name="addquote", aliases=["aq"])
    async def addquote(self, ctx, *, quote_str: str):
        quote, author = (str(term) for term in quote_str.split("$"))
        db.execute("INSERT INTO quotes (Quote, Author, UserID) VALUES(?, ?, ?)",
                   quote, author, ctx.author.id)
        await ctx.send("Quote added.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("quotes")


def setup(bot):
    bot.add_cog(Quotes(bot))
