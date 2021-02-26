import discord
from discord.ext import commands

from cogs.utils.DataBase.guild import Guild, User


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.is_owner()
    @commands.command()
    async def verify(self, ctx, verified: bool = True):
        guild = Guild(ctx.guild, self.bot)
        await guild.set_attribute("verified", verified)
        await ctx.send(f"{'Unv' if not verified else 'V'}erified {ctx.guild.name}")

    @commands.is_owner()
    @commands.command()
    async def trust(self, ctx, user: discord.Member = None, trust: int = 10):
        if user is not None:
            user = User(ctx.guild, self.bot, user)
            await user.get_data()
            await user.set_attribute("trust", trust)
            await ctx.send(f"set trust of {user.user.display_name} to {trust}")


def setup(bot):
    bot.add_cog(Misc(bot))
