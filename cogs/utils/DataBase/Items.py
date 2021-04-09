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


class TradeDB:
    def __init__(self, bot, list_type, item1, other_items, user, record=None):
        self.bot = bot
        self.list_type = list_type
        self.item1 = item1
        self.items = other_items
        self.record = record
        self.user = user

    @classmethod
    async def get_listing(cls, ctx, code: int):
        codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code from listed_trades")
        if code in [cod['code'] for cod in codes]:
            listing = await ctx.cog.bot.db.fetchrow("SELECT * FROM listed_trades WHERE code = $1", code)
            return cls(ctx.cog.bot, listing['list_type'],
                       {Item.get_item_id(ctx, listing['user_item']): listing['stock']},
                       listing['record_item_code'], ctx.author, record=listing)
        else:
            raise BadArgument("uid supplied was not found in database")

    async def add(self):
        query = "INSERT INTO listed_trades (user_item, list_type,stock, user_id, time) " \
                "VALUES ($1, $2, $3, $4, $5) "
        item, stock = self.item1.items()
        record = await self.bot.db.execute(query, item.item_id, self.list_type, stock, self.user.id,
                                           int(datetime.now().timestamp()))

        query = 'INSERT INTO list_trade_items (item1, item2, list_type, item1_quantity, item2_quantity, trade_code) ' \
                'VALUES ($1, $2, $3, $4, $5, $6) '
        records = await self.bot.db.execute_many(query,
                                                 [(item, i[0], self.list_type, stock, i[1], record['code']) for i in
                                                  self.items])
        self.record = await self.bot.db.execute('UPDATE listed_trades set trade_item_code = $1 WHERE code=$2',
                                                [rec['pid'] for rec in records], record['code'])
        return self.record['code']


class ItemDB:
    def __init__(self, bot, item, data, code=None, time=None, record=None):
        self.bot = bot
        self.item_code = item.item_id
        self.data = data
        self.code = code
        self.time = time
        self.record = record

    @classmethod
    async def get_listing(cls, ctx, code: int):
        codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code FROM listed_items")
        if code in [cod['code'] for cod in codes]:
            listing = await ctx.cog.bot.db.fetchrow("SELECT * FROM listed_items WHERE code = $1", code)
            return cls(ctx.cog.bot, Item.get_item_id(ctx, listing['item_code']),
                       [listing['quantity'], listing['price'], listing['user_id'], listing['list_type']], code,
                       listing['time'], record=listing)
        else:
            raise BadArgument("The item is not in the database, have you provided correct uid?")

    async def add(self):
        query = "INSERT INTO listed_items (item_code, quantity, price, user_id, list_type, time) " \
                "VALUES ($1, $2, $3, $4, $5, $6) "
        record = await self.bot.db.execute(query, self.item_code, *self.data, int(datetime.now().timestamp()))
        return record['code']
