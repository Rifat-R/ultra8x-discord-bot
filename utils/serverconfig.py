from sqlitedict import SqliteDict
from utils import database as db


SERVER_CONF_NAME = "serverconf.sqlite"




def add_filter_word(word:str):
    db = SqliteDict(SERVER_CONF_NAME)
    filter_word_list = db.get("filter_word_list")
    if db.get("filter_word_list") is None:
        filter_word_list = []
        
    filter_word_list.append(word)
    db["filter_word_list"] = filter_word_list
    db.commit()
    db.close()
    
def remove_filter_word(word:str):
    db = SqliteDict(SERVER_CONF_NAME)
    filter_word_list = db.get("filter_word_list")
    if db.get("filter_word_list") is None:
        raise ValueError(f"Cannot remove `{word}` from filter word list as list does not exist")
        
    filter_word_list.remove(word)
    db["filter_word_list"] = filter_word_list
    db.commit()
    db.close()
    
    
def get_filter_word_list():
    db = SqliteDict(SERVER_CONF_NAME)
    filter_word_list = db.get("filter_word_list")
    if filter_word_list is None:
        filter_word_list = []
    return filter_word_list
        
    
def set_welcome_message(guild_id:str, channel_id:int , message:str):
    guild_id = str(guild_id)
    db = SqliteDict(SERVER_CONF_NAME)
    welcome_message_dict = db.get("welcome_message")
    if welcome_message_dict is None:
        db["welcome_message"] = {guild_id : {"message": message, "channel_id" : channel_id}}
        db.commit()
        db.close()
        return
    guild_id_dict = welcome_message_dict.get(guild_id)
    guild_id_dict["message"] = message
    guild_id_dict["channel_id"] = channel_id
    welcome_message_dict[guild_id] = guild_id_dict
    db["welcome_message"] = welcome_message_dict
    print(db["welcome_message"])
    db.commit()
    db.close()
    
    
def get_welcome_message(guild_id:str):
    guild_id = str(guild_id)
    db = SqliteDict(SERVER_CONF_NAME)
    welcome_message_dict = db.get("welcome_message")
    if welcome_message_dict is None:
        return None, None
    guild_id_dict = welcome_message_dict.get(guild_id)
    if guild_id_dict is None:
        return None, None
    message = guild_id_dict.get("message")
    channel_id = guild_id_dict.get("channel_id")
    if message is None or channel_id is None:
        return None, None
    return message, channel_id


#Need to make make sure how I want to setup xp_rate
# #Not multi-server
# def get_xp_rate():
#     db = SqliteDict(SERVER_CONF_NAME)
#     xp_rate = db.get("xp_rate")
#     return xp_rate

# def set_xp_rate(xp_rate:int):
#     db = SqliteDict(SERVER_CONF_NAME)
#     db["xp_rate"] = xp_rate
#     db.commit()
#     db.close()
#     print(f"Set XP rate to: {xp_rate}")        
    
    