import json

import discord
from discord.ext import commands
from discord.ext.commands import BadArgument

from cogs.menu import ListItem, MarketMenu
from cogs.utils.DataBase.Items import Item, ItemDB, TradeDB
from cogs.utils.errors import BadListType
from cogs.utils.functions import convert_quantity, to_lower, listing_args, StockConverter, CompleteConvertor, \
    TradeConvertor
from cogs.utils.DataBase.guild import User, Filter
from cogs.utils.DataBase.trades import Trades
from cogs.utils.checks import is_staff, is_trusted
from cogs.utils.embeds import listing_embed, command_error


class Trade(commands.Cog):
    def __init__(self, bot):

        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def market(self, ctx):
        """List your items to be shown in the dank market"""
        pass
        fil = Filter(None, order_by='price')
        user = User(ctx.guild, self.bot, ctx.author)
        listings = await user.get_items('all', fil)
        pages = MarketMenu(listings[:5], ctx, f"Costliest items in the market")
        await pages.start(ctx)

    @market.command()
    async def sell(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        """List items that you want to sell for money"""
        query_obj = ItemDB(self.bot, item, [quantity, price, ctx.author.id, "sell"])
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def buy(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        """List item that you want to buy with money"""
        query_obj = ItemDB(self.bot, item, [quantity, price, ctx.author.id, "buy"])
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def trade(self, ctx, list_type: to_lower, user_item: StockConverter, *, items: TradeConvertor):
        """List items that you want to trade for other items"""
        query = TradeDB(self.bot, list_type, user_item, items, ctx.author)
        uid = await query.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def remove(self, ctx, uid: int = None):
        """Remove one of your listings from the market"""
        if uid is None:
            raise BadArgument
        user = User(ctx.guild, self.bot, ctx.author)
        await user.remove_listing(uid)
        await ctx.send("removed listing")

    @market.command()
    async def search(self, ctx, list_type: to_lower = 'all', items: str = None, *, query: str = None):
        """Search the market for items that you want to sell or need"""  # TODO: add help to market(filter)
        user = User(ctx.guild, self.bot, ctx.author)
        if items.lower() == "none":
            items = None
        else:
            items = [Item.convert(ctx, item) for item in items.split(',')]
        args = listing_args(items, query)
        listings = await user.get_items(list_type, args)
        for listing in listings:
            trader = await self.bot.db.get_user(listing['user_id'])
            if not (set(trader['guilds']) & set(user.data['guilds'])):
                listings.remove(listing)
        pages = ListItem(listings, ctx, f"Search results")
        await pages.start(ctx)

    @commands.command()
    async def list(self, ctx, members: commands.Greedy[discord.Member] = None, *, args: listing_args = Filter(None)):
        """List your market or other user's market listings"""
        user = User(ctx.guild, self.bot, ctx.author)
        if members is None:
            members = [user]
        else:
            members = [User(ctx.guild, self.bot, mem) for mem in members]

        listings = []
        args.user_id = 1
        for mem in members:
            listings.extend(await mem.get_listings('all', args))
        if len(members) == 1:
            members = members[0].user.mention
        else:
            members = ", ".join([member.user.mention for member in members])
        pages = ListItem(listings, ctx, f"Listings of {members}")
        await pages.start(ctx)

    @commands.command()
    async def listing(self, ctx, uid: int):
        # TODO: view guild settings
        """Get detailed info on a market listing"""
        record = await ItemDB.get_listing(ctx, uid)
        author = User(ctx.guild, self.bot, ctx.author)
        await author.get_data()
        trader = await self.bot.db.get_user(record.data[2])  # user_id
        if trader['user_id'] != ctx.author.id:
            common_guilds = await self.get_common_guilds(
                common_guilds=set(trader['guilds']) & set(author.data['guilds']))
        else:
            common_guilds = None
        await ctx.send(embed=listing_embed(record.record, trader, ctx.author, self.bot.get_user(int(record.data[2])),
                                           common_guilds, record.trade))

    async def completer(self, ctx, traders, items, total, verified):
        trade_type = items[0]
        items = items[1:]
        if trade_type == 'money':
            for trader in traders:
                items = items[0]
                text = await trader.complete_trade(items[0], total, items[1])

                await ctx.send(f"{trader.user.mention} {text}")
            items = dict({items[0]: items[1]})
        else:
            for trader in enumerate(traders):
                item, quantity = max(items[trader[0], lambda x: x.value()])
                text = await trader[1].complete_trade(item, total, quantity)
                await ctx.send(f"{trader[1].user.mention} {text}")
            items[0].update(items[1])
        trade = Trades(self.bot, [traders[0].user.id, traders[1].user.id, trade_type, json.dumps(items)],
                       verified=verified)
        await trade.add()

    @commands.check_any(commands.check(is_trusted), commands.check(is_staff))
    @commands.command(description="Can only used be trust level 10 users and guild staff", aliases=['com', 'cplt'])
    async def complete(self, ctx, traders: commands.Greedy[discord.Member], total: convert_quantity, *,
                       items: CompleteConvertor):
        """Complete a trade between two users"""

        if len(traders) != 2:
            raise BadArgument
        traders = [User(ctx.guild, self.bot, trader) for trader in traders]
        await self.completer(ctx, traders, items, total, True)

    @commands.command(aliases=['cmy'])
    async def complete_my(self, ctx, trader: discord.Member, total: convert_quantity, *, items: CompleteConvertor):
        traders = [User(ctx.guild, self.bot, trader), User(ctx.guild, self.bot, ctx.author)]
        await self.completer(ctx, traders, items, total, False)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, BadListType):
            await ctx.send(embed=command_error(BadListType(f"list type has to be one of `'sell', 'buy', 'all'`.\n "
                                                           f"use {ctx.prefix}help {ctx.command} for more info")))
        await ctx.send(embed=command_error(error))

    async def get_invite(self, guild):
        try:
            invite = await guild.vanity_invite()
            invite = invite.url
        except discord.Forbidden:
            invite = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        except discord.HTTPException:
            invites = await guild.invites()
            invite = [inv.url for inv in invites if inv.inviter.id == self.bot.user.id]
            if len(invite) == 0:
                channels = guild.channels
                state = 0
                for channel in channels:
                    try:
                        invite = await channel.create_invite(reason="Promo")
                        state = 1
                        break
                    except discord.NotFound:
                        continue
                if not state:
                    invite = invite.url
                else:
                    invite = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            else:
                invite = invite[0]
        return invite

    async def get_common_guilds(self, common_guilds):
        common_guilds = list(map(self.bot.get_guild, common_guilds))
        if len(common_guilds) == 0:
            return None
        return [f"[{guild.name}]({await self.get_invite(guild)})" for guild in common_guilds if guild is not None]


def setup(bot):
    bot.add_cog(Trade(bot))
