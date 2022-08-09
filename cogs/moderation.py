import disnake
from disnake.ext import commands
from disnake.utils import get
from utils import database as db
import asyncio

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.EMBED_COLOR = 0xffffff
        
        
    @commands.slash_command(description="Warns a member in the server")
    async def warn(self, ctx, member:disnake.Member, *, reason="No reason has been given"):
        db.warn_log(member.id, reason, ctx.author.id)
        embed = disnake.Embed(title="Ban", color= self.EMBED_COLOR)
        embed.add_field(name="User warned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{ctx.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await ctx.send(embed=embed)


    @commands.slash_command(description="Kicks a member in the server")
    async def kick(self, ctx, member:disnake.Member, *, reason="No reason has been given"):
        """Kicks a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.kick(reason=reason)
        db.kick_log(member.id, reason, ctx.author.id)
        embed = disnake.Embed(title="Kick", color= self.EMBED_COLOR)
        embed.add_field(name="User kicked:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{ctx.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await ctx.send(embed=embed)



    @commands.slash_command(description="Bans user from the server")
    async def ban(self, ctx, member:disnake.Member, *, reason="No reason has been given"):
        """Bans a user from the server

        Args:
            member (disnake.Member): The user's id
            reason (str, optional): The reason for the kick. Defaults to "No reason has been given".
        """
        await member.ban(reason=reason)
        db.ban_log(member.id, reason, ctx.author.id)
        embed = disnake.Embed(title="Ban", color= self.EMBED_COLOR)
        embed.add_field(name="User banned:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
        embed.add_field(name="Action issued by:", value=f"**{ctx.author.display_name}**", inline=False)
        embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
        await ctx.send(embed=embed)


    @commands.slash_command(description="Kicks user out from the server")
    async def mute(self, ctx, member: disnake.Member, time, *, reason="No reason has been given"):
        #The reason for the * is so we can have a string of words with spaces instead of it being seperated as parameters.
        """Mutes a user by server muting them so they cannot speak in voice chat but furthermore assigns them to a muted
            role that revokes their permission to type in chat.

        Args:
            member (disnake.Member): The user's id or their @ 
            time ([type]): The time. This is defaulted to minutes but can be changed if you add a prefix (s,m,d) after the number. 
            reason (str, optional): Reason given for the mute. Defaults to "No reason has been given".
        """
        perms = disnake.Permissions(send_messages=False) #Perm attribiute that makes a users send_messages perm False.
        created_role = False
        if_mute_is_finished = False
        while not if_mute_is_finished:
            for role in ctx.guild.roles:
                if role.name == "Muted": #If the role.name == "Muted" is never found, the entire block of code under this if statement is never run.
                    #After, the role name and its permission gets created and then next time it runs it will find the "Muted" role and run the function
                    #properly
                    if time[-1].isalpha(): #Checks if the last character in time parameter is an alphabetical letter
                        real_time = int(time[:-1]) #Just grabs all the characters until the last letter (only the numbers) and converts from str to int
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

                    #Muting the user
                    duration = f"{real_time} {time_prefix}"
                    await member.add_roles(role) #Adds the muted role to the user.
                    embed = disnake.Embed(title="Mute", description=f"{member.mention} has been tempmuted ", color= self.EMBED_COLOR)
                    embed.add_field(name="User muted:", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
                    embed.add_field(name="Action issued by:", value=f"**{ctx.author.display_name}**", inline=False)
                    embed.add_field(name="Reason:", value=f"`{reason}`", inline=False)
                    embed.add_field(name="Mute time: ", value=duration, inline=False)
                    await ctx.send(embed=embed) #Sends an embed of the mute in an aesthetic way

                    print(f"Player {member.display_name} has been muted for {real_time} {time_prefix}") #Checking if it works properly
                    db.mute_log(member.id, reason, duration, ctx.author.id)
                    await asyncio.sleep(time_muted) #Sleeps for the time period the staff member set for in seconds

                    await member.remove_roles(role) #Removes the "Muted" role from the user

                    #Unmuting the user
                    embed = disnake.Embed(title="Unmuted", color = self.EMBED_COLOR)
                    embed.add_field(name="User unmuted: ", value=f"**{member.display_name}** a.k.a **{member.name}**", inline=False)
                    embed.add_field(name="Time muted for: ", value=f"**{real_time} {time_prefix}**", inline=False)
                    await ctx.send(embed=embed)
                    if_mute_is_finished = True #Is now true so the while loop does not run a gain
                    created_role = True #Is now true so the created role block does not run as the "Muted" role exists now
                    for i in ctx.guild.text_channels:
                        await i.set_permissions(role, send_messages=False)

            if not created_role: #If created_role is still false, this means "Muted" role is still not created therefore it will create it here
                await ctx.guild.create_role(name="Muted", permissions=perms) #Creates the Muted role with send_messages perm set as False
                role = get(ctx.guild.roles, name="Muted")
                print(role)
                created_role = True
                for i in ctx.guild.text_channels:
                    await i.set_permissions(role, send_messages=False) 
                    #Makes sure so for every text channel, anyone with the role cannot send messages in text
                    #channels
                    
    @commands.slash_command(description="Purges an amount of messages from the text channel")
    async def clear(self, ctx, amount : int):
        await ctx.channel.purge(limit=int(amount + 1))
     
        
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