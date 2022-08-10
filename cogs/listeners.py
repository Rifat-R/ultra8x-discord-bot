from disnake.ext import commands
from utils import database as db
import sqlite3

class listeners_Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # print(message.content[0])
        if not message.author.bot:
            if message.content[0] != ".":
                try:
                    db.create(message.author.id)
                    print(f"User {message.author.id} has been created and stored in user_data table.")
                except(sqlite3.IntegrityError):
                    pass

def setup(bot):
    bot.add_cog(listeners_Cog(bot))
