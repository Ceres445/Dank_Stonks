import math

import discord
from discord.ext.commands.errors import BadArgument

from cogs.utils.DataBase.Items import Item
from main import StonksBot


class Guild:
    def __init__(self, guild: discord.Guild, bot: StonksBot):
        self.bot = bot
        self.guild = guild
        self.prefix, self.staff, self.verified = None, None, None

    async def get_data(self):
        record = await self.bot.db.fetchrow("SELECT * FROM guild_info WHERE guild=$1", self.guild.id)
        self.prefix, self.staff,  \
        self.verified = record['prefix'], record['staff'], record[
            'verified']

    async def set_attribute(self, attribute, value):
        await self.bot.db.execute(f"UPDATE guild_info set {attribute} = $1" , value)


class Filter:
    def __init__(self, items, price='0', price_type='>=', quantity='1', quantity_type='>=', order_by='time',
                 order_type='DESC', trade=False, user_id=None):
        self.items = items
        self.price = price
        self.price_type = price_type
        self.quantity = quantity
        self.quantity_type = quantity_type
        self.order_by = order_by
        self.order_type = order_type
        self.user_id = user_id
        self.trade = trade

    def query_gen(self):
        if self.items is None:
            items = '(SELECT item_code FROM listed_items)'
        else:
            items = tuple(self.items) if len(self.items) > 1 else f'({self.items[0]})'
        if self.trade:
            if self.user_id is None:
                return f"SELECT * FROM traded_items WHERE user_item in {items} and list_type = $1 ORDER BY time DESC"
            else:
                return f"SELECT * FROM traded_items WHERE user_item in {items} and" \
                       f" list_type = $1 and user_id = $2 ORDER BY time DESC"
        if self.user_id is None:
            return f"SELECT * FROM listed_items WHERE item_code in {items}" \
                   f" and price {self.price_type} {self.price} and quantity {self.quantity_type} {self.quantity} " \
                   f" and list_type = $1 ORDER BY {self.order_by} {self.order_type}"
        else:
            return f"SELECT * FROM listed_items WHERE item_code in {items}" \
                   f" and price {self.price_type} {self.price} and quantity {self.quantity_type} {self.quantity} " \
                   f" and list_type = $1 and user_id = $2 ORDER BY {self.order_by} {self.order_type}"


def calc_trust(new_worth, new_trade, trust):
    if trust == 10:
        return 10
    x = int(math.log10(new_worth / 1e5))
    if x >= 10:
        return 9
    y = int(math.log10(new_trade))
    if y >= 10:
        return 9
    return max(x, y)


class User:
    def __init__(self, guild, bot, user: discord.Member):
        self.bot = bot
        self.guild = guild
        self.user = user
        self.data = None
        self.listings = None

    async def complete_trade(self, item: Item, amount: int, quantity: int = 1):
        if self.data is None:
            await self.get_data()
        records = [record['item_code'] for record in self.listings]
        if item.item_id not in records:
            update = "No item in listing"
        else:
            record = self.listings[records.index(item.item_id)]
            query = "UPDATE listed_items set quantity = $1 WHERE user_id = $2"
            await self.bot.db.execute(query, record['quantity'] - quantity, self.user.id)
            update = f"New quantity {record['quantity'] - quantity} for {item}"
        query = "UPDATE user_data set trades = $1, worth = $2, trust = $3 WHERE user_id = $4"
        trust = calc_trust(self.data['worth'] + amount, self.data['trades'] + 1, self.data['trust'])
        await self.bot.db.execute(query, self.data['trust'], self.data['worth'], trust, self.user.id)
        await self.get_data()
        return update

    async def set_attribute(self, attribute, value):
        await self.bot.db.execute(f"UPDATE user_data set {attribute} = $1", value)

    async def create_user(self):
        query = "INSERT INTO user_data (user_id, guilds, worth, trades, trust) VALUES ($1, $2, 0, 0, 0)"
        await self.bot.db.execute(query, self.user.id, [self.guild.id])

    async def get_data(self):
        query = "SELECT * FROM user_data WHERE user_id = $1"
        user = await self.bot.db.fetchrow(query, self.user.id)
        if user is None:
            await self.create_user()
            user = await self.bot.db.fetchrow(query, self.user.id)
        if self.guild.id not in user['guilds']:
            query = "UPDATE user_data set guilds = $1 WHERE user_id= $2"
            await self.bot.db.execute(query, user['guilds'] + [self.guild.id], self.user.id)
        self.data = user
        await self.get_listings()

    async def get_listings(self, list_type: str = 'all', fil: Filter = Filter(None, user_id=1)):
        if list_type != "all":
            query = fil.query_gen()
            listings = await self.bot.db.fetch(query, list_type, self.user.id)
        else:
            query = fil.query_gen()
            listings = await self.bot.db.fetch(query, "sell", self.user.id)
            listings += await self.bot.db.fetch(query, "buy", self.user.id)
        self.listings = listings
        return listings

    async def remove_listing(self, uid: int):
        listings = await self.get_listings('all', Filter(None, user_id=1))
        if int(uid) in [i['code'] for i in listings]:
            query = "DELETE FROM listed_items WHERE code=$1"
            await self.bot.db.execute(query, uid)
            return

        else:
            listings = await self.get_listings('all', Filter(None, user_id=1, trade=True))
            if int(uid) in [i['code'] for i in listings]:
                query = "DELETE FROM traded_items WHERE code=$1"
                await self.bot.db.execute(query, uid)
                return
            else:
                raise BadArgument

    async def get_items(self, list_type, fil: Filter = Filter(None)):
        if self.data is None:
            await self.get_data()
        query = fil.query_gen()
        if list_type != 'all':
            listings = await self.bot.db.fetch(query, list_type)
            return listings
        else:
            listings = await self.bot.db.fetch(query, "sell")
            listings += await self.bot.db.fetch(query, "buy")
            return listings
