from disnake.ext import commands
from disnake.ui import Button, View
import disnake
from funcs import database as db, pagination
import asyncio

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def ticket(self, ctx):
        pass

    @ticket.sub_command(description = "Create a ticket with a reason")
    async def create(self, inter:disnake.CommandInteraction, reason):
        user = inter.author
        if db.check_if_has_ticket(inter.author.id):
            await inter.send(f"You already have a ticket opened! Close that ticket to make a new one.", ephemeral = True)
            return
        
        guild = inter.guild
        await inter.send(f"You created a ticket support channel!", ephemeral = True)
        support = disnake.utils.get(guild.roles, name='support')
        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages = False),
            inter.author: disnake.PermissionOverwrite(read_messages=True),
            support: disnake.PermissionOverwrite(read_messages = True),
        }
        channel = await guild.create_text_channel(f"Ticket {inter.author.id}", overwrites=overwrites)
        db.add_ticket(user.id, channel.id, reason)

        close_ticket_button = Button(label="Close Ticket", style=disnake.ButtonStyle.danger)

        view = View()
        async def close_ticket_button_callback(interaction:disnake.CommandInteraction):
            if interaction.author.id != inter.author.id:
                await interaction.response.send_message(f"This is not your embed to use.", ephemeral = True)
                return
            
            await channel.set_permissions(support, send_messages = False, read_messages = True)
            await channel.set_permissions(inter.author, send_messages = False, read_messages = True)
            embed = disnake.Embed(title="Ticket Closed")
            embed.add_field(name = f"**Channel Name**", value = f"{channel.name}", inline = False)
            embed.add_field(name = f"**Creator**", value = f"{inter.author.name}#{inter.author.discriminator} | {inter.author.id}", inline = False)
            embed.add_field(name = f"**Closed by**", value = f"{interaction.author.name}#{interaction.author.discriminator}", inline = False)
            await interaction.response.send_message(embed=embed)
            close_ticket_button.disabled = True
            db.remove_ticket(user.id)

        close_ticket_button.callback = close_ticket_button_callback
        view.add_item(close_ticket_button)

        ticket_embed = disnake.Embed()
        ticket_embed.add_field(name = "**Reason**", value = f"{reason}")
        ticket_embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
        ticket_embed.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
        await channel.send(embed=ticket_embed, view=view)
        await asyncio.sleep(600)
        channel.delete()


    @ticket.sub_command(description = "Closes a ticket")
    async def close(self, inter:disnake.CommandInteraction):
        user = inter.author
        if db.check_if_has_ticket(user.id) is False:
            await inter.send(f"You do not have a ticket open currently")
            return
        
        if db.get_ticket_channel(user.id) != inter.channel.id:
            inter.send(f"You need to use this command in the ticket channel to close it.", ephemeral = True)
            return
        
        members = inter.channel.members
        for member in members:
            inter.channel.set_permissions(member, send_messsages = False, read_messages = True)
            
        embed = disnake.Embed(title="Ticket Closed")
        embed.add_field(name = f"**Channel Name**", value = f"{inter.channel.name}", inline = False)
        embed.add_field(name = f"**Creator**", value = f"{user.name}#{user.discriminator} | {user.id}", inline = False)
        embed.add_field(name = f"**Closed by**", value = f"{user.name}#{user.discriminator}", inline = False)
        await inter.send(embed=embed)
        db.remove_ticket(user.id)

    @ticket.sub_command(description="Shows all current open tickets", name = "list")
    async def _list(self, inter:disnake.CommandInteraction):
        user = inter.author
        ticket_description = ""
        embeds = []
        counter = 1
        ticket_list = db.get_ticket_list()
        divided_list = list(pagination.divide_list(ticket_list, 5))    #All infraction divided in lists of length 10 (so we can paginate)
        for ticket in divided_list:
            embed = disnake.Embed(title=f"Ticket list", description=ticket_description)
            embeds.append(embed)
            for row in ticket:
                #indexes represent location of column in row log table
                user_mention = row[0]
                channel_id = row[1]
                reason = row[2]
                date = row[3].strftime("%m/%d/%Y, %H:%M:%S")
                embed.add_field(name = f"{counter})" , value = f"User: `{user_mention}`\nTicket channel ID: `{channel_id}`\nReason: `{reason}`\nDate: `{date}`",inline=False)
                counter += 1
        if len(embeds) == 0:
            await inter.send(f"No one currently has a ticket open! ✅", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))

    # @ticket.sub_command(description = "Adds a user to the ticket channel")
    # async def add_user(self, inter:disnake.CommandInteraction, user:disnake.Member):
    #     inter.channel.set_permissions(user, send_messsages = True, read_messages = True)
    #     await inter.send(f"Added user {user.mention} to the ticket channel")


    # @ticket.sub_command(description = "Removes a user from the ticket channel")
    # async def remove_user(self, inter:disnake.CommandInteraction, user:disnake.Member):
    #     inter.channel.set_permissions(user, send_messsages = False, read_messages = False)
    #     await inter.send(f"Removed user {user.mention} from the ticket channel")
        
        
    
        



def setup(bot):
    bot.add_cog(Tickets(bot))
