import discord
from discord.ext import commands
from discord.ext.commands import BadArgument

from cogs.utils.DataBase.Items import Item, convert_quantity, ItemDB, get_item, item_id
from cogs.utils.DataBase.guild import User, Filter
from cogs.utils.checks import is_staff, is_trusted
from cogs.utils.embeds import listings_embed, listing_embed


def to_lower(text):
    if text.lower() in ('sell', 'buy'):
        return text.lower()
    else:
        raise BadArgument


def listing_args(args):
    filters = [("i ", "item"), ("price", "p"), ("q", "quantity"), ("order", "o")]
    if not args.startswith("--"):
        return Filter(None)
    filtered = [(fil.split(' ')[0], fil.split(' ')[1:]) for fil in args.split('--')[1:]]
    key = [fil[0] for fil in filtered]
    items = None
    price = '0'
    price_type = '>'
    quantity = '1'
    quantity_type = '>='
    order_by = 'time'
    order_type = "DESC"
    for i in range(4):
        if set(filters[i]) & set(key):
            try:
                index = key.index(filters[i][0])
            except ValueError:
                index = key.index(filters[i][1])
            if i == 0:
                items = [item_id(get_item(el)) for el in filtered[index][1]]

            elif i == 1:
                if len(filtered[index]) == 1:
                    price = convert_quantity(filtered[index][0])
                    price_type = '='
                elif len(filtered[index]) == 2:
                    price_type = filtered[index][0]
                    price = str(convert_quantity(filtered[index][1]))
            elif i == 2:
                if len(filtered[index]) == 1:
                    quantity = convert_quantity(filtered[index][0])
                    quantity_type = '='
                elif len(filtered[index]) == 2:
                    quantity_type = filtered[index][0]
                    quantity = str(convert_quantity(filtered[index][1]))
            elif i == 3:
                order_by = filtered[index][0]
                if len(filtered[index]) == 2:
                    order_type = 'ASC'
            filtered.pop(index)
            key.pop(index)
    return Filter(items, price, price_type, quantity, quantity_type, order_by, order_type)


class Trade(commands.Cog):
    def __init__(self, bot):

        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def market(self, ctx, args):
        pass
        # show some help here?

    @market.command()
    async def sell(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        query_obj = ItemDB(self.bot, item, [quantity, price, ctx.author.id, "sell"])
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def buy(self, ctx, item: Item, quantity: convert_quantity, price: convert_quantity):
        query_obj = ItemDB(self.bot, item, [quantity, price, ctx.author.id, "buy"])
        uid = await query_obj.add()
        await ctx.send(f"your product has been listed id: {uid}")

    @market.command()
    async def remove(self, ctx, uid: int = None):
        if uid is None:
            raise BadArgument
        user = User(ctx.guild, self.bot, ctx.author)
        await user.remove_listing(uid)
        await ctx.send("removed listing")

    @market.command()
    async def search(self, ctx, list_type: to_lower = 'all', *, args: listing_args = Filter(None)):
        user = User(ctx.guild, self.bot, ctx.author)
        listings = await user.get_items(list_type, args)
        for listing in listings:
            trader = await self.bot.db.get_user(listing['user_id'])
            if not (set(trader['guilds']) & set(user.data['guilds'])):
                listings.remove(listing)
        await ctx.send(embed=listings_embed(listings, ctx.author))

    @commands.command()
    async def list(self, ctx, members: commands.Greedy[discord.Member] = None, *, args: listing_args = Filter(None)):
        user = User(ctx.guild, self.bot, ctx.author)
        if members is None:
            members = [user]
        else:
            members = [User(ctx.guild, self.bot, mem) for mem in members]

        listings = []
        args.user_id = 1
        for mem in members:
            listings.extend(await mem.get_listings('all', args))
        await ctx.send(listings)  # TODO: make into embed

    @commands.command()
    async def listing(self, ctx, uid: int):
        record = await ItemDB.get_listing(ctx, uid)
        author = User(ctx.guild, self.bot, ctx.author)
        await author.get_data()
        trader = await self.bot.db.get_user(record.data[2])  # user_id
        common_guilds = await self.get_common_guilds(common_guilds=set(trader['guilds']) & set(author.data['guilds']))
        await ctx.send(embed=listing_embed(record.record, trader, ctx.author, self.bot.get_user(record.data[2]),
                                           common_guilds))

    @commands.check_any(commands.check(is_trusted), commands.check(is_staff))
    @commands.command()
    async def complete(self, ctx, traders: commands.Greedy[discord.Member], item: Item, total: convert_quantity,
                       quantity: convert_quantity = 1):
        if len(traders) != 2:
            raise BadArgument
        traders = [User(ctx.guild, self.bot, trader) for trader in traders]
        for trader in traders:
            text = await trader.complete_trade(item, total, quantity)
            await ctx.send(f"{trader.user.mention} {text}")

    # async def cog_command_error(self, ctx, error):
    #     print(error)
    #     if isinstance(error, BadArgument):
    #         await ctx.send(error)
    #     # TODO: embedify errors

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
