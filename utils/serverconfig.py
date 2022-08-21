from sqlitedict import SqliteDict


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
        
    