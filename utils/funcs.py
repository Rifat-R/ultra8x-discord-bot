from utils import database as db, constants as const, pagination, serverconfig as conf
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


#Job funcs
def get_job_list_dict():
    with open("utils/jobs.json") as f:
        return json.load(f)
    
    
def get_job_info_dict(job_name):
    job_list_dict = get_job_list_dict()
    job_dict = job_list_dict["job_list"]
    job_info_dict = job_dict[job_name]
    return job_info_dict
    


def gen_job_list_embed():
    job_list_data = get_job_list_dict()
    embeds = []
    job_description_string = """To apply for a job use `/job apply <job-id>`.
                                You can only apply for jobs with 🔓
                                Leave a job by using `/job leave.`"""
    jobs_dict = job_list_data["job_list"]
    counter = 1
    divided_job_list = list(pagination.divide_list(list(jobs_dict),5))
    for job_list in divided_job_list:
        embed = disnake.Embed(title=f"Job list", description=job_description_string, color = const.EMBED_COLOUR)
        embeds.append(embed)
        for job_name in job_list:
            per_hour_wage = jobs_dict[job_name]["per_hour_wage"]
            hours_per_day = jobs_dict[job_name]["hours_per_day"]
            level_needed = jobs_dict[job_name]["level_needed"]
            job_name = job_name.capitalize()
            embed.add_field(name = f"{counter}) __**{job_name}**__",
                            value = f"> £{per_hour_wage} / hour \n> Maximum {hours_per_day} hours / day.\n> Required level to apply: `{level_needed}`", inline=False)
            counter += 1
        
    return embeds

def get_job_level_needed(job_name:str):
    return get_job_info_dict(job_name)["level_needed"]

def get_job_hours_per_day(job_name:str):
    return get_job_info_dict(job_name)["hours_per_day"]

def get_job_per_hour_wage(job_name:str):
    return get_job_info_dict(job_name)["per_hour_wage"]

def get_job_daily_wage(job_name:str):
    hours = get_job_hours_per_day(job_name)
    hourly_wage = get_job_per_hour_wage(job_name)
    return hours * hourly_wage

def get_job_cooldown_seconds(job_name:str):
    return get_job_hours_per_day(job_name) * 3600



#Shop funcs
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


def convert_to_ordinal(number:int):
    if number == 1:
        return f"{number}st"
    elif number == 2:
        return f"{number}nd"
    elif number == 3:
        return f"{number}rd"
    else:
        return f"{number}th"
    
    
    