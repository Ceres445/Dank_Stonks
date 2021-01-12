from datetime import datetime

from cogs.utils.DataBase.Items import items

import discord


def listings_embed(listings, author: discord.Member):
    desc = ""
    for listing in listings:
        desc += f"**ID: {listing['code']} \u2014 {list(items.keys())[listing['item_code']]}**  " \
                f"\u2014 [\u23e3 {int(listing['price']):,}]" \
                f"(https://www.youtube.com/watch?v=_BD140nCDps) \u2014 {int(listing['quantity'])} nos\n\n "

    embed = discord.Embed(title="Dank Market", timestamp=datetime.now(), colour=discord.Colour.green())
    embed.add_field(name="Shop Items", value=desc)
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)
    return embed


def listing_embed(listing, trader, author, trader_user, common):
    embed = discord.Embed(title="Listing Info", timestamp=datetime.now(), colour=discord.Colour.green())
    embed.add_field(name="Item shop",
                    value=f"uid: {listing['code']}\nitem: {list(items.keys())[listing['item_code']]}\n"
                          f"quantity: {listing['quantity']}\nprice: {listing['price']: ,}\n "
                          f"lister: {trader_user.mention}", inline=False)
    if common is not None:
        embed.add_field(name="User Info", value=f"name: {trader_user.name}\n common guilds: {' |'.join(common)}")
    else:
        embed.add_field(name="User Info", value=f"name: {trader_user.name}\n common guilds: None")
    embed.set_author(name=author.display_name, icon_url=author.avatar_url)

    return embed
