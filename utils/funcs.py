from utils import database as db, constants as const, pagination
import math
import json
import disnake

def get_exact_level(user_id:int) -> float:
    """Gets exact flaot value of user's level and how far he is from
       the next level. 

    Args:
        user_id (int): Discord user ID

    Returns:
        float: Level
    """
    current_xp = db.get_xp(user_id)
    level = math.log(current_xp / const.STARTING_VALUE, const.MULTIPLIER)
    return level


def get_next_level_xp(user_id:int) -> int:
    level = db.get_level(user_id)
    next_level_xp = const.STARTING_VALUE * (const.MULTIPLIER** (level+1))
    next_level_xp = int(round(next_level_xp, -1))
    return next_level_xp
     
    

def get_shop_dict():
    with open("utils/shop.json") as f:
        shop_data = json.load(f)
        
    return shop_data

def get_item_buy_price(item_name:str):
    shop_data = get_shop_dict()
    items = shop_data["items"]
    price = items[item_name]["buy_price"]
    return price

def get_item_sell_price(item_name:str):
    shop_data = get_shop_dict()
    items = shop_data["items"]
    price = items[item_name]["sell_price"]
    return price


def gen_shop_embed():
    shop_data = get_shop_dict()
    embeds = []
    leaderboard_string = ""
    items_dict = shop_data["items"]
    counter = 1
    divided_item_list = list(pagination.divide_list(list(items_dict),5))
    for item_list in divided_item_list:
        embed = disnake.Embed(title=f"Shop", description=leaderboard_string, color = const.EMBED_COLOUR)
        embeds.append(embed)
        for item_name in item_list:
            price = items_dict[item_name]["buy_price"]
            description = items_dict[item_name]["description"]
            item_name = item_name.capitalize()
            embed.add_field(name = f"{counter})`{item_name}`", value = f"Price: `{price}`\nDescription: `{description}`", inline=False)
            counter += 1
        
    return embeds


def gen_ordinal_prefix(number:int):
    if number == 1:
        return "st"
    elif number == 2:
        return "nd"
    elif number == 3:
        return "rd"
    else:
        return "th"
    
    
    