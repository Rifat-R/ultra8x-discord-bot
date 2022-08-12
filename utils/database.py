import aiosqlite
from datetime import datetime

PLAYER_DATA = "player_data.db"
# conn = await aiosqlite.connect(PLAYER_DATA, detect_types=aiosqlite.PARSE_DECLTYPES | aiosqlite.PARSE_COLNAMES)
async def update_wallet(user_id:int,money:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"UPDATE user_data SET wallet = wallet + {money} WHERE user_id = {user_id}") 
        await db.commit()

async def deduct_wallet(user_id:int,money:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"UPDATE user_data SET wallet = wallet - {money} WHERE user_id = {user_id}")
        await db.commit()

async def update_bank(user_id:int,money:int):
    """Adds money to the user's bank in the user_data table.

    Args:
        user_id (int): The discord user's ID.
        money (int): The amount of money added to the user's bank.
    """
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"UPDATE user_data SET bank = bank + {money} WHERE user_id = {user_id}")
        await db.commit()

async def deduct_bank(user_id:int,money:int):
    """Deducts money from the user's bank in the user_data table.

    Args:
        user_id (int): The discord user's ID.
        money (int): The amount of money that is going to be deducted from the user's bank account.
    """
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"UPDATE user_data SET bank = bank - {money} WHERE user_id = {user_id}")
        await db.commit()

async def create(user_id:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"INSERT INTO user_data (user_id) VALUES (?)",(user_id,))
        await db.commit()

async def wallet(user_id:int) -> int:
    async with aiosqlite.connect(PLAYER_DATA) as db:
        async with db.execute(f"SELECT wallet FROM user_data WHERE user_id = {user_id}") as cursor:
            row = await cursor.fetchone()
            bank_balance = row[0]
            return bank_balance

async def bank(user_id:int) -> int:
    async with aiosqlite.connect(PLAYER_DATA) as db:
        async with db.execute(f"SELECT bank FROM user_data WHERE user_id = {user_id}") as cursor:
            row = await cursor.fetchone()
            bank_balance = row[0]
            return bank_balance


#Levelling functions

async def get_level(user_id:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        async with db.execute(f"SELECT level FROM user_data WHERE user_id = {user_id}") as cursor:
            row = await cursor.fetchone()
            level = row[0]
            return level

async def get_xp(user_id:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        async with db.execute(f"SELECT xp FROM user_data WHERE user_id = {user_id}") as cursor:
            row = await cursor.fetchone()
            xp = row[0]
            return xp

async def add_xp(user_id:int, xp:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"UPDATE user_data SET xp = xp + ? WHERE user_id = ?", (xp, user_id,))
        await db.commit()


#Logging system
async def infraction_log(user_id:int, infraction_type:str, reason_message:str, issued_by_id:int):
    time = datetime.now() 
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"INSERT INTO infraction_log VALUES (?,?,?,?,?)",(user_id, time, reason_message, issued_by_id, infraction_type,))
        await db.commit()
    
async def ban_log(user_id:int, reason_message:str, issued_by_id:int):
    await infraction_log(user_id, "Ban", reason_message, issued_by_id)
    
async def mute_log(user_id:int, reason_message:str, issued_by_id:int):
    await infraction_log(user_id, "Mute", reason_message, issued_by_id)
    
async def kick_log(user_id:int, reason_message:str, issued_by_id:int):
    await infraction_log(user_id, "Kick", reason_message, issued_by_id)
    
async def warn_log(user_id:int, reason_message:str, issued_by_id:int):
    await infraction_log(user_id, "Warn", reason_message, issued_by_id)
    
    
async def get_infractions(user_id:int) -> list:
    async with aiosqlite.connect(PLAYER_DATA) as db:
        async with db.execute(f"SELECT * FROM infraction_log WHERE user_id = ? ORDER BY time DESC",(user_id, )) as cursor:
            infraction_list = await cursor.fetchall()
            return infraction_list

async def remove_infraction(user_id:int):
    async with aiosqlite.connect(PLAYER_DATA) as db:
        await db.execute(f"DELETE FROM infraction_log WHERE user_id = ? ",(user_id, ))
        await db.commit()

