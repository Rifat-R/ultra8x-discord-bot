from time import time
from disnake.ext import commands
import disnake
from funcs import database as db, constants as const, funcs, serverconfig as conf
import sqlite3
import datetime
import math

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
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        
        company_name = db.get_company_name(user.id)
        
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
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        embed=disnake.Embed(title="Factory Products", description="Use `/factory set-production <factory-id> <product-id>` to produce an item.")
        products_dict = funcs.get_products_dict()
        for product_id in products_dict:
            product_info = products_dict[product_id]
            product_name = product_info["name"]
            product_price = product_info["price"]
            product_time = product_info["hours"]
            product_emoji = product_info["emoji"]
            embed.add_field(name=f"{product_emoji} {product_name} - £{product_price:,} / Item", value=f"> ID: {product_id}\n> Production: 1x every {product_time} hours", inline=False)
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


    @factory.sub_command(description="View all your running factories")
    async def view(self, inter:disnake.CommandInteraction):       
        user = inter.author
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        
        company_name = db.get_company_name(user.id)
        embed = disnake.Embed(title=f"Factories of {company_name}", description="Use `/factory set-production` to produce an item.\nTo buy a new factory use `/factory buy.`", color = const.EMBED_COLOUR)

        factories_dict = funcs.get_factories_dict()
        owned_factory_list = db.get_owned_factories(company_name)
        for factory_id in factories_dict:
            six_black_squares = ":black_large_square::black_large_square::black_large_square::black_large_square::black_large_square::black_large_square:"
            factory_info = factories_dict[factory_id]
            factory_name = factory_info["name"]
            factory_status = "Not unlocked yet."
            if factory_id in owned_factory_list:
                factory_status = "Factory standby"
                if db.check_if_has_running_factory(company_name, factory_id) is True:
                    six_black_squares = ":gear::gear::gear::gear::gear::gear:"
                    product_id = db.get_running_factory_product_id(company_name, factory_id)
                    products_dict = funcs.get_products_dict()
                    product_info = products_dict[product_id]
                    product_name = product_info["name"]
                    product_emoji = product_info["emoji"]
                    product_hours = product_info["hours"]
                    time_until_completion = product_hours * 6
                    db_until_completion_timestamp = db.get_running_factory_timestamp(company_name,factory_id)
                    timedelta_until_completion = db_until_completion_timestamp - datetime.datetime.now()
                    if str(timedelta_until_completion)[0] == "-":
                        factory_status = "Ready to collect :white_check_mark:"
                    else:
                        factory_status = f"in `{str(timedelta_until_completion)[:-7]}`"
                        
                    time_completed_so_far = (datetime.timedelta(hours=time_until_completion) - timedelta_until_completion).total_seconds()
                    
                    products_completed = math.floor(time_completed_so_far // (product_hours * 3600))
                    for _ in range(products_completed):
                        six_black_squares = six_black_squares.replace(":gear:",product_emoji,1)


            embed.add_field(name=f"{factory_name.capitalize()}", value = f"{six_black_squares}\n{factory_status}")


        embed.set_footer(text=f"Requested By: {user.name} | {user.id}")
        await inter.send(embed=embed)

    @factory.sub_command(description="Produce items from a factory", name= "set-production")
    async def set_production(self, inter:disnake.CommandInteraction, factory_id:str, product_id:str):
        user = inter.author
        factory_id = factory_id.lower()
        product_id = product_id.lower()
        
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        company_name = db.get_company_name(user.id)
        if funcs.check_if_factory_exists(factory_id) is False:
            await inter.send(f"That factory ID does not exist! Choose a factory from `/factory store`", ephemeral = True)
            return
        
        if funcs.check_if_product_exists(product_id) is False:
            await inter.send(f"That product ID does not exist! Choose a product from `/factory production`", ephemeral = True)
            return
        
        
        products_dict = funcs.get_products_dict()
        product_info = products_dict[product_id]
        product_name = product_info["name"]
        product_hours = product_info["hours"]
        product_seconds = product_hours * 3600
        time_until_completion = product_seconds * 6
        
        if db.check_if_has_factory(company_name, factory_id) is False:
            await inter.send(f"You do not own that factory! Buy one from `/factory store`", ephemeral = False)
            return
        
        if db.check_if_has_running_factory(company_name, factory_id) is True:
            until_completion_timestamp = db.get_running_factory_timestamp(company_name,factory_id)
            timestamp_until_completion = str(until_completion_timestamp - datetime.datetime.now())[:-7]
            if timestamp_until_completion[0] == "-":
                #If production is already completed
                await inter.send(f"Production in factory ID: `{factory_id}` has already been completed!", ephemeral = True)
                return
                
            await inter.send(f"You have something already running in this factory! Time until completion: `{timestamp_until_completion}`")
            return


        timestamp_until_completion = datetime.datetime.now() + datetime.timedelta(seconds = time_until_completion)
        db.add_running_factory(company_name, factory_id, product_id, timestamp_until_completion)
        await inter.send(f"Added product `{product_name}` to factory `{factory_id}` for company `{company_name}`")


    @factory.sub_command(description="Stop production that is happening in a factory", name= "stop-production")
    async def stop_production(self, inter:disnake.CommandInteraction, factory_id:str):
        user = inter.author
        factory_id = factory_id.lower()
        if funcs.check_if_factory_exists(factory_id) is False:
            await inter.send(f"That factory ID does not exist! Choose a factory from `/factory store`", ephemeral = True)
            return
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        company_name = db.get_company_name(user.id)
        if db.check_if_has_running_factory(company_name, factory_id) is False:
            await inter.send(f"You do not have a running factory to stop production!", ephemeral = True)
            return

        db.stop_running_factory(company_name, factory_id)
        await inter.send(f"You have stopped Factory `{factory_id}` from production")
               

    @factory.sub_command(description="Collect items that are ready from production")
    async def collect(self, inter:disnake.CommandInteraction, factory_id:str):
        user = inter.author
        if db.check_if_has_company(user.id) is False:
            await inter.send(f"You do not have a company. Buy one using `/company create`", ephemeral=True)
            return
        company_name = db.get_company_name(user.id)
        if funcs.check_if_factory_exists(factory_id) is False:
            await inter.send(f"That factory ID does not exist! Choose a factory from `/factory store`", ephemeral = True)
            return
        if db.check_if_has_factory(company_name, factory_id) is False:
            await inter.send(f"You do not own that factory! Buy one from `/factory store`", ephemeral = True)
            return
        if db.check_if_has_running_factory(company_name, factory_id) is False:
            await inter.send(f"That factory has not started production yet!", ephemeral = True)
            return


        product_id = db.get_running_factory_product_id(company_name, factory_id)
        products_dict = funcs.get_products_dict()
        product_info = products_dict[product_id]
        product_name = product_info["name"]
        product_emoji = product_info["emoji"]
        product_hours = product_info["hours"]
        time_until_completion = product_hours * 6
        db_until_completion_timestamp = db.get_running_factory_timestamp(company_name, factory_id)
        timedelta_until_completion = db_until_completion_timestamp - datetime.datetime.now()
        if str(timedelta_until_completion)[0] != "-":
            await inter.send(f"Factory ID `{factory_id}` is still producing products!", ephemeral = True)
            return
        
        db.company_inventory_add_product(company_name, product_id, 6)
        db.stop_running_factory(company_name, factory_id)
        await inter.send(f"You collected 6 {product_emoji}{product_name}'s! Added to company inventory")


def setup(bot):
    bot.add_cog(Factory(bot))
