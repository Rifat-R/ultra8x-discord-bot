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
    player_data.close()