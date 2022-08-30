from disnake.ext import commands
import disnake
from utils import database as db, constants as const, funcs, serverconfig as conf
import sqlite3
import math
import random

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
        



def setup(bot):
    bot.add_cog(Company(bot))
