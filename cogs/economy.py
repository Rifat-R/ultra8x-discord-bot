import disnake
from disnake.ext import commands
import random
import asyncio
from utils import database as db, constants as const

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Checks user economy balance") #The aliases in this decorator is made so people can also use "bal" as the command name. eg. .bal
    async def balance(self, ctx, user:disnake.Member = None): #user is defaulted as None if the user just want's to check their own balance.
        #The user can therefore check their own balance or someone elses. This is a polymorphic function.
        if user == None: #If the user input's no other user's id or their @.
            author = ctx.author #Variable contains the message sender user's instance object.
            pfp = author.display_avatar #The user's profile picture URL link

            em = disnake.Embed(title = f"{ctx.author.name}'s balance", color = disnake.Color.blue()) #Creates the embed instance object
            em.add_field(name = "Wallet balance:", value = f"**{db.wallet(ctx.author.id):,}**")
            em.add_field(name = "Bank balance:", value = f"**{db.bank(ctx.author.id):,}**" )
            em.set_thumbnail(url=pfp) #Sets the thumbnail of the embed as the user's profile picture.
            await ctx.send(embed = em) #Sends the embed in the text channel the command has been sent.
        else: #If the user does actually put a user ID or their @ in the parameter, the next block of code will happen instead.
            pfp = user.display_avatar #The profile picture of the user the sender mentioned.
            em = disnake.Embed(title = f"{user.name}'s balance", color = disnake.Color.blue())
            em.add_field(name = "Wallet balance:", value = f"**{db.wallet(user.id):,}**")
            em.add_field(name = "Bank balance:", value = f"**{db.bank(user.id):,}**" )
            em.set_thumbnail(url=pfp)
            await ctx.send(embed = em)

    @commands.slash_command(description="Give a user an amount of money")
    async def give(self, ctx, user:disnake.Member, amount):
        amount = int(amount) #All text is in string so therefore any number's need to be converted to integer to be 
        if amount > 0: #This is so the user cannot send negative values.
            if amount <= db.wallet(ctx.author.id): #If the amount of money they specified is less than or equal to the money they
                #have, then the transaction will go through
                db.deduct_wallet(ctx.author.id, amount) #Deducts the wallet of the user using the command
                db.update_wallet(user.id, amount) #Updates the wallet of the mentioned user
                await ctx.send(f"{ctx.author.mention} has paid {user.mention} **{amount:,}**.") #Sends message that
                #transaction has happened successfully in the text-channel the user has sent the command to.
            else:
                #If the user has less money than the amount entered in the parameter, the database transaction will not go through.
                await ctx.send(f"{ctx.author.mention} You don't have that much !" + 
                               f" You only have **{db.wallet(ctx.author.id):,}** in your wallet!")
                
        else:
            #This occurs if the user sends in negative values.
            await ctx.send(f"{ctx.author.mention} Please enter a **valid** value!")

    @commands.slash_command(description="Deposits money in your bank") #Alias is "dep" so users do not need to type out the entire command name to use this command.
    async def deposit(self, ctx, num):
        wallet_balance = db.wallet(ctx.author.id) #Wallet balance of the user.
        if num == "all": #num is the parameter they need to put an input in, so if it's "all", it should deposit all of it's wallet balance onto it's bank balance.
            if wallet_balance == 0: #If the wallet balance is 0, that means they do not have any money to deposit therefore the transaction should not happen
                await ctx.send(f"<@{ctx.author.id}> You do **not** have any funds to deposit!")
            else:
                db.update_bank(ctx.author.id,wallet_balance) #Add the wallet balance to the bank balance
                await ctx.send(f"<@{ctx.author.id}> You have deposited **{wallet_balance:,}**. " + 
                               f"Current wallet balance **{db.bank(ctx.author.id):,}**.")
                db.deduct_wallet(ctx.author.id,wallet_balance) #Remove the wallet balance from the wallet balance. This should be zero as we deposited all of our money.
        else:
            if num.isdecimal(): #Checks if the num variable is a positive integer (num from 0-9)
                num_int = int(num) #Converts variable into integer. 
                if num_int > wallet_balance: #Checks whether the amount of money deposited is greater than or equal to their wallet balance. 
                    #This is to prevent user's from inputting more than what they actually have.
                    #This code block will do nothing as if the number they input is greater than their balance, it will result in an error text message.
                    await ctx.send(f"<@{ctx.author.id}> You do not have the necessary funds to deposit.")			
                else:
                    #Else if the user actually put a number less than their wallet balance, then the transaction will occur normally.
                    db.update_bank(ctx.author.id, num_int)
                    db.deduct_wallet(ctx.author.id, num_int)
                    await ctx.send(f"<@{ctx.author.id}> You have deposited **{num_int:,}**. "
                                   +f"Current bank balance **{db.bank(ctx.author.id):,}**.")		
            else:
                await ctx.send(f"<@{ctx.author.id}> Please enter a valid number!") #Error if the user input is not a numerical value. This will also prevent
                #Users from entering negative numbers aswell as this checks if all the characters in the input is between 0-9.

    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")
    async def withdraw(self, ctx,num):
        bank_balance = db.bank(ctx.author.id)
        if num == "all": #If the user types in "all" in the amount of money parameter, then it will withdraw all money from bank balance.
            if bank_balance == 0: #If the user has no bank balance, It bot will send a text error why there was an error.
                await ctx.send(f"<@{ctx.author.id}> You do **not** have any funds to withdraw!")
            else: #Else the bot will function fine and the transaction will go through.
                db.update_wallet(ctx.author.id,bank_balance) #Add the bank balance to the wallet balance.
                await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{bank_balance:,}**. "+
                               f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")
                db.deduct_bank(ctx.author.id,bank_balance) #Deduct bank balnace with bank balance (should be zero at the end.)
        else:
            if num.isdecimal():
                amount_transferred = int(num)
                if amount_transferred > bank_balance:
                    await ctx.send(f"<@{ctx.author.id}> You can only **withdraw** **{bank_balance:,}** or less.")			
                else:
                    db.update_wallet(ctx.author.id, amount_transferred)
                    db.deduct_bank(ctx.author.id, amount_transferred)
                    await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{amount_transferred:,}**. "+
                                   f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")		
            else:
                await ctx.send(f"<@{ctx.author.id}> Please enter a valid **number**!")
                
                
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
        

    # @commands.slash_command(description="A ")
    # @commands.cooldown(1,40.0,type=commands.BucketType.user) #Cooldown decorator.
    # async def beg(self, ctx):
    #     money = random.randrange(0,100) #Random value from 0-100
    #     await ctx.send(f"<@{ctx.message.author.id}> A **kind stranger** has given you {const.BINGUSBOIN}**{money}**") #Message stating they recieved money
    #     db.update_wallet(ctx.author.id,money) #Adding the money generated from the random number generator.



    @commands.command()
    async def money(self, ctx):
        db.update_wallet(338764415358861314,1000000)
        #338764415358861314


    @daily.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): #Checks whether the error is the same as the cooldown error.
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 3600, 1)} hours.")
            
    @weekly.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): #Checks whether the error is the same as the cooldown error.
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 86400, 1)} days.")


def setup(bot):
    bot.add_cog(Economy(bot))

