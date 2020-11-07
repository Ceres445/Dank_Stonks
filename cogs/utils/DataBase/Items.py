import json
from discord.ext.commands.errors import BadArgument

with open("cogs/utils//DataBase/json/items.json", "r") as f:
    items = json.load(f)
items = dict(items)


def get_item(name: str) -> dict or None:
    if name in items:
        return name
    for key, i in items.items():
        if name in i:
            return key
    return None


def item_id(item):
    return list(items.keys()).index(item)


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
            raise BadArgument  # TODO: raise custom error
        return cls(ctx.cog.bot, item_data, items[item_data])

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
    def __init__(self, bot, list_type: str, item: Item, quantity: int, price: int, user: int):
        self.bot = bot
        self.code = None
        self.item = item
        self.list_type = list_type
        self.quantity = quantity
        self.price = price
        self.user = user

    async def get_code(self):
        codes = await self.bot.db.fetch("SELECT DISTINCT code FROM listed_items")
        codes = [code['code'] for code in codes]
        if len(codes) == 0:
            return 1
        else:
            return codes[-1] + 1

    async def add(self):
        self.code = await self.get_code()
        query = "INSERT INTO listed_items (code, item_code, quantity, price, user_id, list_type) VALUES ($1, $2, $3, " \
                "$4, $5, $6) "
        await self.bot.db.execute(query,
                                  self.code, self.item.item_id, self.quantity, self.price, self.user, self.list_type)
        return self.code
