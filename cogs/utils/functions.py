from discord.ext import commands
from discord.ext.commands import BadArgument, CommandError

from cogs.utils.DataBase.Items import Item
from cogs.utils.DataBase.guild import Filter
from cogs.utils.errors import BadListType, BadQueryType


def convert_quantity(text: str) -> int:
    allowed_symbols = "1234567890ek.+-*/"
    if set(text) > set(allowed_symbols):
        raise BadArgument("unsupported quantity")
    try:

        new = eval(text)
        return new
    except SyntaxError:
        for i in text:
            if i not in allowed_symbols:
                raise BadArgument("unsupported quantity")
        new = text.replace('k', "*1e3")
        try:
            new = eval(new)
            return new
        except SyntaxError:
            raise BadArgument("unsupported quantity")


def to_lower(text):
    if text.lower() in ('sell', 'buy', 'all'):
        return text.lower()
    else:
        raise BadListType


def calc_quantity(args):
    relation = ''
    value = None
    for i, arg in enumerate(args):
        if arg in ('>', '=', '<'):
            relation += arg
        else:
            value = convert_quantity(arg[i:])
            break
    if relation in ('>', '<', '=', '<=', '>=', '=') and value is not None:
        return relation, value
    else:
        raise BadQueryType


def listing_args(items, query):
    if query is None:
        return Filter(items)
    kwargs = {}
    queries = query.split(' ')  # sample: price>=1e6 quantity<20
    for q in queries:
        if q.startswith("price") or q.startswith("p"):
            if len(q.split('price')) == 2:
                args = q.split('price')[1]
            else:
                args = q.split('p')[1]
            kwargs['price'], kwargs['price_type'] = calc_quantity(args)
        elif q.startswith("quantity") or q.startswith("q"):
            if len(q.split('price')) == 2:
                args = q.split('price')[1]
            else:
                args = q.split('q')[1]
            kwargs['quantity'], kwargs['quantity_type'] = calc_quantity(args)
    # items = None
    # price = '0'
    # price_type = '>'
    # quantity = '1'
    # quantity_type = '>='
    # order_by = 'time'
    # order_type = "DESC"
    # trade = False
    return Filter(items, **kwargs)


class Incorrect_Args(CommandError):
    def __init__(self):
        pass


class StockConverter(commands.Converter):

    def __getitem__(self, item):
        pass

    async def convert(self, ctx, args) -> list:
        if args.find('=') == -1:
            item = await Item.convert(ctx, args)
            return [item, 1]
        else:
            item, quantity = args.split('=')
            quantity = convert_quantity(quantity)
            item = await Item.convert(ctx, item)
            return [item, quantity]


class CompleteConvertor(commands.Converter):
    def __getitem__(self, item):
        pass

    async def convert(self, ctx, argument):
        args = argument.split(', ')
        if len(args) == 1:
            typer = 'money'
            trader = await StockConverter().convert(ctx, args[0])
            return typer, trader
        else:
            trader1 = await TradeConvertor().convert(ctx, args[0])
            trader2 = await TradeConvertor().convert(ctx, args[1])
            return 'item', trader1, trader2


class TradeConvertor(commands.Converter):
    async def convert(self, ctx, args):
        args = args.split(' ')
        return_items = {}
        for arg in args:
            if arg.find('=') != -1:
                item, quantity = arg.split('=')
                quantity = convert_quantity(quantity)
                item = await Item.convert(ctx, item)
                return_items[item.item_id] = quantity
            else:
                item = await Item.convert(ctx, args.strip())
                return_items[item.item_id] = 1
        return return_items
