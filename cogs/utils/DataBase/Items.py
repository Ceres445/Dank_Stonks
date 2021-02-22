import json
from datetime import datetime

from discord.ext.commands.errors import BadArgument, CommandError

with open("cogs/utils/json_files/items.json", "r") as f:
    items = json.load(f)
items = dict(items)
with open("cogs/utils/json_files/item_convertor.json", "r") as f:
    item_convertor = json.load(f)
item_convertor = dict(item_convertor)


def get_item(name: str) -> dict or None:
    if name in items:
        return name
    for key, i in items.items():
        if name in i:
            return key
    return None


def item_id(item):
    return list(items.keys()).index(item)


class ItemNotFound(CommandError):
    def __init__(self):
        pass


class Item:

    def __init__(self, bot, name, aliases):
        self.bot = bot

        self.name = name

        self.item_id = item_id(name)

        self.aliases = aliases

    @classmethod
    async def convert(cls, ctx, argument):
        item_data = get_item(argument)
        if item_data is None:
            raise ItemNotFound
        return cls(ctx.cog.bot, item_data, items[item_data])

    @classmethod
    def get_item_id(cls, ctx, item_code: int):
        if item_code < 0 or item_code >= len(items):
            raise BadArgument(f"item_id must be an integer in the range of 0 and {len(items)}")
        item = list(items.keys())[item_code]
        return cls(ctx.cog.bot, item, items[item])

    def __repr__(self):
        return self.name


class ItemDB:
    def __init__(self, bot, item, data, code=None, time=None, record=None, trade: bool = False):
        # TODO: use auto incrementing primary keys and change table structure for trades
        self.bot = bot
        self.item_code = item.item_id
        self.data = data
        self.code = code
        self.time = time
        self.record = record
        self.trade = trade

    async def get_code(self):
        codes = await self.bot.db.fetch("SELECT DISTINCT code FROM listed_items")
        code = [code['code'] for code in codes]
        codes = await self.bot.db.fetch("SELECT DISTINCT code FROM traded_items")
        codes_trades = [code['code'] for code in codes]
        if len(code) == 0 and len(codes_trades) == 0:
            return 1
        else:
            return max(code + codes_trades) + 1

    @classmethod
    async def get_listing(cls, ctx, code: int):
        codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code FROM listed_items")
        if code in [cod['code'] for cod in codes]:
            listing = await ctx.cog.bot.db.fetchrow("SELECT * FROM listed_items WHERE code = $1", code)
            return cls(ctx.cog.bot, Item.get_item_id(ctx, listing['item_code']),
                       [listing['quantity'], listing['price'], listing['user_id'], listing['list_type']], code,
                       listing['time'], record=listing)
        else:
            codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code from traded_items")
            if code in [cod['code'] for cod in codes]:
                listing = await ctx.cog.bot.db.fetchrow("SELECT * FROM traded_items WHERE code = $1", code)
                return cls(ctx.cog.bot, Item.get_item_id(ctx, listing['user_item']),
                           [listing['stock'], listing['trade_item'], listing['user_id'], listing['list_type']], code,
                           listing['time'], record=listing, trade=True)
            else:
                raise BadArgument

    async def add(self):
        if not self.trade:
            if self.code is None:
                self.code = await self.get_code()
                query = "INSERT INTO listed_items (code, item_code, quantity, price, user_id, list_type, time) " \
                        "VALUES ($1, $2, $3, $4, $5, $6, $7) "
                await self.bot.db.execute(query,
                                          self.code, self.item_code, *self.data, int(datetime.now().timestamp()))
            return self.code
        else:
            if self.code is None:
                self.code = await self.get_code()
                query = "INSERT INTO traded_items (code,  user_item, list_type, trade_item, stock, user_id, time) " \
                        "VALUES ($1, $2, $3, $4, $5, $6, $7) "
                await self.bot.db.execute(query, self.code, self.item_code, *self.data, int(datetime.now().timestamp()))
                return self.code
