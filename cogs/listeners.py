from disnake.ext import commands
import disnake
from utils import database as db, constants as const, funcs
import sqlite3
import math


class listeners_Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_message(self, message:disnake.Message):
        user_id = message.author.id
        if not message.author.bot:
            if db.check_user(user_id):
                db.add_xp(user_id, 10)
                current_level = db.get_level(user_id)
                exact_level = funcs.get_exact_level(user_id)
                print(exact_level)
                if exact_level - 1 >= current_level:
                    level_added = math.floor((exact_level)) - current_level
                    db.add_level(user_id, level_added)
                    new_level = db.get_level(user_id)
                    await message.channel.send(f"You have increased by {level_added} Level! You are now Level {new_level}")
                    
            else:
                db.create(user_id)
                db.add_xp(user_id, 10)
                print(f"User {user_id} has been created and stored in user_data table.")


def setup(bot):
    bot.add_cog(listeners_Cog(bot))
