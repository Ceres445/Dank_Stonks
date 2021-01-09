import json
from datetime import datetime

from discord.ext.commands.errors import BadArgument, CommandError

with open("cogs/utils//DataBase/json_files/items.json", "r") as f:
    items = json.load(f)
items = dict(items)


class Incorrect_Args(CommandError):
    def __init__(self):
        pass


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


def convert_quantity(text: str) -> int:
    allowed_symbols = "1234567890ek"
    try:
        new = eval(text)
        return new
    except SyntaxError:
        for i in text:
            if i not in allowed_symbols:
                raise BadArgument
        new = text.replace('k', "*1e3")
        try:
            new = eval(new)
            return new
        except SyntaxError:
            raise BadArgument


class ItemDB:
    def __init__(self, bot, item, data, code=None, time=None):
        self.bot = bot
        self.item_code = item.item_id
        self.data = data
        self.code = code
        self.time = time

    async def get_code(self):
        codes = await self.bot.db.fetch("SELECT DISTINCT code FROM listed_items ORDER BY code ASC ")
        codes = [code['code'] for code in codes]
        print(codes)
        if len(codes) == 0:
            return 1
        else:
            return codes[-1] + 1

    @classmethod
    async def get_listing(cls, ctx, code: int):
        codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code FROM listed_items ORDER BY code ASC")
        if code in [cod['code'] for cod in codes]:
            listing = await ctx.cog.bot.db.fetchrow("SELECT * FROM listed_items WHERE code = $1", code)
            return cls(ctx.cog.bot, Item.get_item_id(ctx, listing['item_code']),
                       [listing['quantity'], listing['price'], listing['user_id'], listing['list_type']], code,
                       listing['time'])
        else:
            raise BadArgument

    async def add(self):
        if self.code is None:
            self.code = await self.get_code()
            query = "INSERT INTO listed_items (code, item_code, quantity, price, user_id, list_type, time) VALUES " \
                    "($1, $2, $3, $4, $5, $6, $7) "
            print(self.data)
            await self.bot.db.execute(query,
                                      self.code, self.item_code, *self.data, int(datetime.now().timestamp()))
        return self.code
