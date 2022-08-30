from utils import database as db, constants as const

player_data = db.database(const.PLAYER_DATA_DATABASE)


def restore_database():
    
    player_data.start_connection()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS user_data
    (
    user_id INTEGER PRIMARY KEY,
    author TEXT,
    wallet INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0
    ) 
    """)
    player_data.conn.commit()
    
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS user_inventory
    (
    user_id INTEGER,
    item TEXT,
    PRIMARY KEY (user_id, item)
    ) 
    """)
    player_data.conn.commit()


    player_data.start_connection()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS infraction_log
    (
    user_id INTEGER,
    time TIMESTAMP,
    reason TEXT,
    issued_by_id INTEGER,
    infraction_type TEXT,
    PRIMARY KEY (user_id, time)
    ) 
    """)
    player_data.commit()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS user_job
    (
    user_id INTEGER PRIMARY KEY,
    job TEXT,
    cooldown_timestamp TIMESTAMP,
    working_status BIT DEFAULT 0
    ) 
    """)
    player_data.commit()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS tickets
    (
    user_id INTEGER PRIMARY KEY,
    channel_id INTEGER,
    reason TEXT,
    created_at TIMESTAMP
    ) 
    """)
    player_data.commit()

#Company
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS companies
    (
    company_name TEXT UNIQUE,
    user_id INTEGER UNIQUE,
    created_at TIMESTAMP
    ) 
    """)
    player_data.commit()
#Factory
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS factories
    (
    company_name TEXT,
    factory_id TEXT,
    PRIMARY KEY (company_name, factory_id)
    ) 
    """)
    player_data.commit()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS running_factories
    (
    company_name TEXT,
    factory_id INTEGER,
    product_id TEXT,
    until_completion TIMESTAMP,
    PRIMARY KEY (company_name, factory_id)
    ) 
    """)
    player_data.commit()
    player_data.close()