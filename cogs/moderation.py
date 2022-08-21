from os import remove
import disnake
from disnake.ext import commands
from disnake.utils import get
from utils import database as db, pagination, constants as const, serverconfig as conf



class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Warns a member in the server")
    async def warn(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        db.warn_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Warn", color= const.EMBED_COLOUR)
        embed.add_field(name="User warned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)

    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Kicks a member in the server")
    async def kick(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        """Kicks a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.kick(reason=reason)
        db.kick_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Kick", color= const.EMBED_COLOUR)
        embed.add_field(name="User kicked:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)


    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Bans user from the server")
    async def ban(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        """Bans a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.ban(reason=reason)
        db.ban_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Ban", color= const.EMBED_COLOUR)
        embed.add_field(name="User banned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)
        
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Gives user a timeout")
    async def mute(self, inter, member: disnake.Member, time:int, *, reason="No reason has been given"):
        """
        Mute command
        Parameters
        ----------
        member: The user you want to mute.
        time: Time muted in SECONDS.
        reason: Give a reason for the mute. Not mandatory.
        """
        await member.timeout(duration=time)
        muted_until = member.current_timeout.strftime("%m/%d/%Y, %H:%M:%S")
        db.mute_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Mute", description=f"{member.mention} has been tempmuted ", color= const.EMBED_COLOUR)
        embed.add_field(name="User muted:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Muted until: ", value=f"**{muted_until}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Removes user from timeout")
    async def unmute(self, inter, member: disnake.Member,*, reason="No reason has been given"):
        await member.timeout(duration=None)
        embed = disnake.Embed(title="Unmuted", color = const.EMBED_COLOUR)
        embed.add_field(name="User unmuted: ", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)
                    
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Purges an amount of messages from the text channel")
    async def clear(self, inter, amount : int):
        await inter.channel.purge(limit=int(amount + 1))
        messages = "message" if amount==1 else "messages"
        await inter.send(f"You deleted **{amount}** {messages}", ephemeral=True)
        
    
    @commands.slash_command(description="Shows server info")
    async def serverinfo(self, inter):
        server_id = inter.guild.id
        server_name = inter.guild.name
        server_owner_id = inter.guild.owner_id
        embed= disnake.Embed(title="Server Info", 
                             description=f"\
                             Server Name: {server_name}\n\
                             Server ID: {server_id}\n\
                             Server Owner: <@{server_owner_id}>\n\
                             ", color = const.EMBED_COLOUR)
        embed.set_thumbnail(inter.guild.icon)
        await inter.send(embed=embed)
        
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Shows user info")
    async def userinfo(self, inter:disnake.CommandInteraction, user:disnake.Member):
        user_id = user.id
        username = user.name
        user_pfp = user.avatar.url
        user_joined_at = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S")
        user_created_at = user.created_at.strftime("%m/%d/%Y, %H:%M:%S")
        embed = disnake.Embed(title=f"User Information", 
                             description=f"\
                             Username: `{username}`\n\
                             User ID: `{user_id}`\n\
                             Joined at: `{user_joined_at}`\n\
                             Created at: `{user_created_at}`\n\
                             ", color = const.EMBED_COLOUR)
        embed.set_thumbnail(user_pfp)
        await inter.send(embed=embed)
        
    
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Gets user infractions")
    async def infractions(self, inter:disnake.CommandInteraction, user:disnake.Member):
        infraction_string = ""
        embeds = []
        counter = 1
        infractions_list = db.get_infractions(user.id) #All infractions of a user in one list
        divided_infraction_list = list(pagination.divide_list(infractions_list, 5)) #All infraction divided in lists of length 10 (so we can paginate)
        for infraction_list in divided_infraction_list:
            embed = disnake.Embed(title=f"Infractions of {user.name}", description=infraction_string, color = const.EMBED_COLOUR)
            embeds.append(embed)
            for infraction in infraction_list:
                #indexes represent location of column in infraction log table
                time_of_infraction = infraction[1].strftime("%m/%d/%Y, %H:%M:%S")
                reason = infraction[2]
                issued_by_id = infraction[3]
                infraction_type = infraction[4]
                embed.add_field(name = f"{counter})" , value = f"Time of infraction:`{time_of_infraction}`\nType: `{infraction_type}`\nReason: `{reason}`\nIssued by: <@{issued_by_id}>",inline=False)
                counter += 1
        

        if len(embeds) == 0:
            await inter.send(f"User has no infractions ✅", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))
            
            
    @commands.has_any_role(*const.STAFF_ROLE)
    @commands.slash_command(description="Removes ALL user infractions")
    async def remove_infractions(self, inter:disnake.CommandInteraction, user:disnake.Member):
        db.remove_infraction(user.id)
        await inter.send(f"Removed infractions from user {user.mention} ✅", ephemeral = True)
        
    
    #Server config commands
    @commands.Cog.listener()
    async def on_message(self, message:disnake.Message):
        if not message.author.bot:
            filter_word_list = conf.get_filter_word_list()
            for word in filter_word_list:
                if word in message.content:
                    await message.delete()
                    reason_message = "Used inappropriate language"
                    db.warn_log(message.author.id, reason_message, self.bot.user.id)
                    await message.channel.send(f"{message.author.mention} You have used innapropriate language hence your message was deleted. You have gained a warn infraction.")
                    return
        
    @commands.slash_command()
    async def serverconf(self, ctx):
        pass
    
    @commands.has_any_role(*const.STAFF_ROLE)
    @serverconf.sub_command(description="Add a word to the word filtering list")
    async def add_filter_word(self, inter:disnake.CommandInteraction, word:str):
        filter_word_list = conf.get_filter_word_list()
        if word in filter_word_list:
            await inter.send(f"The word `{word}` already exists in the filtering list.", ephemeral = True)
            return
        conf.add_filter_word(word)
        await inter.send(f"Added word `{word}` to the filtering list", ephemeral = True)
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @serverconf.sub_command(description="Remove a word from the word filtering list")
    async def remove_filter_word(self, inter:disnake.CommandInteraction, word:str):
        try:
            conf.remove_filter_word(word)
        except ValueError:
            await inter.send(f"The word `{word}` does not exist in the filter word list.", ephemeral = True)
        else:
            await inter.send(f"Removed word `{word}` from the filter word list", ephemeral = True)
            
    @commands.has_any_role(*const.STAFF_ROLE)
    @serverconf.sub_command(description="See the word filtering list")
    async def get_filter_word_list(self, inter:disnake.CommandInteraction):
        filter_word_list = conf.get_filter_word_list()
        await inter.send(f"Word list: {filter_word_list}", ephemeral = True)
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @serverconf.sub_command(description="Set welcome message")
    async def set_welcome_message(self, inter:disnake.CommandInteraction, channel:disnake.TextChannel, message:str):
        conf.set_welcome_message(inter.guild_id, channel.id, message)
        await inter.send(f"You have updated welcome message to\n`{message}`")
        
    @commands.has_any_role(*const.STAFF_ROLE)
    @serverconf.sub_command(description="Get welcome message")
    async def get_welcome_message(self, inter:disnake.CommandInteraction):
        message, channel_id = conf.get_welcome_message(inter.guild_id)
        await inter.send(f"Welcome message:\n `{message}`")
		

    @warn.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)
    @mute.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)

    @kick.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)

    @ban.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)
    @infractions.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)
    @remove_infractions.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)
            
    @userinfo.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)
            
            
    @clear.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingAnyRole): 
            await ctx.send(f"You do not have any of these roles: `{error.missing_roles}` to use this command.", ephemeral = True)



def setup(bot):
    bot.add_cog(Moderation(bot))