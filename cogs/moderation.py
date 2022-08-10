import disnake
from disnake.ext import commands
from disnake.utils import get
from utils import database as db
import asyncio



unmuted_ids = []

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.EMBED_COLOR = 0xffffff
        
        
    @commands.slash_command(description="Warns a member in the server")
    async def warn(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        db.warn_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Warn", color= self.EMBED_COLOR)
        embed.add_field(name="User warned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)


    @commands.slash_command(description="Kicks a member in the server")
    async def kick(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        """Kicks a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.kick(reason=reason)
        db.kick_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Kick", color= self.EMBED_COLOR)
        embed.add_field(name="User kicked:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)



    @commands.slash_command(description="Bans user from the server")
    async def ban(self, inter, member:disnake.Member, *, reason="No reason has been given"):
        """Bans a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.ban(reason=reason)
        db.ban_log(member.id, reason, inter.author.id)
        embed = disnake.Embed(title="Ban", color= self.EMBED_COLOR)
        embed.add_field(name="User banned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await inter.send(embed=embed)


    @commands.slash_command(description="Kicks user out from the server")
    async def mute(self, inter, member: disnake.Member, time, *, reason="No reason has been given"):
        
        """Mutes a user by server muting them so they cannot speak in voice chat but furthermore assigns them to a muted
            role that revokes their permission to type in chat.

        Args:
            member (disnake.Member): The user's id or their @ 
            time ([type]): The time. This is defaulted to minutes but can be changed if you add a prefix (s,m,d) after the number. 
            reason (str, optional): Reason given for the mute. Defaults to "No reason has been given".
        """
        perms = disnake.Permissions(send_messages=False) 
        created_role = False
        if_mute_is_finished = False
        while not if_mute_is_finished:
            for role in inter.guild.roles:
                if role.name == "Muted": 
                    if time[-1].isalpha(): 
                        real_time = int(time[:-1]) 
                        if time[-1] == "s":
                            time_muted = real_time
                            time_prefix = "second(s)"
                        elif time[-1] == "m":
                            time_muted = real_time * 60
                            time_prefix = "minute(s)"
                        elif time[-1] == "d":
                            time_muted = real_time * 60 * 60
                            time_prefix = "day(s)"
                    else:
                        real_time = int(time)
                        time_muted = real_time * 60
                        time_prefix = "minute(s)"

                    
                    duration = f"{real_time} {time_prefix}"
                    await member.add_roles(role) 
                    embed = disnake.Embed(title="Mute", description=f"{member.mention} has been tempmuted ", color= self.EMBED_COLOR)
                    embed.add_field(name="User muted:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
                    embed.add_field(name="Action issued by:", value=f"**{inter.author.display_name}**", inline=False)
                    embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
                    embed.add_field(name="Mute time: ", value=duration, inline=False)
                    await inter.send(embed=embed) 

                    print(f"Player {member.display_name} has been muted for {real_time} {time_prefix}") 
                    db.mute_log(member.id, reason, duration, inter.author.id)
                    await asyncio.sleep(time_muted) 

                    await member.remove_roles(role) 

                    
                    embed = disnake.Embed(title="Unmuted", color = self.EMBED_COLOR)
                    embed.add_field(name="User unmuted: ", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
                    embed.add_field(name="Time muted for: ", value=f"**{real_time} {time_prefix}**", inline=False)
                    await inter.send(embed=embed)
                    if_mute_is_finished = True 
                    created_role = True 
                    for i in inter.guild.text_channels:
                        await i.set_permissions(role, send_messages=False)

            if not created_role: 
                await inter.guild.create_role(name="Muted", permissions=perms) 
                role = get(inter.guild.roles, name="Muted")
                print(role)
                created_role = True
                for i in inter.guild.text_channels:
                    await i.set_permissions(role, send_messages=False) 
                    
                    
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
                             ")
        embed.set_thumbnail(inter.guild.icon)
        await inter.send(embed=embed)

    @commands.slash_command(description="Shows user info")
    async def userinfo(self, inter:disnake.CommandInteraction, user:disnake.Member):
        user_id = user.id
        username = user.name
        user_pfp = user.avatar.url
        user_joined_at = user.joined_at.strftime("%m/%d/%Y, %H:%M:%S")
        embed= disnake.Embed(title=f"User Information", 
                             description=f"\
                             Username: `{username}`\n\
                             User ID: `{user_id}`\n\
                             Joined at: `{user_joined_at}`\n\
                             ")
        embed.set_thumbnail(user_pfp)
        await inter.send(embed=embed)
        
        
    #Error handlers
    @ban.error
    async def example_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"<@{ctx.author.id}> **Command was typed incorrectly!** `.ban <@user> (<reason>)`"
            await ctx.send(message, delete_after = 10)


    @kick.error
    async def example_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"<@{ctx.author.id}> **Command was typed incorrectly!** `.kick <@user> <time>(<s/m/h/d>) (<reason>)`"
            await ctx.send(message, delete_after = 10)


    @mute.error
    async def example_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            message = f"<@{ctx.author.id}> **Command was typed incorrectly!** `.mute <@user> <time>(<s/m/h/d>) (<reason>)`"
            await ctx.send(message, delete_after = 10)			


def setup(bot):
    bot.add_cog(Moderation(bot))