import sqlite3
from datetime import datetime

class database:
    def __init__(self, database):
        self.database = database #gets the database name from constructor

    def start_connection(self):
        """
        Starts connection to database and creating cursor.
        """
        self.conn = sqlite3.connect(self.database) #Connects to the database
        self.c = self.conn.cursor() #Inititalises the cursor, this can now be used globally and be used to
        #do other sql queries than the set functions in the class

    def close(self):
        """Closes connection to database"""
        self.conn.close() #closes the connection to the database. This is needed to stop database locking so other
        #transactions can be made.

    def commit(self):
        """Commits transaction in database"""
        self.conn.commit() #This commits any changes to the database

    def finding(self, user_id, table = "player_profile"):
        """Fetches entire row data from sql database.
        Args:
            user_id (integer): The discord user id
            table (string), optional): Table name. Defaults to "player_profile".
        Returns:
            list: Returns list of all row data of a user.
        """
        if table == None: #Since this is used quite often for the table "player_profile", it is defaulted as it.
            self.c.execute(f"SELECT * FROM player_profile WHERE id = {user_id}")
            return self.c.fetchone()
        else: #If another table is needed to fetch the information of a row, we can do it by specifying the table
            self.c.execute(f"SELECT * FROM {table} WHERE id = {user_id}")
            return self.c.fetchone()

    def show_all(self, table): #Returns all rows and attribiutes from a table
            self.c.execute(f"SELECT * FROM {table}")
            return self.c.fetchall()


#Methods for economy

#database name constants as they are used multiple times and makes the code look readable. 
PLAYER_DATA = "player_data.db"
MODERATION = "moderation_logs.db"

def update_wallet(user_id:int,money:int):
    """Adds money to a user's wallet in the user_data table

    Args:
        user_id (int): The user's discord ID.
        money (int): The amount of money transferred to the user's wallet
    """
    db = database(PLAYER_DATA) #Starts initialisation to the class database and passed in the database file name parameter for it to be connected to later.
    db.start_connection() #Starts the connection to the database and initialises the cursor and connection.
    db.c.execute(f"UPDATE user_data SET wallet = wallet + {money} WHERE user_id = {user_id}") #This is the query that we want to pass to the SQL database.
    db.conn.commit() #Commits the transaction we just made from the query.
    db.conn.close() #Closes the connection to the database so we don't have an open database whilst other transactions are happening.

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


def ban_log(user_id:int, reason_message:str):
    time = datetime.now() #This gets the current time in a datetime datatype. This allows us to instantly put this variable into the
    #database query as it is already in a datetime datatype format. The function datetime has been imported at the start of this file.
    db = database(MODERATION)
    db.start_connection()
    db.c.execute(f"INSERT INTO ban_log VALUES (?,?,?)",(user_id, reason_message, time,))
    db.commit()
    db.close()
    
    
def kick_log(user_id:int, reason_message:str):
    time = datetime.now() #This gets the current time in a datetime datatype. This allows us to instantly put this variable into the
    #database query as it is already in a datetime datatype format. The function datetime has been imported at the start of this file.
    db = database(MODERATION)
    db.start_connection()
    db.c.execute(f"INSERT INTO kick_log VALUES (?,?,?)",(user_id, reason_message, time,))
    db.commit()
    db.close()
    
    
def mute_log(user_id:int, reason_message:str):
    time = datetime.now() #This gets the current time in a datetime datatype. This allows us to instantly put this variable into the
    #database query as it is already in a datetime datatype format. The function datetime has been imported at the start of this file.
    db = database(MODERATION)
    db.start_connection()
    db.c.execute(f"INSERT INTO mute_log VALUES (?,?,?)",(user_id, reason_message, time,))
    db.commit()
    db.close()