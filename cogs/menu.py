import asyncio

import discord
from discord.ext import menus
from cogs.utils.DataBase.Items import items, item_convertor


class MarketMenu(menus.MenuPages):
    def __init__(self, data, ctx, desc):
        super().__init__(source=MarketSource([(1, data), (2, ""), (3, "")]),
                         clear_reactions_after=True)
        self.data = data[:5]
        self.current_page = 0
        self.desc = desc
        self.ctx = ctx
        self.max_pages = 5
        self.sort = 'time'

    @menus.button('\U0001f503', position=menus.Last(1.2))
    async def sort_by(self, _):
        """Lets you sort the results (go to page 1) """
        sort = ['time', 'quantity', 'price']
        sort_id = sort.index(self.sort)
        if sort_id == 2:
            self.sort = 'time'
        else:
            self.sort = sort[sort_id + 1]
        data = sorted(self.data, key=lambda x: x[self.sort])
        self.data = data

    @menus.button('\N{INFORMATION SOURCE}\ufe0f', position=menus.Last(3))
    async def show_help(self, _):
        """shows this message"""
        embed = discord.Embed(title='Paginator help', description='Hello! Welcome to the help page.')
        messages = []
        for (emoji, button) in self.buttons.items():
            messages.append(f'{emoji}: {button.action.__doc__}')

        embed.add_field(name='What are these reactions for?', value='\n'.join(messages), inline=False)
        embed.set_footer(text=f'We were on page {self.current_page + 1} before this message.')
        await self.message.edit(content=None, embed=embed)

        async def go_back_to_current_page():
            await asyncio.sleep(30.0)
            await self.show_page(self.current_page)

        self.bot.loop.create_task(go_back_to_current_page())

    @menus.button('\N{INPUT SYMBOL FOR NUMBERS}', position=menus.Last(1.5))
    async def numbered_page(self, payload):
        """lets you type a page number to go to"""
        channel = self.message.channel
        author_id = payload.user_id
        to_delete = [await channel.send('What page do you want to go to?')]

        def message_check(m):
            return m.author.id == author_id and \
                   channel == m.channel and \
                   m.content.isdigit()

        try:
            msg = await self.bot.wait_for('message', check=message_check, timeout=30.0)
        except asyncio.TimeoutError:
            to_delete.append(await channel.send('Took too long.'))
            await asyncio.sleep(5)
        else:
            page = int(msg.content)
            to_delete.append(msg)
            await self.show_checked_page(page - 1)

        await channel.delete_messages(to_delete)


class MarketSource(menus.GroupByPageSource):
    def __init__(self, data):
        super().__init__(data, key=lambda x: x[0], per_page=1)

    async def format_page(self, menu: MarketMenu, entry):
        if menu.current_page == 0:
            entries = menu.data
            desc = ""
            for listing in entries:
                desc += f"**ID: {listing['code']} \u2014 " \
                        f"{item_convertor[list(items.keys())[listing['item_code']]]}**  " \
                        f"\u2014 [\u23e3 {int(listing['price']):,}]" \
                        f"(https://www.youtube.com/watch?v=_BD140nCDps) \u2014 {int(listing['quantity'])} nos\n\n "

            embed = discord.Embed(title="Dank Market", colour=discord.Colour.green(),
                                  description=menu.desc)
            embed.add_field(name="Listed items", value=desc)
            embed.set_author(name=menu.ctx.author.display_name, icon_url=menu.ctx.author.avatar_url)
            embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()} | Sorting by {menu.sort}")
            return embed
        if menu.current_page == 1:
            _help = await menu.ctx.cog.bot.help_command.get_command_help(menu.ctx.command, menu.ctx)
            _help.timestamp = discord.Embed.Empty
            _help.set_author(name=menu.ctx.author.display_name, icon_url=menu.ctx.author.avatar_url)
            _help.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
            return _help
        if menu.current_page == 2:
            embed = discord.Embed(title='Using the bot', colour=discord.Colour.blurple())
            embed.title = 'Using the market command'
            entries = (
                ('<argument>', 'This means the argument is __**required**__.'),
                ('[argument]', 'This means the argument is __**optional**__.'),
                ('[A|B]', 'This means that it can be __**either A or B**__.'),
                ('[argument...]', 'This means you can have multiple arguments.\n'
                                  'Now that you know the basics, it should be noted that...\n'
                                  '__**You do not type in the brackets!**__')
            )
            embed.add_field(name='How do I use this command?', value='Reading the bot signature is pretty simple.')

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)
            embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
            return embed


class ListItem(menus.MenuPages):
    def __init__(self, data, ctx, desc):
        super().__init__(source=MySource(data), clear_reactions_after=True)
        self.data = data
        self.sort = "time"
        self.ctx = ctx
        self.desc = desc

    @menus.button('\U0001f503', position=menus.Last(1.2))
    async def sort_by(self, _):
        """Lets you sort the results    """
        sort = ['time', 'quantity', 'price']
        sort_id = sort.index(self.sort)
        if sort_id == 2:
            self.sort = 'time'
        else:
            self.sort = sort[sort_id + 1]
        data = sorted(self.data, key=lambda x: x[self.sort])
        await self.change_source(source=MySource(data))


class MySource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=5)

    async def format_page(self, menu: ListItem, entries):
        entries = await self.get_page(menu.current_page)
        desc = ""
        for listing in entries:
            desc += f"**ID: {listing['code']} \u2014 {item_convertor[list(items.keys())[listing['item_code']]]}**  " \
                    f"\u2014 [\u23e3 {int(listing['price']):,}]" \
                    f"(https://www.youtube.com/watch?v=_BD140nCDps) \u2014 {int(listing['quantity'])} nos\n\n "

        embed = discord.Embed(title="Dank Market", colour=discord.Colour.green(),
                              description=menu.desc)
        embed.add_field(name="Listed items", value=desc)
        embed.set_author(name=menu.ctx.author.display_name, icon_url=menu.ctx.author.avatar_url)
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()} | Sorting by {menu.sort}")
        return embed
