from datetime import datetime

from discord.ext.commands import BadArgument


class Trades:
    def __init__(self, bot, data, verified: bool = False, record=None):
        # TODO: rewrite table structure for traded items/money
        self.bot = bot
        self.data = data
        self.verified = verified
        self.record = record

    async def add(self):
        query = "INSERT INTO trades (user_1, user_2, type, info, verified, time) VALUES " \
                "($1, $2, $3, $4, $5, $6)"
        self.record = await self.bot.db.execute(query, self.data, self.verified, int(datetime.now().timestamp()))

    @classmethod
    async def get_from(cls, ctx, code):
        codes = await ctx.cog.bot.db.fetch("SELECT DISTINCT code FROM trades")
        if code in [code['code'] for code in codes]:
            record = await ctx.cog.bot.db.fetchrow("SELECT * FROM trades WHERE code=$1", code)
            return cls(ctx.cog.bot, data=None, verified=record['verified'], record=record)
        else:
            raise BadArgument

    async def verify(self, verify: bool = True):
        query = "UPDATE trades set verified = $1 WHERE code = $2"
        await self.bot.db.execute(query, verify, self.record['code'])
