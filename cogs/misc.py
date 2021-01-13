from discord.ext import commands

from cogs.utils.DataBase.guild import Guild


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(commands.is_owner())
    @commands.command()
    async def verify(self, ctx, verified: bool = True):
        guild = Guild(ctx.guild, self.bot)
        await guild.set_attribute("verified", verified)


def setup(bot):
    bot.add_cog(Misc(bot))
