from discord.ext import commands
import discord


class Guild:
    def __init__(self, guild, bot):
        self.bot = bot
        self.guild = guild
        self.prefix, self.staff, self.trade, self.promo = None, None, None, None

    async def get_data(self):
        record = await self.bot.db.fetchrow("SELECT * FROM prefix WHERE guild=$1", self.guild.id)
        self.prefix, self.staff, self.trade, self.promo = record['prefix'], record['staff'], record['trade'], record['promo']

    async def set_attribute(self, attribute, value):
        await self.bot.db.execute(f"UPDATE prefix set {attribute} = $1", value)


class User:
    def __init__(self, guild, bot, user: discord.Member):
        self.bot = bot
        self.guild = guild
        self.user = user

    async def create_user(self):
        query = "INSERT INTO user_data (user_id, guilds, worth, trades, trust) VALUES ($1, $2, 0, 0, 0)"
        await self.bot.db.execute(query, self.user.id, [self.guild.id])

    async def get_data(self):
        query = "SELECT * FROM user_data WHERE user_id = $1"
        user = self.bot.db.fetchrow(query, self.user.id)
        if user is None:
            await self.create_user()
        if self.guild.id not in user['guilds']:
            query = "UPDATE user_data set guilds = $1 WHERE user_id= $2"
            await self.bot.db.execute(query, user['guilds'] + [self.guild.id], self.user.id)

    async def get_listings(self, list_type: str):
        if list_type != "all":
            query = "SELECT * FROM listed_items where list_type = $1 and user_id = $2"
            listings = await self.bot.db.fetch(query, list_type, self.user.id)
        else:
            query = "SELECT * FROM listed_items where $1 = user_id "
            listings = await self.bot.db.fetch(query, self.user.id)
        return listings
