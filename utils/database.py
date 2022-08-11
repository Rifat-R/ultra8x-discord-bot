import sqlite3
from datetime import datetime

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
MODERATION = "moderation_logs.db"

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

def create(user_id:int):
    """Creates a blank account for the user in the user_data table.
    This makes sure the other functions will be able to work or else
    they will not work due to the user not existing in the database.

    Args:
        user_id (int): The discord user's ID.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO user_data (user_id) VALUES (?)",(user_id,))
    db.conn.commit()
    db.conn.close()
    print(f"Created new account for user {user_id}")

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


#Logging system
def infraction_log(user_id:int, infraction_type:str, reason_message:str, issued_by_id:int):
    time = datetime.now() 
    db = database(MODERATION)
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
    db = database(MODERATION)
    db.start_connection()
    db.c.execute(f"SELECT * FROM infraction_log WHERE user_id = ? ORDER BY time DESC",(user_id, ))
    infraction_list = db.c.fetchall()
    return infraction_list

def remove_infraction(user_id:int):
    db = database(MODERATION)
    db.start_connection()
    db.c.execute(f"DELETE FROM infraction_log WHERE user_id = ? ",(user_id, ))
    db.commit()
    db.close()
    
    
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

