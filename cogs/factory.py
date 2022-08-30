from disnake.ext import commands
import disnake
from utils import database as db, constants as const, funcs, serverconfig as conf
import sqlite3
import math
import random

class Factory(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @commands.slash_command()
    async def factory(self, inter):
        pass
    
    @factory.sub_command(description="Shows the factory store")
    async def store(self, inter:disnake.CommandInteraction):
        user = inter.author
        wallet_balance = db.wallet(user.id)
        try:
            company_name = db.get_company_name(user.id)
        except sqlite3.IntegrityError:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        
        embed=disnake.Embed(title=f"Factories of {company_name}", description=f"To buy a new factory use /factory buy <id>")
        factories_dict = funcs.get_factories_dict()
        for factory_id in factories_dict:
            
            factory_info = factories_dict[factory_id]
            factory_name = factory_info["name"]
            factory_price = factory_info["price"]
            lock_emoji = ":lock:"
            if wallet_balance >= factory_price:
                lock_emoji = ":unlock:"
            embed.add_field(name=f"{lock_emoji}{factory_name}", value=f"Cost: **{factory_price:,}**", inline=True)
        embed.set_footer(text=f"Requested By: {user.name} | {user.id}")
        await inter.send(embed=embed)
        
        
    @factory.sub_command(description="Show products you can produce at a factory")
    async def production(self, inter:disnake.CommandInteraction):
        user = inter.author
        try:
            company_name = db.get_company_name(user.id)
        except sqlite3.IntegrityError:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        embed=disnake.Embed(title="Factory Products", description="Use `/factory set-production <factory-id> <product-id>` to produce an item.")
        products_dict = funcs.get_products_dict()
        for product_name in products_dict:
            product_info = products_dict[product_name]
            product_price = product_info["price"]
            product_time = product_info["hours"]
            product_emoji = product_info["emoji"]
            product_name = product_name.capitalize()
            embed.add_field(name=f"{product_emoji} {product_name} - £{product_price:,} / Item", value=f"> ID: {product_name.lower()}\n> Production: 1x every {product_time} hours", inline=False)
        embed.set_footer(text=f"Requested By: {user.name} | {user.id}")
        await inter.send(embed=embed)
      
    @factory.sub_command(description="Buy a factory from /factory store")
    async def buy(self, inter:disnake.CommandInteraction, factory_id:str):  
        factory_id = factory_id.lower()
        user = inter.author
        wallet_balance = db.wallet(user.id)
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        if funcs.check_if_factory_exists(factory_id) is False:
            await inter.send(f"That factory ID does not exist! Choose a factory from `/factory store`", ephemeral = True)
            return
        
        company_name = db.get_company_name(user.id)
        try:
            db.add_factory(company_name, factory_id)
        except sqlite3.IntegrityError:
            await inter.send(f"You already have that factory!", ephemeral = True)
            return
        factory_price = funcs.get_factory_price(factory_id)
        if wallet_balance < factory_price:
            await inter.send(f"You do not have enough money in your wallet to buy this factory.", ephemeral=True)
            return
        db.deduct_wallet(user.id, factory_price)
        await inter.send(f"You bought a Factory with the ID: `{factory_id}` Price: `{factory_price:,}`")
    
            

            



def setup(bot):
    bot.add_cog(Factory(bot))
