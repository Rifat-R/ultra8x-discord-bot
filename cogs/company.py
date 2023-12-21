from disnake.ext import commands
import disnake
from funcs import database as db, funcs, serverconfig as conf, pagination
import sqlite3
from settings import constants as const

class Company(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.slash_command()
    async def company(self, inter):
        pass  
        
    @company.sub_command(description="Create a company")
    async def create(self, inter:disnake.CommandInteraction, company_name:str):
        company_name = company_name.lower()
        user = inter.author
        try:
            db.create_company(company_name, user.id)
        except sqlite3.IntegrityError:
            company_name = db.get_company_name(user.id)
            await inter.send(f"You already have a company called `{company_name}`", ephemeral = True)
            return

        await inter.send(f"Created company `{company_name}`")

    @company.sub_command(description="Delete your company")
    async def delete(self, inter:disnake.CommandInteraction):
        user = inter.author
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You don't have a company!", ephemeral = True)
            return
        company_name = db.get_company_name(user.id)
        
        db.delete_company(company_name)
        await inter.send(f"Deleted company `{company_name}`")
        
    @company.sub_command(description="View your company inventory")
    async def inventory(self, inter:disnake.CommandInteraction):
        user = inter.author
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        company_name = db.get_company_name(user.id)
        inventory_string = ""
        embeds = []
        company_inventory_list = db.get_company_inventory_list(company_name)
        counter = 1
        divided_inventory_list = list(pagination.divide_list(company_inventory_list, 5))  # All infraction divided in lists of length 5 (so we can paginate)

        for company_inventory in divided_inventory_list:
            embed = disnake.Embed(title=f"Company inventory", description=inventory_string, color=const.EMBED_COLOUR)
            embeds.append(embed)
            for row in company_inventory:
                # indexes represent location of column in row log table
                product_id = row[0]
                product_info = funcs.get_products_dict()[product_id]
                product_name = product_info["name"]
                product_price = product_info["price"]
                product_emoji = product_info["emoji"]

                count = row[1]
                embed.add_field(name=f"{counter}. {product_emoji} {product_name}", value=f"Count : {count}x", inline=False)
                counter += 1

        if len(embeds) == 0:
            await inter.send(f"{const.CROSS_EMOJI} No one in this server has been registered to the bot. Start by creating your account with /create", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))
            
    @company.sub_command(description="Get more info about a company")
    async def info(self, inter:disnake.CommandInteraction, company_name:str = None):
        user = inter.author
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        if company_name is None:
            company_name = db.get_company_name(user.id)
        else:
            company_name = company_name.lower()
        created_at = str(db.get_company_created_at(company_name))[:-7]
        company_founder = db.get_company_founder_author(company_name)
        company_networth = db.get_company_networth(company_name)
        amount_of_employees = db.get_number_of_employees(company_name)
            
        embed = disnake.Embed(title = f"Information about {company_name}", description = "To check company inventory use `/company inventory`", color = const.EMBED_COLOUR)
        embed.add_field(name = "Company Founder: ", value = f"`{company_founder}`", inline = False)
        embed.add_field(name = "Created at: ", value = f"`{created_at}`", inline = False)
        embed.add_field(name = f"Company networth: ", value = f"`£{company_networth:,}`", inline = False)
        embed.add_field(name = f"Number of employees: ", value = f"`{amount_of_employees}`", inline = False)
        embed.set_footer(text=f"Requested By: {user.name} | {user.id}")
        print(db.get_company_networth(company_name))
        await inter.send(embed=embed)


def setup(bot):
    bot.add_cog(Company(bot))
