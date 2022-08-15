import sqlite3
from datetime import datetime
from utils import funcs

class database:
    def __init__(self, database):
        self.database = database
        
    def start_connection(self):
        """
        Starts connection to database and creating cursor.
        """
        self.conn = sqlite3.connect(self.database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) #detect_types so time type is datetime
        self.c = self.conn.cursor() 

    def close(self):
        """Closes connection to database"""
        self.conn.close() 
        
    def commit(self):
        """Commits transaction in database"""
        self.conn.commit() 

PLAYER_DATA = "player_data.db"

def update_wallet(user_id:int,money:int):
    """Adds money to a user's wallet in the user_data table

    Args:
        user_id (int): The user's discord ID.
        money (int): The amount of money transferred to the user's wallet
    """
    db = database(PLAYER_DATA) 
    db.start_connection() 
    db.c.execute(f"UPDATE user_data SET wallet = wallet + {money} WHERE user_id = {user_id}") 
    db.conn.commit() 
    db.conn.close() 

def deduct_wallet(user_id:int,money:int):
    """Deducts money from a user's wallet in the user_data table.

    Args:
        user_id (int): The user's discord ID.
        money (int): The amount of money that is going to be deducted from the user's wallet.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET wallet = wallet - {money} WHERE user_id = {user_id}")
    db.conn.commit()
    db.conn.close()

def update_bank(user_id:int,money:int):
    """Adds money to the user's bank in the user_data table.

    Args:
        user_id (int): The discord user's ID.
        money (int): The amount of money added to the user's bank.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET bank = bank + {money} WHERE user_id = {user_id}")
    db.conn.commit()
    db.conn.close()

def deduct_bank(user_id:int,money:int):
    """Deducts money from the user's bank in the user_data table.

    Args:
        user_id (int): The discord user's ID.
        money (int): The amount of money that is going to be deducted from the user's bank account.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET bank = bank - {money} WHERE user_id = {user_id}")
    db.conn.commit()
    db.conn.close()

def create(user_id:int, author:str):
    """Creates a blank account for the user in the user_data table.
    This makes sure the other functions will be able to work or else
    they will not work due to the user not existing in the database.

    Args:
        user_id (int): The discord user's ID.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO user_data (user_id, author) VALUES (?, ?)",(user_id, author))
    db.conn.commit()
    db.conn.close()
    print(f"Created new account for user {user_id}")
    
def update_author(user_id:int, author:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET author = ? WHERE user_id = ?", (author, user_id))
    db.conn.commit()
    db.conn.close()
    
def get_author(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.start_connection()
    db.c.execute(f"SELECT author FROM user_data WHERE user_id = {user_id}")
    return db.c.fetchone()[0]


def wallet(user_id:int) -> int:
    """Returns the wallet content.

    Args:
        user_id (int): The discord user's ID.

    Returns:
        int: The wallet content of the user.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT wallet FROM user_data WHERE user_id = {user_id}")
    return db.c.fetchone()[0]

def bank(user_id:int) -> int:
    """Returns the bank content.

    Args:
        user_id (int): The discord user's ID.

    Returns:
        int: The bank content of the user.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT bank FROM user_data WHERE user_id = {user_id}")
    return db.c.fetchone()[0]

def get_rich_leaderboard():
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT author, (wallet + bank) as networth FROM user_data ORDER BY networth DESC LIMIT 30")
    rich_list = db.c.fetchall()
    return rich_list


def get_item(user_id:int, item_name:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM user_inventory WHERE user_id = ? AND item = ?", (user_id, item_name))
    return db.c.fetchall()

#Might need it for future purposes (the execute line)

# def get_user_inventory(user_id:int):
#     db = database(PLAYER_DATA)
#     db.start_connection()
#     db.c.execute(f"SELECT user_data.author, user_inventory.item FROM user_inventory INNER JOIN user_data ON user_inventory.user_id = user_data.user_id WHERE user_data.user_id = ?", (user_id,))
#     player_inventory = db.c.fetchall()
#     return player_inventory

def get_user_inventory(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM user_inventory WHERE user_id = ?", (user_id,))
    return db.c.fetchall()

def buy_item(user_id:int, item_name):
    item_name = item_name.lower()
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO user_inventory VALUES (?, ?)",(user_id, item_name))
    db.conn.commit()
    db.conn.close()
    price = funcs.get_item_buy_price(item_name)
    deduct_wallet(user_id, price)
    
def sell_item(user_id:int, item_name):
    item_name = item_name.lower()
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM user_inventory WHERE user_id = ? AND item = ?",(user_id, item_name))
    db.conn.commit()
    db.conn.close()
    price = funcs.get_item_sell_price(item_name)
    update_wallet(user_id, price)
    

def check_user(user_id:int) -> bool:
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM user_data WHERE user_id = {user_id}")
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True

#Logging system
def infraction_log(user_id:int, infraction_type:str, reason_message:str, issued_by_id:int):
    time = datetime.now() 
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO infraction_log VALUES (?,?,?,?,?)",(user_id, time, reason_message, issued_by_id, infraction_type,))
    db.commit()
    db.close()
    
def ban_log(user_id:int, reason_message:str, issued_by_id:int):
    infraction_log(user_id, "Ban", reason_message, issued_by_id)
    
def mute_log(user_id:int, reason_message:str, issued_by_id:int):
    infraction_log(user_id, "Mute", reason_message, issued_by_id)
    
def kick_log(user_id:int, reason_message:str, issued_by_id:int):
    infraction_log(user_id, "Kick", reason_message, issued_by_id)
    
def warn_log(user_id:int, reason_message:str, issued_by_id:int):
    infraction_log(user_id, "Warn", reason_message, issued_by_id)
    
    
def get_infractions(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM infraction_log WHERE user_id = ? ORDER BY time DESC",(user_id, ))
    infraction_list = db.c.fetchall()
    return infraction_list

def remove_infraction(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM infraction_log WHERE user_id = ? ",(user_id, ))
    db.commit()
    db.close()
    
    
#Levelling functions
    
def get_level(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT level FROM user_data WHERE user_id = ? ",(user_id, ))
    return db.c.fetchone()[0]


def get_xp(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT xp FROM user_data WHERE user_id = ? ",(user_id, ))
    return db.c.fetchone()[0]

def add_xp(user_id:int, xp:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET xp = xp + ? WHERE user_id = ?", (xp, user_id,))
    db.commit()
    db.close()
    
def remove_xp(user_id:int, xp:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET xp = xp - ? WHERE user_id = ?", (xp, user_id,))
    db.commit()
    db.close()

def add_level(user_id:int, level:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET level = level + ? WHERE user_id = ?", (level, user_id,))
    db.commit()
    db.close()

def get_leaderboard():
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT author, level, xp FROM user_data ORDER BY xp DESC LIMIT 30")
    infraction_list = db.c.fetchall()
    return infraction_list