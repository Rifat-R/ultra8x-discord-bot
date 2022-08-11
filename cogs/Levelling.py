from disnake.ext import commands
from utils import database as db

class Levelling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(Levelling(bot))
