from disnake.ext import commands, tasks
import disnake
from utils import database as db, funcs
import math

class Levelling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command(description="Get your rank")
    async def rank(self, inter:disnake.CommandInteraction):
        user = inter.author
        embed = disnake.Embed(title=f"Your Rank")
        embed.set_thumbnail(user.display_avatar)
        level = db.get_level(user.id)
        xp = db.get_xp(user.id)
        next_level_xp = funcs.get_next_level_xp(user.id)
        embed.add_field(name=f"Current Level: ", value=f"`{level}`", inline=False)
        embed.add_field(name=f"Current XP: ", value=f"`{xp}`", inline=False)
        embed.add_field(name=f"Next Level XP: ", value=f"`{next_level_xp}`", inline=False)
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(Levelling(bot))
