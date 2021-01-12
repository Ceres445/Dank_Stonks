from datetime import datetime

from cogs.utils.DataBase.Items import items

import discord


def listings_embed(listings, author: discord.Member):
    desc = ""
    for listing in listings:
        desc += f"**ID: {listing['code']} -- {items[listing['item_code']]}** -- \u2014 [\u2303 {int(listing['price']):,}]" \
                f"(https://www.youtube.com/watch?v=_BD140nCDps) - {int(listing['quantity'])} nos\n\n "

    embed = discord.Embed(title="Dank Market", timestamp=datetime.now(), colour=discord.Colour.green())
    embed.add_field(name="Shop Items", value=desc)
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    return embed


def listing_embed(listing, trader, user):
    common_guilds = set(trader['guilds']) & set(user.data['guilds'])
    embed = discord.Embed(title="Listing Info", timestamp=datetime.now(), colour=discord.Colour.green())
    embed.add_field(name="Item shop")
    # TODO: complete this
    return embed
