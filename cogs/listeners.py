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
        user = message.author
        if not message.author.bot:
            if db.check_user(user.id):
                if str(user) != db.get_author(user.id):
                    db.update_author(user.id, str(user))
                db.add_xp(user.id, 10)
                current_level = db.get_level(user.id)
                exact_level = funcs.get_exact_level(user.id)
                if (exact_level-1) >= current_level:
                    level_added = math.floor((exact_level)) - current_level
                    db.add_level(user.id, level_added)
                    new_level = db.get_level(user.id)
                    await message.channel.send(f"You have increased by {level_added} Level! You are now Level {new_level}")
            else:
                db.create(user.id, str(user))
                db.add_xp(user.id, 10)
                print(f"User {user.id} has been created and stored in user_data table.")


def setup(bot):
    bot.add_cog(listeners_Cog(bot))
