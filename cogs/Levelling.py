from disnake.ext import commands
import disnake
from utils import database as db
import math

class Levelling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(description="Level")
    async def level(self, inter:disnake.CommandInteraction):
        level = db.get_level(inter.author.id)
        await inter.send(level)

def setup(bot):
    bot.add_cog(Levelling(bot))
