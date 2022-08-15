import disnake
from disnake.ext import commands
from utils import database as db, blackjack, pagination, funcs, constants as const
import sqlite3
import random

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(description="Checks user economy balance") 
    async def balance(self, inter:disnake.CommandInteraction, user:disnake.Member = None):                              # Balance Command
        """
        Buy an item from the shop
        Parameters
        ----------
        user: The user you want to check the balance of.
        """
        if user is None:
            user = inter.author

        pfp = user.display_avatar 
        em = disnake.Embed(color = const.EMBED_COLOUR)   #title = f"{user.name}'s Balance",
        em.add_field(name = "💵 __Cash__     ", value = f"**{db.wallet(user.id):,}**")
        em.add_field(name = "💳 __Bank__     ", value = f"**{db.bank(user.id):,}**" )
        em.add_field(name = "🏦 __Total__     ", value = f"**{db.wallet(user.id) + db.bank(user.id):,}**")
        em.set_author(name = f"{user.name}'s Balance", icon_url = pfp)
        em.set_thumbnail(url = pfp)
        em.set_footer(text=f"Requested By: {user.name} | {user.id}")
        await inter.send(embed = em)


    @commands.slash_command(description="Transfer an amount of money to a user")                                        # Transfer Command
    async def transfer(self, inter:disnake.CommandInteraction, user:disnake.Member, amount):
        """
        Buy an item from the shop
        Parameters
        ----------
        user: The user you want send money to.
        """
        amount = int(amount) 
        if amount > 0: 
            if amount <= db.wallet(inter.author.id): 
                db.deduct_wallet(inter.author.id, amount)
                db.update_wallet(user.id, amount) 
                await inter.send(f"{inter.author.mention} has paid {user.mention} **{amount:,}**.") 
            else:
                await inter.send(f"{inter.author.mention} You don't have that much ! You only have **{db.wallet(inter.author.id):,}** in your wallet!")
        else:
            await inter.send(f"{inter.author.mention} Please enter a **valid** value!")

    @commands.slash_command(description="Deposits money in your bank")                                                  # Deposit Command
    async def deposit(self, inter:disnake.CommandInteraction, amount):
        """
        Deposit money from your wallet balance
        Parameters
        ----------
        amount: The amount of money you want to deposit. Can also type 'all' to deposit all money from wallet.
        """
        wallet_balance = db.wallet(inter.author.id) 
        if amount == "all": 
            if wallet_balance == 0: 
                await inter.send(f"<@{inter.author.id}> You do **not** have any funds to deposit!")
            else:
                db.update_bank(inter.author.id,wallet_balance) 
                await inter.send(f"<@{inter.author.id}> You have deposited **{wallet_balance:,}**. " + 
                               f"Current wallet balance **{db.bank(inter.author.id):,}**.")
                db.deduct_wallet(inter.author.id,wallet_balance) 
        else:
            if amount.isdecimal(): 
                amount_int = int(amount) 
                if amount_int > wallet_balance: 
                    await inter.send(f"<@{inter.author.id}> You do not have the necessary funds to deposit.")			
                else:
                    
                    db.update_bank(inter.author.id, amount_int)
                    db.deduct_wallet(inter.author.id, amount_int)
                    await inter.send(f"<@{inter.author.id}> You have deposited **{amount_int:,}**. "
                                   +f"Current bank balance **{db.bank(inter.author.id):,}**.")		
            else:
                await inter.send(f"<@{inter.author.id}> Please enter a valid number!") 
                

    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")                          # Withdraw Command
    async def withdraw(self, ctx, amount):
        """
        Withdraw money from your bank balance
        Parameters
        ----------
        amount: The amount of money you want to withdraw. Can also type 'all' to withdraw all money from bank.
        """
        bank_balance = db.bank(ctx.author.id)
        if amount == "all": 
            if bank_balance == 0: 
                await ctx.send(f"<@{ctx.author.id}> You do **not** have any funds to withdraw!")
            else: 
                db.update_wallet(ctx.author.id,bank_balance) 
                await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{bank_balance:,}**. "+
                               f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")
                db.deduct_bank(ctx.author.id,bank_balance) 
        else:
            if amount.isdecimal():
                amount_transferred = int(amount)
                if amount_transferred > bank_balance:
                    await ctx.send(f"<@{ctx.author.id}> You can only **withdraw** **{bank_balance:,}** or less.")			
                else:
                    db.update_wallet(ctx.author.id, amount_transferred)
                    db.deduct_bank(ctx.author.id, amount_transferred)
                    await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{amount_transferred:,}**. "+
                                   f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")		
            else:
                await ctx.send(f"<@{ctx.author.id}> Please enter a valid **number**!")
                
                
    @commands.slash_command(description="Get top 10 richest players")                                                   # Rich (Leaderboard) Command
    async def rich(self, inter:disnake.CommandInteraction):
        leaderboard_string = ""
        embeds = []
        leaderboard_list = db.get_rich_leaderboard()
        counter = 1
        divived_leaderboard_list = list(pagination.divide_list(leaderboard_list, 5)) #All infraction divided in lists of length 5 (so we can paginate)
        for leaderboard in divived_leaderboard_list:
            embed = disnake.Embed(title=f"Economy Leaderboard", description=leaderboard_string, color = const.EMBED_COLOUR)
            embeds.append(embed)
            for row in leaderboard:
                #indexes represent location of column in row log table
                user_mention = f"`{row[0]}`"
                networth = row[1]
                embed.add_field(name = f"{counter}. {user_mention}", value = f"Networth: `{networth:,}`\n", inline = True)
                counter += 1
        if len(embeds) == 0:
            await inter.send(f"No one in this server has been registered to the bot. Start by typing in chat.✅", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))
            
            
            
    @commands.slash_command(description="Buy an item from the shop")                                                    # Buy Command
    async def buy(self, inter:disnake.CommandInteraction, item_name):
        """
        Buy an item from the shop
        Parameters
        ----------
        item_name: The name of the item you want to buy.
        """
        user = inter.author
        item_name = item_name.lower()
        item_price = funcs.get_item_buy_price(item_name)
        wallet_balance = db.wallet(user.id)
        if wallet_balance < item_price:
            await inter.send(f"You don't have enough money to buy this item!", ephemeral=True)
            return
        
        try:
            db.buy_item(user.id, item_name)
        except(sqlite3.IntegrityError):
            await inter.send(f"You already have that item in your inventory!", ephemeral=True)
            return
            
        await inter.send(f"You have bought `{item_name}` for **{item_price}**.")
        
    @commands.slash_command(description="Sell an item from your inventory")
    async def sell(self, inter:disnake.CommandInteraction, item_name):
        """
        Sell an item from your inventory
        Parameters
        ----------
        item_name: The name of the item you want to sell.
        """
        item_name = item_name.lower()
        user = inter.author
        
        if len(db.get_item(user.id, item_name)) == 0:
            await inter.send(f"You do not have that item in your inventory!", ephemeral=True)
            return
        db.sell_item(inter.author.id, item_name)
        await inter.send(f"You have sold `{item_name}` for **{funcs.get_item_sell_price(item_name)}**.")
        
        
    @commands.slash_command(description = "Shows your inventory")
    async def inventory(self, inter:disnake.CommandInteraction):
        user = inter.author
        inventory_string = ""
        embeds = []
        inventory_list = db.get_user_inventory(user.id)
        counter = 1
        divided_inventory_list = list(pagination.divide_list(inventory_list, 5)) #All infraction divided in lists of length 5 (so we can paginate)
        for inventory in divided_inventory_list:
            for row in inventory:
                item = f"{row[1]}"
                inventory_string += f"• `{item.capitalize()}`\n"
                counter += 1
            embed = disnake.Embed(title=f"Economy inventory", description=inventory_string, color = const.EMBED_COLOUR)
            embeds.append(embed)
        if len(embeds) == 0:
            await inter.send(f"You have no items in your inventory! Start by looking at the shop!", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))
            
    @commands.has_role(const.ADMIN_ROLE)
    @commands.slash_command(description = "Give user money")
    async def give(self, inter:disnake.CommandInteraction, amount:int, user:disnake.Member, location:str):
        """
        Give a user a sum of money in their wallet or bank
        Parameters
        ----------
        amount: Amount of money you want to give the user
        user: The user you want to give money to
        location: The location where you want to give money to. Must be either "wallet" or "bank". 
        """
        location = location.lower()
        if location != "wallet" and location != "bank":
            await inter.send("You must specify location as either `wallet` or `bank`.", ephemeral = True)
            return
        if location == "wallet":
            db.update_wallet(user.id, amount)
        if location == "bank":
            db.update_bank(user.id, amount)
        
        await inter.send(f"Gave **{amount:,}** to {user.mention}'s {location}", ephemeral=True)


    @commands.has_role(const.ADMIN_ROLE)
    @commands.slash_command(description = "Give user money")
    async def take(self, inter:disnake.CommandInteraction, amount:int, user:disnake.Member, location:str):
        """
        Take a sum of money from a user either from their wallet or bank
        Parameters
        ----------
        amount: Amount of money you want to take from the user
        user: The user you want to take money from
        location: The location where you want to take money from. Must be either "wallet" or "bank". 
        """
        location = location.lower()
        if location != "wallet" and location != "bank":
            await inter.send("You must specify location as either `wallet` or `bank`.", ephemeral = True)
            return
        if location == "wallet":
            db.deduct_wallet(user.id, amount)
        if location == "bank":
            db.deduct_bank(user.id, amount)
        
        await inter.send(f"Took **{amount:,}** from {user.mention}'s {location}", ephemeral=True)
        
        
                

                
    @commands.slash_command(description="Blackjack game")
    async def blackjack(self, inter:disnake.CommandInteraction, bet:int):
        """
        Game
        Parameters
        ----------
        bet: The amount of money you want to bet. Must be atleast 500
        """
        user = inter.author
        wallet_balance = db.wallet(user.id)
        if bet < 500:
            await inter.send("You must bet atleast 500", ephemeral=True)
            return
        if wallet_balance < bet:
            await inter.send(f"You do not have {bet} in your wallet!", ephemeral=True)
            return
        
        db.deduct_wallet(user.id, bet)
        bj = blackjack.blackjack(inter, self.bot.user.name, bet)
        description = f"You are now betting **{bet:,}**"
        
        embed = bj.gen_embed(user, self.bot.user.name, bj.user_cards, bj.bot_cards, description=description)

        await inter.send(embed=embed,view=bj)
        
    @commands.slash_command(description="Shop where you can buy products")
    async def shop(self, inter:disnake.CommandInteraction):
        embeds = funcs.gen_shop_embed()
        await inter.send(embed=embeds[0], view=pagination.Menu(embeds))
    
                
    @commands.slash_command(description="Work for money. One hour cooldown")
    @commands.cooldown(1,3600,type=commands.BucketType.user)
    async def work(self, inter:disnake.CommandInteraction):
        amount_of_money = random.randint(250, 5000)
        db.update_wallet(inter.author.id, amount_of_money)
        await inter.send(f"You worked and gained **{amount_of_money}**. Enjoy!", ephemeral=False)
                
                
    @commands.slash_command()
    @commands.cooldown(1,86400,type=commands.BucketType.user)
    async def daily(self, ctx):
        AMOUNT = 5000
        db.update_wallet(ctx.author.id, AMOUNT)
        await ctx.send(f"You claimed your daily and recieved **{AMOUNT}** Cash!")
        
    @commands.slash_command()
    @commands.cooldown(1,604800,type=commands.BucketType.user)
    async def weekly(self, ctx):
        AMOUNT = 25000
        db.update_wallet(ctx.author.id, AMOUNT)
        await ctx.send(f"You claimed your weekly and recieved **{AMOUNT}** Cash!")
        

#Testing purposes (The id is Anom4ly's)

    # @commands.command()
    # async def money(self, ctx):
    #     db.update_wallet(338764415358861314,1000000)
        

#Error handlers

    @daily.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the daily command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 3600, 1)} hours.", ephemeral=True)
            
    @weekly.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the weekly command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 86400, 1)} days.", ephemeral=True)
            
    @work.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the work command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 60, 1)} minutes.", ephemeral=True)


    @give.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingRole): 
            await ctx.send(f"You do not have the `{error.missing_role}` command to use this command", ephemeral = True)
            
    @give.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingRole): 
            await ctx.send(f"You do not have the `{error.missing_role}` command to use this command", ephemeral = True)

def setup(bot):
    bot.add_cog(Economy(bot))

