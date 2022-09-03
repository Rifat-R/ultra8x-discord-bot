from disnake.ext import commands, tasks
from disnake.ui import Button, View
import disnake
from funcs import database as db, funcs, pagination, constants as const

class Levelling(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

# RANK COMMAND
    @commands.slash_command(description="Get your rank")
    async def rank(self, inter: disnake.CommandInteraction, user: disnake.Member = None):
        #user = inter.author

        if user is None:
            user = inter.author

        embed = disnake.Embed(title=f"{user.name}'s Rank")
        embed.set_thumbnail(user.display_avatar)
        level = db.get_level(user.id)
        xp = db.get_xp(user.id)
        next_level_xp = funcs.get_next_level_xp(user.id)

        embed.add_field(name=f"Current Level: ", value=f"`{level}`", inline=False)
        embed.add_field(name=f"Current XP: ", value=f"`{xp}`", inline=True)
        embed.add_field(name=f"Next Level: ", value=f"`{next_level_xp}`", inline=True)
        embed.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
        await inter.send(embed=embed)

# LEADERBOARD COMMAND
    @commands.slash_command(description="Shows the rank leaderboard")
    async def leaderboard(self, inter:disnake.CommandInteraction):
        user = inter.author
        leaderboard_string = ""
        embeds = []
        leaderboard_list = db.get_leaderboard()
        divided_leaderboard_list = list(pagination.divide_list(leaderboard_list, 5))    #All infraction divided in lists of length 10 (so we can paginate)
        for leaderboard in divided_leaderboard_list:
            embed = disnake.Embed(title=f"Ranking Leaderboard", description=leaderboard_string)
            embeds.append(embed)
            for index, row in enumerate(leaderboard):
                #indexes represent location of column in row log table
                user_mention = f"`{row[0]}`"
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
        
    @commands.slash_command(description="Reset your level or economy.")
    async def reset(self, inter:disnake.CommandInteraction, sector:str):
        """
        Withdraw money from your bank balance
        Parameters
        ----------
        sector: Can be only 'xp' or 'economy'. Reset's the stats of which sector you choose.
        """
        sector = sector.lower()
        if sector != "xp" and sector != "economy":
            await inter.send(f"You must pick between `xp` or `economy`", ephemeral = True)
            return
        
        if sector == "xp":
            reset_func = db.reset_levelling_sector
        if sector == "economy":
            reset_func = db.reset_economy
            
        reset_button = Button(label="Reset", style=disnake.ButtonStyle.danger)
        cancel_button = Button(label="Cancel", style=disnake.ButtonStyle.green)
        
        
        view = View()
        async def reset_button_callback(interaction:disnake.CommandInteraction):
            if interaction.author.id != inter.author.id:
                await interaction.response.send_message(f"This is not your embed to use.", ephemeral = True)
                return
            reset_func(interaction.author.id)
            embed = disnake.Embed(description = f"You have **RESET** your `{sector}` sector!", color = const.EMBED_COLOUR)
            embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
            reset_button.disabled = True
            cancel_button.disabled = True
            await interaction.response.send_message(embed=embed)
            await inter.edit_original_message(view=view)


        async def cancel_button_callback(interaction:disnake.CommandInteraction):
            embed = disnake.Embed(description = f"You have cancelled your `{sector}` reset.", color = const.EMBED_COLOUR)
            embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
            reset_button.disabled = True
            cancel_button.disabled = True
            await interaction.response.send_message(embed=embed)
            await inter.edit_original_message(view=view)
            
        reset_button.callback = reset_button_callback
        cancel_button.callback = cancel_button_callback
        view.add_item(reset_button)
        view.add_item(cancel_button)
        embed = disnake.Embed(description=f"Are you **SURE** you want to reset the following sector: `{sector}`", color = const.EMBED_COLOUR)
        embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
        await inter.send(embed=embed, view=view)
        
        
        
            
        
        
        
    
    

def setup(bot):
    bot.add_cog(Levelling(bot))
