from discord.ext.commands import Cog, command, has_permissions
from discord import Embed, Member, Message
from datetime import datetime
from ..bot import functions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from ..db import db


class Birthdays(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    @command(name="addbirthday", hidden=True)
    @has_permissions(manage_messages=True)
    async def addbirthday(self, ctx, target: Member, bday_date: str):
        bday_date_db = "9999-" + bday_date
        db.execute("INSERT INTO birthdays (UserID, BirthdayDate) VALUES(?, ?)", target.id, bday_date_db)
        await ctx.send(f"{target.mention}'s added to birthday database on {bday_date}")

    @command(name="deletebirthday", hidden=True)
    @has_permissions(manage_messages=True)
    async def deletebirthday(self, ctx, target: Member):
        db.execute("DELETE FROM birthdays WHERE UserID=?", target.id)
        await ctx.send(f"{target.mention}'s birthday was deleted from database")

    @command(name="cleanbirthdaylist", hidden=True)
    @has_permissions(manage_messages=True)
    @functions.is_in_channel(773307586715320360)
    async def cleanbirthdaylist(self, ctx):
        cleanedListOfBirthdaysInDB = []
        listOfMemberIDS = []
        listOfMembersInGuild = ctx.guild.members
        listOfBirthdaysInDB = db.records("SELECT * from birthdays ORDER BY BirthdayDate ASC")
        for record in listOfBirthdaysInDB:
            cleanedListOfBirthdaysInDB.append(record[0])
        for member in listOfMembersInGuild:
            listOfMemberIDS.append(member.id)
        # print(cleanedListOfBirthdaysInDB)
        # print(listOfMemberIDS)
        listOfDeletedMembers = []
        for entry in cleanedListOfBirthdaysInDB:
            if entry not in listOfMemberIDS:
                listOfDeletedMembers += entry
                db.execute("DELETE FROM birthdays WHERE UserID=?", entry)
        await ctx.send(f"Members who have left the server have been cleaned from the DB: {listOfDeletedMembers}")

    @command(name="listbirthdays", hidden=True)
    async def listbirthdays(self, ctx):
        x = 0
        y = 15
        desc = ["User - M/D\n"]
        allbdays = db.records("SELECT * from birthdays ORDER BY BirthdayDate ASC")
        for record in allbdays:
            desc.append(f"<@{record[0]}> - {record[1][5:]}")
        embed = Embed(title="List of birthdays",
                      description="\n".join(desc[x:y]),
                      colour=0x89DAFF,
                      )
        bdayEmbed = await ctx.send(embed=embed)
        await Message.add_reaction(bdayEmbed, "◀️")
        await Message.add_reaction(bdayEmbed, "▶️")
        await Message.add_reaction(bdayEmbed, "❌")
        await functions.embed_cycler(self, embed, bdayEmbed, desc)

    async def birthdaymessage(self):
        date = "9999-" + datetime.utcnow().strftime("%m/%d")
        bdays = db.records("SELECT UserID from birthdays WHERE BirthdayDate = ?", date)
        message_channel = self.bot.get_channel(724338025902899354)
        if bdays:
            for entry in bdays:
                embed = Embed(title=" :confetti_ball: HAPPY BIRTHDAY :confetti_ball: ",
                              description=f"SamihBot loves you  <@{entry[0]}> :heart: and wishes you the happiest of birthdays! May you achieve all your dreams and your next year be <:PogChamp:734092872655175730> \nHere have some cake :cake:\n <:atpRtsd:733675921369858190> ",
                              color=0x89DAFF)
                await message_channel.send(embed=embed)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.scheduler.add_job(self.birthdaymessage, CronTrigger(hour=1, minute=0, second=0))
            self.scheduler.start()
            self.bot.cogs_ready.ready_up("birthdays")


def setup(bot):
    bot.add_cog(Birthdays(bot))
