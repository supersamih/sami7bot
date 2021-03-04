from discord.ext.commands import Cog, command, has_permissions
from discord.ext.commands import BucketType, cooldown
from discord import Embed
from ..db import db
from ..bot import functions


class Quotes(Cog):
    def __init__(self, bot):
        self.bot = bot

    @functions.in_philosophy()
    @command(name="wisdom", aliases=["quotes", "quote"])
    @cooldown(1, 60, type=BucketType.guild)
    async def wisdom(self, ctx):
        quote_id, quote, author, user_id = db.record("SELECT QuoteID, Quote, Author, UserID FROM quotes order by RANDOM() LIMIT 1")
        embed = Embed(title="Wisdom",
                      description=quote,
                      colour=0xF6AE2D)
        fields = [("Author", author, False),
                  ("Submitted by", f"<@{user_id}>", False)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_footer(text=f"{quote_id}")
        await ctx.send(embed=embed)

    @functions.in_philosophy()
    @command(name="addquote", aliases=["aq"])
    async def addquote(self, ctx, *, quote_str: str):
        await ctx.message.delete()
        if "$" in quote_str:
            quote, author = (str(term) for term in quote_str.split("$"))
            db.execute("INSERT INTO quotes (Quote, Author, UserID) VALUES(?, ?, ?)",
                       quote, author, ctx.author.id)
            await ctx.send("Quote added.", delete_after=5)
        else:
            await ctx.send("Oops that didn't work make sure to use this format 'quote$author'", delete_after=5)

    @functions.in_philosophy()
    @command(name="deletequote", aliases=["dq"], hidden=True)
    @has_permissions(manage_messages=True)
    async def deletequote(self, ctx, q_id: int):
        db.execute("DELETE FROM quotes WHERE QuoteID=?", q_id)
        await ctx.send(f"Entry {q_id} deleted", delete_after=5)

    @functions.in_philosophy()
    @command(name="forcequote", aliases=["fq"], hidden=True)
    @has_permissions(manage_messages=True)
    async def forcequote(self, ctx, q_id: int):
        try:
            quote, author, user_id = db.record("SELECT Quote, Author, UserID FROM quotes where QuoteID=?", q_id)
        except TypeError:
            await ctx.send("That doesn't exist m8", delete_after=5)
        else:
            embed = Embed(title="Wisdom",
                          description=quote,
                          colour=0xF6AE2D)
            fields = [("Author", author, False),
                      ("Submitted by", f"<@{user_id}>", False)]
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
            embed.set_footer(text=f"{q_id}")
            await ctx.send(embed=embed)

    @functions.in_philosophy()
    @command(name="listids", aliases=["lids"], hidden=True)
    @has_permissions(manage_messages=True)
    async def listids(self, ctx):
        all_qids = db.records("SELECT QuoteID from quotes")
        await ctx.send(all_qids)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("quotes")


def setup(bot):
    bot.add_cog(Quotes(bot))
