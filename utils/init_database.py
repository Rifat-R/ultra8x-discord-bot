from utils import database as db

player_data = db.database("player_data.db")
moderation = db.database("moderation_logs.db")


def restore_database():
    
    player_data.start_connection()
    player_data.c.execute("""CREATE TABLE IF NOT EXISTS user_data
    (
    user_id INTEGER PRIMARY KEY,
    wallet INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0
    ) 
    """)
    player_data.conn.commit()
    


    moderation.start_connection()
    moderation.c.execute("""CREATE TABLE IF NOT EXISTS infraction_log
    (
    user_id INTEGER,
    time DATETIME,
    reason TEXT,
    issued_by_id INTEGER,
    infraction_type TEXT,
    PRIMARY KEY (user_id, time)
    ) 
    """)
    moderation.commit()
    moderation.close()
    
    # moderation.c.execute("""CREATE TABLE IF NOT EXISTS ban_log
    # (
    # user_id INTEGER,
    # reason TEXT,
    # issued_by_id,
    # time DATETIME
    # ) 
    # """)
    # moderation.commit()
    # moderation.c.execute("""CREATE TABLE IF NOT EXISTS kick_log
    # (
    # user_id INTEGER,
    # reason TEXT,
    # issued_by_id,
    # time DATETIME
    # ) 
    # """)
    # moderation.commit()
    
    # moderation.c.execute("""CREATE TABLE IF NOT EXISTS mute_log
    # (
    # user_id INTEGER,
    # reason TEXT,
    # duration TEXT,
    # issued_by_id,
    # time DATETIME
    # ) 
    # """)
    # moderation.commit()
    
    # moderation.c.execute("""CREATE TABLE IF NOT EXISTS warn_log
    # (
    # user_id INTEGER,
    # reason TEXT,
    # issued_by_id,
    # time DATETIME
    # ) 
    # """)
    # moderation.commit()
    # moderation.close()
