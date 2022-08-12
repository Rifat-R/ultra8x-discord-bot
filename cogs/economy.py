import disnake
from disnake.ext import commands
from utils import database as db, constants as const

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Checks user economy balance") 
    async def balance(self, ctx, user:disnake.Member = None):
        if user is None:
            user = ctx.author
        wallet_balance = await db.wallet(user.id)
        bank_balance = await db.bank(user.id)

        pfp = user.display_avatar 
        em = disnake.Embed(title = f"{user.name}'s balance", color = disnake.Color.blue())
        em.add_field(name = "Wallet balance:", value = f"**{wallet_balance:,}**")
        em.add_field(name = "Bank balance:", value = f"**{bank_balance:,}**" )
        em.set_thumbnail(url=pfp)
        await ctx.send(embed = em)

    @commands.slash_command(description="Give a user an amount of money")
    async def give(self, ctx, user:disnake.Member, amount):
        wallet_balance = await db.wallet(user.id)
        amount = int(amount) 
        if amount > 0: 
            if amount <= wallet_balance: 
                
                db.deduct_wallet(ctx.author.id, amount) 
                db.update_wallet(user.id, amount) 
                await ctx.send(f"{ctx.author.mention} has paid {user.mention} **{amount:,}**.") 
                
            else:
                
                await ctx.send(f"{ctx.author.mention} You don't have that much !" + 
                               f" You only have **{db.wallet(ctx.author.id):,}** in your wallet!")
                
        else:
            
            await ctx.send(f"{ctx.author.mention} Please enter a **valid** value!")

    @commands.slash_command(description="Deposits money in your bank") 
    async def deposit(self, inter:disnake.CommandInteraction, num):
        wallet_balance = await db.wallet(inter.author.id)
        bank_balance = await db.bank(inter.author.id)
        if num == "all": 
            if wallet_balance == 0: 
                await inter.send(f"<@{inter.author.id}> You do **not** have any funds to deposit!")
            else:
                db.update_bank(inter.author.id, wallet_balance) 
                await inter.send(f"<@{inter.author.id}> You have deposited **{wallet_balance:,}**. " + 
                               f"Current wallet balance **{bank_balance:,}**.")
                db.deduct_wallet(inter.author.id,wallet_balance) 
        else:
            if num.isdecimal(): 
                num_int = int(num) 
                if num_int > wallet_balance: 
                    
                    
                    await inter.send(f"<@{inter.author.id}> You do not have the necessary funds to deposit.")			
                else:
                    
                    db.update_bank(inter.author.id, num_int)
                    db.deduct_wallet(inter.author.id, num_int)
                    await inter.send(f"<@{inter.author.id}> You have deposited **{num_int:,}**. "
                                   +f"Current bank balance **{bank_balance:,}**.")		
            else:
                await inter.send(f"<@{inter.author.id}> Please enter a valid number!") 
                

    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")
    async def withdraw(self, inter,num):
        wallet_balance = await db.wallet(inter.author.id)
        bank_balance = await db.bank(inter.author.id)
        if num == "all": 
            if bank_balance == 0: 
                await inter.send(f"<@{inter.author.id}> You do **not** have any funds to withdraw!")
            else: 
                db.update_wallet(inter.author.id,bank_balance) 
                await inter.send(f"<@{inter.author.id}> You have withdrawn **{bank_balance:,}**. "+
                               f"Current wallet balance **{wallet_balance:,}**.")
                db.deduct_bank(inter.author.id,bank_balance) 
        else:
            if num.isdecimal():
                amount_transferred = int(num)
                if amount_transferred > bank_balance:
                    await inter.send(f"<@{inter.author.id}> You can only **withdraw** **{bank_balance:,}** or less.")			
                else:
                    db.update_wallet(inter.author.id, amount_transferred)
                    db.deduct_bank(inter.author.id, amount_transferred)
                    await inter.send(f"<@{inter.author.id}> You have withdrawn **{amount_transferred:,}**. "+
                                   f"Current wallet balance **{wallet_balance:,}**.")		
            else:
                await inter.send(f"<@{inter.author.id}> Please enter a valid **number**!")
                
                
    @commands.slash_command()
    @commands.cooldown(1,86400,type=commands.BucketType.user)
    async def daily(self, ctx):
        AMOUNT = 5000
        await db.update_wallet(ctx.author.id, AMOUNT)
        await ctx.send(f"You claimed your daily and recieved **{AMOUNT}** Cash!")
        
    @commands.slash_command()
    @commands.cooldown(1,604800,type=commands.BucketType.user)
    async def weekly(self, ctx):
        AMOUNT = 25000
        await db.update_wallet(ctx.author.id, AMOUNT)
        await ctx.send(f"You claimed your weekly and recieved **{AMOUNT}** Cash!")
        

    
    
    
    
    
    



    @commands.command()
    async def money(self, ctx):
        print("Gave money to Anom4ly")
        await db.update_wallet(338764415358861314,1000000)
        


    @daily.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 3600, 1)} hours.")
            
    @weekly.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 86400, 1)} days.")


def setup(bot):
    bot.add_cog(Economy(bot))

