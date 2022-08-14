from disnake.ext import commands, tasks
import disnake
from utils import database as db, funcs, pagination

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
        
    @commands.slash_command(description="Shows the rank leaderboard")
    async def leaderboard(self, inter:disnake.CommandInteraction):
        user = inter.author
        leaderboard_string = ""
        embeds = []
        leaderboard_list = db.get_leaderboard()
        divived_leaderboard_list = list(pagination.divide_list(leaderboard_list, 5)) #All infraction divided in lists of length 10 (so we can paginate)
        for leaderboard in divived_leaderboard_list:
            embed = disnake.Embed(title=f"Ranking Leaderboard", description=leaderboard_string)
            embeds.append(embed)
            for index, row in enumerate(leaderboard):
                #indexes represent location of column in row log table
                user_mention = f"<@{row[0]}>"
                level = row[1]
                xp = row[2]
                embed.add_field(name = f"{index+1})" , value = f"User: {user_mention}\nLevel: `{level}`\nXP: `{xp}`\n",inline=False)
        if len(embeds) == 0:
            await inter.send(f"No one in this server has been registered to the bot. Start by typing in chat.✅", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))

    @commands.slash_command(description="Add XP to user")
    async def addxp(self, inter:disnake.CommandInteraction, user:disnake.Member, xp:int):
        db.add_xp(user.id, xp)
        await inter.send(f"Added {xp} to {user.mention}", ephemeral=True)
        
    @commands.slash_command(description="Add XP to user")
    async def removexp(self, inter:disnake.CommandInteraction, user:disnake.Member, xp:int):
        db.remove_xp(user.id, xp)
        await inter.send(f"Removed {xp} from {user.mention}", ephemeral=True)
        
    @commands.slash_command(description="Shows player profile")
    async def profile(self, inter:disnake.CommandInteraction):
        user = inter.author
        username = user.name
        user_joined_at = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S")
        user_created_at = user.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        level = db.get_level(user.id)
        xp = db.get_xp(user.id)
        next_level_xp = funcs.get_next_level_xp(user.id)
        embed = disnake.Embed(title=f"User Profile", 
                             description=f"\
                             Username: `{username}`\n\
                             User ID: `{user.id}`\n\
                             Joined at: `{user_joined_at}`\n\
                             Created at: `{user_created_at}`\n\
                             Level: `{level}`\n\
                             XP: `{xp}/{next_level_xp}`\n\
                             ")
        embed.set_thumbnail(url=user.display_avatar)
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(Levelling(bot))
