from utils import database as db

player_data = db.database("player_data.db")
moderation = db.database("moderation_logs.db")


def restore_database():
    # Creates player_data tables if player_data.db does not exist.
    player_data.start_connection()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS user_data
    (
    user_id INTEGER PRIMARY KEY,
    wallet INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0
    ) 
    """)
    player_data.conn.commit()

    # Creates moderation tables if moderation.db does not exist.

    moderation.start_connection()
    moderation.c.execute("""CREATE TABLE IF NOT EXISTS ban_log
    (
    user_id INTEGER,
    reason TEXT,
    time DATETIME
    ) 
    """)
    moderation.commit()
    moderation.c.execute("""CREATE TABLE IF NOT EXISTS kick_log
    (
    user_id INTEGER,
    reason TEXT,
    time DATETIME
    ) 
    """)
    moderation.commit()
    #Duration will be in seconds for the mute_log database
    moderation.c.execute("""CREATE TABLE IF NOT EXISTS mute_log
    (
    user_id INTEGER,
    reason TEXT,
    duration INTEGER,
    time DATETIME
    ) 
    """)
    moderation.commit()

    moderation.close()
