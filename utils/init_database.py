import aiosqlite


PLAYER_DATA = "player_data.db"

async def restore_database():
    conn = await aiosqlite.connect(PLAYER_DATA) #detect_types so time type is datetime  
    c = await conn.cursor() 
    await c.execute("""CREATE TABLE IF NOT EXISTS user_data
    (
    user_id INTEGER PRIMARY KEY,
    wallet INTEGER DEFAULT 0,
    bank INTEGER DEFAULT 0,
    level INTEGER DEFAULT 0,
    xp INTEGER DEFAULT 0
    ) 
    """)
    await conn.commit()

    await c.execute("""CREATE TABLE IF NOT EXISTS infraction_log
    (
    user_id INTEGER,
    time TIMESTAMP,
    reason TEXT,
    issued_by_id INTEGER,
    infraction_type TEXT,
    PRIMARY KEY (user_id, time)
    ) 
    """)
    await conn.commit()
    await conn.close()
    
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
