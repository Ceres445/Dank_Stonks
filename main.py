from discord.ext import commands
import discord
from aiohttp import ClientSession

from config import load_vars
import asyncio
from cogs.utils.DataBase.database import Database

initial = [
    'cogs.setup',
    'cogs.trade',
    'cogs.misc',
    'cogs.help'
]


async def get_prefix(bot, message):
    prefix = await bot.db.get_prefix(message.guild)
    prefix.extend([f'<@!{bot.user.id}> ', f'<@{bot.user.id}> '])
    return prefix


class StonksBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents(messages=True, guilds=True, reactions=True)
        super().__init__(command_prefix=get_prefix, case_insensitive=True,
                         allowed_mentions=discord.AllowedMentions(everyone=False, roles=True, users=True),
                         intents=intents)
        self.session = ClientSession(loop=self.loop)
        self.clean_text = commands.clean_content(escape_markdown=True, fix_channel_mentions=True)
        self.db = None
        for cog in initial:
            self.load_extension(cog)
            print("loaded", cog)

    async def on_connect(self):
        try:
            self.db = await Database.create_pool(bot=self, uri=postgres, loop=self.loop)
            print("connected to DB")
        except OSError:
            print("postgres server is not running")

    async def on_message(self, message):
        ctx = await self.get_context(message)
        if message.author.bot:
            return
        elif message.content == f'<@!{self.user.id}>' or message.content == f'<@{self.user.id}>':
            prefix = await self.get_prefix(message)
            await ctx.send(f"use the prefix` {prefix[0]}`")
        await self.process_commands(message)

    async def on_ready(self):
        print(f'Successfully logged in as {self.user}\nSharded to {len(self.guilds)} guilds')
        await self.change_presence(status=discord.Status.online, activity=discord.Game(name='use the prefix "+"'))

    @classmethod
    async def setup(cls):
        bot = cls()
        try:

            await bot.start(token)
        except KeyboardInterrupt:
            await bot.close()


if __name__ == '__main__':
    postgres, token = load_vars()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(StonksBot.setup())
