from typing import Dict

import discord
from discord.ext import commands
from discord.ext import menus

from cogs.utils.DataBase.guild import Guild


class channel_menu(menus.Menu):
    def __init__(self, ctx):
        super().__init__(timeout=30.0, delete_message_after=False)
        self.ctx = ctx
        self.data = {'promo': None, "trade": None}

    async def send_initial_message(self, ctx, channel):
        return await ctx.send(f"Setup channels, react to 1 to set promotional channel, react to 2 to set trade "
                              f"command channels")

    @menus.button('\N{SHOPPING TROLLEY}')
    async def promo(self, payload):
        print('added')
        await self.message.edit(content="mention the channel in which u want trade promotions to take place (make "
                                        "sure the bot has perms to send there)")

        def check(msg):
            if msg.author == self.ctx.author and msg.channel == self.ctx.channel:
                return True
            else:
                return False

        message = await self.bot.wait_for('message', check=check)
        if message.channel_mentions is None:
            await self.ctx.send("you haven't mentioned a channel")
            self.stop()
        elif len(message.channel_mentions) > 1:
            await self.ctx.send("only one promo channel is allowed, react again to send")
        else:
            self.data['promo'] = message.channel_mentions[0]
            await self.ctx.send("react to stop to confirm, react to any other to change")

    @menus.button('\N{TRIANGULAR FLAG ON POST}')
    async def trade(self, payload):
        await self.message.edit(
            content="mention the channel in which u want trade commands take place (make sure the bot has perms to "
                    "send there), mention all channels if u have multiple")

        def check(msg):
            if msg.author == self.ctx.author and msg.channel == self.ctx.channel:
                return True
            else:
                return False

        message = await self.bot.wait_for('message', check=check)
        if message.channel_mentions is None:
            await self.ctx.send("you haven't mentioned a channel")
            self.stop()
        else:
            self.data['trade'] = message.channel_mentions
            await self.ctx.send("react to stop to confirm, react to any other to change")

    @menus.button('\U000023f9')
    async def stop_button(self, payload):
        await self.ctx.send('confirmed')
        self.stop()

    async def starter(self, ctx) -> Dict[str, None or discord.TextChannel]:
        await self.start(ctx=ctx, wait=True)
        return self.data


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # TODO: try to load all guilds at start

    @commands.group(invoke_without_command=True)
    async def setup(self, ctx, args: str = None):
        guild = Guild(ctx.guild, self.bot)
        await guild.get_data()
        if args is None:
            await ctx.send("Welcome to setup manager")  # TODO: make into embed
            desc = f"guild id: {guild.guild.id}\nchannels: {guild.trade, guild.promo}\nstaff: {guild.staff}"
            await ctx.send(desc)

    @setup.command()
    async def staff(self, ctx, staff: discord.Role):
        guild = Guild(ctx.guild, self.bot)
        await guild.get_data()
        await guild.set_attribute('staff', [staff.id])
        await ctx.send(f"Successfully set staff role to {staff.name}")

    @setup.command()
    async def channel(self, ctx):
        guild = Guild(ctx.guild, self.bot)
        m = await channel_menu(ctx).starter(ctx)
        if m['promo'] is not None:
            await guild.set_attribute('promo', m['promo'].id)
            await ctx.send(f"Successfully set promo to <#   {m['promo'].mention}>")
        if m['trade'] is not None:

            await guild.set_attribute('trade', [a.id for a in m['trade']])
            trade_mention = [f"<#{i}>" for i in m['trade']]
            await ctx.send(f"Successfully set trade to {trade_mention}")

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        guild = Guild(ctx.guild, self.bot)
        await guild.get_data()
        prefixes = guild.prefix
        desc = ""
        print(prefixes)
        for index, prefix in enumerate(prefixes):
            desc += f"{index+1}. {prefix}\n"
        await ctx.send(f"```{desc}```")

    @prefix.command()
    async def add(self, ctx, new: str):
        guild = Guild(ctx.guild, self.bot)
        await guild.get_data()
        if new in guild.prefix:
            await ctx.send("that's already a prefix :/")
            return
        else:
            await guild.set_attribute("prefix", guild.prefix + [new])
            await ctx.send(f"added {new} to prefix")

    @prefix.command(aliases=['rm'])
    async def remove(self, ctx, rm: str):
        guild = Guild(ctx.guild, self.bot)
        await guild.get_data()
        if rm in guild.prefix:
            await guild.set_attribute("prefix", guild.prefix.remove(rm))
            await ctx.send(f"{rm} removed")
        else:
            await ctx.send("I do not have this prefix registered.")

    @prefix.command(aliases=['make'])
    async def set(self, ctx, prefix: str):
        guild = Guild(ctx.guild, self.bot)
        await guild.set_attribute("prefix", [prefix])
        await ctx.send(f"Prefix for this server is now {prefix}")

    def cog_check(self, ctx):
        if discord.Permissions(manage_guild=True) <= ctx.author.guild_permissions:
            return True
        else:
            return False


def setup(bot):
    bot.add_cog(Setup(bot))
