from discord.ext.commands import check


def is_in_channel(channel_id):
    async def predicate(ctx):
        return ctx.channel and ctx.channel.id == channel_id
    return check(predicate)


def in_philosophy():
    async def predicate(ctx):
        return ctx.guild and ctx.guild.id == 696423795128402023
    return check(predicate)
