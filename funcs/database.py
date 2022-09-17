import sqlite3
from datetime import datetime, timedelta
from funcs import funcs

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
    
def reset_economy(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET wallet = 0, bank = 0 WHERE user_id = ? ",(user_id, ))
    db.commit()
    db.close()

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

def get_rich_rank(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT ROW_NUMBER() OVER (ORDER BY (wallet + bank) DESC) row_num, user_id, (wallet+bank) FROM user_data")
    rich_rank_list = db.c.fetchall()
    print(rich_rank_list)
    for rich_rank_tuple in rich_rank_list:
        if rich_rank_tuple[1] == user_id:
            return rich_rank_tuple[0]
    


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


def reset_levelling_sector(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_data SET xp = 0, level = 0 WHERE user_id = ? ",(user_id, ))
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


#Job functions

def set_working_status_true(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_job SET working_status = ? WHERE user_id = ?", (1, user_id))
    db.commit()
    db.close()

def set_working_status_false(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_job SET working_status = ? WHERE user_id = ?", (0, user_id))
    db.commit()
    db.close()
    
def get_working_status(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT working_status FROM user_job WHERE user_id = ?", (user_id,))
    working_status = db.c.fetchone()[0]
    if working_status == 1:
        return True
    elif working_status == 0:
        return False


def get_job(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT job FROM user_job WHERE user_id = ?", (user_id,))
    job = db.c.fetchone()
    return job[0]

def add_job(user_id:int, job:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO user_job (user_id, job, cooldown_timestamp) VALUES (?, ?, ?)",(user_id, job, datetime.now()))
    db.commit()
    db.close()
    
def remove_job(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM user_job WHERE user_id = ?",(user_id,))
    db.commit()
    db.close()
    
def get_job_cooldown_timestamp(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT cooldown_timestamp FROM user_job WHERE user_id = ?", (user_id,))
    job = db.c.fetchone()
    return job[0]

def reset_job_cooldown(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"UPDATE user_job SET cooldown_timestamp = ? WHERE user_id = ?", (datetime.now(), user_id))
    db.commit()
    db.close()
    
def check_if_has_job(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM user_job WHERE user_id = {user_id}")
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
    
#Ticket functions

def add_ticket(user_id:int, channel_id:int, reason:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO tickets (user_id, channel_id, reason, created_at) VALUES (?, ?, ?, ?)",(user_id, channel_id, reason, datetime.now()))
    db.commit()
    db.close()
    
def remove_ticket(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM tickets WHERE user_id = ?",(user_id,))
    db.commit()
    db.close()
    
def get_ticket_channel(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT channel_id FROM ticket WHERE user_id = ?", (user_id,))
    job = db.c.fetchone()
    return job[0]

def get_ticket_list():
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT user_data.author, tickets.channel_id, tickets.reason, tickets.created_at FROM tickets INNER JOIN user_data ON user_data.user_id = tickets.user_id ORDER BY tickets.created_at DESC")
    ticket_list = db.c.fetchall()
    return ticket_list
    
def check_if_has_ticket(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM tickets WHERE user_id = {user_id}")
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
    
#Company functions
def create_company(company_name:str, user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO companies (company_name, user_id, created_at) VALUES (?, ?, ?)",(company_name, user_id, datetime.now()))
    db.commit()
    db.close()
    

def get_company_name(user_id:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT company_name FROM companies WHERE user_id = ?",(user_id,))
    return db.c.fetchone()[0]

def check_if_has_company(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM companies WHERE user_id = {user_id}")
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
def get_company_created_at(company_name: str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT created_at FROM companies WHERE company_name = ?",(company_name,))
    return db.c.fetchone()[0]

def get_company_founder_author(company_name : str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT user_data.author FROM user_data INNER JOIN companies ON companies.user_id = user_data.user_id WHERE company_name = ?", (company_name,))
    return db.c.fetchone()[0]
    
def company_inventory_add_product(company_name: str, product_id:str, count:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    try:
        db.c.execute(f"INSERT INTO company_inventory (company_name, product_id, count) VALUES (?, ?, ?)",(company_name, product_id, count))
    except sqlite3.IntegrityError:
        db.c.execute(f"UPDATE company_inventory SET count = count + ? WHERE company_name = ? AND product_id = ?", (count, company_name, product_id))
    
    db.commit()
    db.close()

def get_company_inventory_list(company_name: int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT product_id, count FROM company_inventory WHERE company_name = ?", (company_name,))
    return db.c.fetchall()
    
def delete_company(company_name:int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM companies WHERE company_name = ?",(company_name,))
    db.c.execute(f"DELETE FROM factories WHERE company_name = ?",(company_name,))
    db.c.execute(f"DELETE FROM running_factories WHERE company_name = ?",(company_name,))
    db.commit()
    db.close()
    
    
def add_company_employee(user_id: int, company_name: str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO company_employees (user_id,company_name) VALUES (?,?)",(user_id, company_name))
    db.commit()
    db.close()
    
def remove_company_employee(user_id: int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM company_employees WHERE user_id = ?",(user_id,))
    db.commit()
    db.close()
    
def get_employee_company_name(user_id: int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT company_name FROM company_employees WHERE user_id = ?", (user_id,))
    return db.c.fetchone()[0]

def check_if_employee(user_id : int):
    db = database(PLAYER_DATA)
    
    db.start_connection()
    db.c.execute(f"SELECT * FROM company_employees WHERE user_id = ?", (user_id,))
    
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
def get_company_networth(company_name):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT (user_data.bank + user_data.wallet) FROM user_data INNER JOIN company_employees ON company_employees.user_id = user_data.user_id WHERE company_name = ?", (company_name,))
    employee_networth = db.c.fetchall()
    db.c.execute(f"SELECT (user_data.bank + user_data.wallet) FROM user_data INNER JOIN companies ON companies.user_id = user_data.user_id WHERE company_name = ?", (company_name,))
    founder_networth = db.c.fetchall()
    networth_list = employee_networth + founder_networth
    networth_list = [i[0] for i in networth_list]
    return sum(networth_list)

def get_number_of_employees(company_name: str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT COUNT(company_name) FROM company_employees WHERE company_name = ?", (company_name,))
    return db.c.fetchone()[0]
#Factory functions

def add_factory(company_name:str, factory_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO factories (company_name,factory_id) VALUES (?,?)",(company_name, factory_id))
    db.commit()
    db.close()
  
    
def get_owned_factories(company_name:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT factory_id FROM factories WHERE company_name = ?", (company_name,))
    owned_factories = db.c.fetchall()
    owned_factories = [i[0] for i in owned_factories]
    return owned_factories
    
def delete_factory(company_name:int, factory_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM factories WHERE company_name = ? AND factory_id = ?",(company_name, factory_id))
    db.commit()
    db.c.execute(f"DELETE FROM running_factories WHERE company_name = ? AND factory_id = ?",(company_name, factory_id))
    db.commit()
    db.close()
    
def add_running_factory(company_name:str, factory_id, product_id, timestamp_until_completion):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"INSERT INTO running_factories (company_name,factory_id,product_id,until_completion) VALUES (?,?,?,?)",(company_name, factory_id,product_id,timestamp_until_completion))
    db.commit()
    db.close()    
    
def stop_running_factory(company_name:int, factory_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM running_factories WHERE company_name = ? AND factory_id = ?",(company_name, factory_id))
    db.commit()
    db.close()
    
def get_running_factory_timestamp(company_name:str, factory_id:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT until_completion FROM running_factories WHERE company_name = ? AND factory_id = ?", (company_name,factory_id))
    return db.c.fetchone()[0]

def get_running_factory_product_id(company_name:str, factory_id:str):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT product_id FROM running_factories WHERE company_name = ? AND factory_id = ?", (company_name,factory_id))
    return db.c.fetchone()[0]
    
def check_if_has_factory(company_name:str, factory_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM factories WHERE company_name = ? AND factory_id = ?", (company_name, factory_id))
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True

def check_if_has_running_factory(company_name:str, factory_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM running_factories WHERE company_name = ? AND factory_id = ?", (company_name, factory_id))
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
#Jail system functions

def add_user_to_jail(user_id: int, duration: int):
    """Add's user to jail.

    Args:
        user_id (int): User's discord ID
        duration (int): Duration measured in HOURS.
    """
    db = database(PLAYER_DATA)
    db.start_connection()
    user_free_timestamp = datetime.now() + timedelta(hours = duration)
    db.c.execute(f"INSERT INTO jail (user_id, until_free) VALUES (?,?)",(user_id, user_free_timestamp))
    db.commit()
    db.close() 

def remove_user_from_jail(user_id: int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"DELETE FROM jail WHERE user_id = ?",(user_id,))
    db.commit()
    db.close()
    
def check_if_user_in_jail(user_id):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT * FROM jail WHERE user_id = ?", (user_id,))
    if len(db.c.fetchall()) == 0:
        return False
    else:
        return True
    
def get_user_jail_timestamp(user_id: int):
    db = database(PLAYER_DATA)
    db.start_connection()
    db.c.execute(f"SELECT until_free FROM jail WHERE user_id = ?", (user_id,))
    return db.c.fetchone()[0]