from discord.ext import commands
from cogs.utils.DataBase.Items import Item, convert_quantity, ItemDB
from cogs.utils.DataBase.guild import User
import discord


class Trade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def market(self, ctx, args):
        pass
        # show some help here?

    @market.command()
    async def sell(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        query_obj = ItemDB(self.bot, "sell", item, quantity, price, ctx.author.id)
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def buy(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        query_obj = ItemDB(self.bot, "sell", item, quantity, price, ctx.author.id)
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def remove(self, ctx, uid: str = None):
        user = User(ctx.guild, self.bot, ctx.author)
        await user.remove_listing(uid)
        await ctx.send("removed listing")

    @commands.command()
    async def list(self, ctx, members: commands.Greedy[discord.Member] = None, *args):
        user = User(ctx.guild, self.bot, ctx.author)
        if members is None:
            members = [user]
        else:
            members = [User(ctx.guild, self.bot, mem) for mem in members]

        listings = []
        for mem in members:
            listings.extend(await mem.get_listings('all'))  # TODO: filter args and add filters for listing
        await ctx.send(listings)


def setup(bot):
    bot.add_cog(Trade(bot))
