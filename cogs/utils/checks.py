from discord.ext.commands import CommandError

from cogs.utils.DataBase.guild import Guild, User


class GuildNotSetup(CommandError):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


class NotAStaff(CommandError):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text


async def is_staff(ctx):
    guild = Guild(ctx.guild, ctx.cog.bot)
    await guild.get_data()
    if guild.staff is None:
        raise GuildNotSetup(f" The guild {guild.guild.name} is not setup. Setup with {guild.prefix[0]}setup")
    if not guild.
    if set([role.id for role in ctx.author.roles]) & set(guild.staff):
        return True
    else:
        return False


async def is_trusted(ctx):
    user = User(ctx.guild, ctx.cog.bot, ctx.author)
    await user.get_data()
    if user.data['trust'] == 10:
        return True
    else:
        return False
