import disnake
from disnake.ext import commands
import random
import asyncio
from utils import database as db, constants as const, blackjack

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Checks user economy balance") 
    async def balance(self, ctx, user:disnake.Member = None):
        if user is None:
            user = ctx.author

        pfp = user.display_avatar 
        em = disnake.Embed(title = f"{user.name}'s balance", color = disnake.Color.blue())
        em.add_field(name = "Wallet balance:", value = f"**{db.wallet(user.id):,}**")
        em.add_field(name = "Bank balance:", value = f"**{db.bank(user.id):,}**" )
        em.set_thumbnail(url=pfp)
        await ctx.send(embed = em)

    @commands.slash_command(description="Give a user an amount of money")
    async def give(self, ctx, user:disnake.Member, amount):
        amount = int(amount) 
        if amount > 0: 
            if amount <= db.wallet(ctx.author.id): 
                db.deduct_wallet(ctx.author.id, amount) 
                db.update_wallet(user.id, amount) 
                await ctx.send(f"{ctx.author.mention} has paid {user.mention} **{amount:,}**.") 
            else:
                await ctx.send(f"{ctx.author.mention} You don't have that much ! You only have **{db.wallet(ctx.author.id):,}** in your wallet!")
        else:
            await ctx.send(f"{ctx.author.mention} Please enter a **valid** value!")

    @commands.slash_command(description="Deposits money in your bank") 
    async def deposit(self, ctx, num):
        wallet_balance = db.wallet(ctx.author.id) 
        if num == "all": 
            if wallet_balance == 0: 
                await ctx.send(f"<@{ctx.author.id}> You do **not** have any funds to deposit!")
            else:
                db.update_bank(ctx.author.id,wallet_balance) 
                await ctx.send(f"<@{ctx.author.id}> You have deposited **{wallet_balance:,}**. " + 
                               f"Current wallet balance **{db.bank(ctx.author.id):,}**.")
                db.deduct_wallet(ctx.author.id,wallet_balance) 
        else:
            if num.isdecimal(): 
                num_int = int(num) 
                if num_int > wallet_balance: 
                    await ctx.send(f"<@{ctx.author.id}> You do not have the necessary funds to deposit.")			
                else:
                    
                    db.update_bank(ctx.author.id, num_int)
                    db.deduct_wallet(ctx.author.id, num_int)
                    await ctx.send(f"<@{ctx.author.id}> You have deposited **{num_int:,}**. "
                                   +f"Current bank balance **{db.bank(ctx.author.id):,}**.")		
            else:
                await ctx.send(f"<@{ctx.author.id}> Please enter a valid number!") 
                

    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")
    async def withdraw(self, ctx,num):
        bank_balance = db.bank(ctx.author.id)
        if num == "all": 
            if bank_balance == 0: 
                await ctx.send(f"<@{ctx.author.id}> You do **not** have any funds to withdraw!")
            else: 
                db.update_wallet(ctx.author.id,bank_balance) 
                await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{bank_balance:,}**. "+
                               f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")
                db.deduct_bank(ctx.author.id,bank_balance) 
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
                
                
    @commands.slash_command(description="Blackjack game")
    async def blackjack(self, inter:disnake.CommandInteraction):
        user = inter.author
        bj = blackjack.blackjack(inter, self.bot.user.name)
        
        embed = bj.gen_embed(user, self.bot.user.name, bj.user_cards, bj.bot_cards)

        await inter.send(embed=embed,view=bj)
    
    @commands.command()
    async def test(self, ctx):
        embed = disnake.Embed()
        embed.set_author(name="test", value="[asdsad](https://google.com)")
        await ctx.send(embed=embed)
        
                
                
    @commands.slash_command(description="Work for money. One hour cooldown")
    @commands.cooldown(1,3600,type=commands.BucketType.user)
    async def work(self, inter:disnake.CommandInteraction):
        amount_of_money = 5000
        db.update_wallet(inter.author.id, amount_of_money)
        await inter.send(f"You worked and gained **{amount_of_money}**. Enjoy!", ephemeral=True)
                
                
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
        

    
    
    
    
    
    



    @commands.command()
    async def money(self, ctx):
        db.update_wallet(338764415358861314,1000000)
        

#Error handlers

    @daily.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 3600, 1)} hours.", ephemeral=True)
            
    @weekly.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 86400, 1)} days.", ephemeral=True)
            
    @work.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the beg command."""
        if isinstance(error, commands.CommandOnCooldown): 
            await ctx.send(f"This command is on cooldown. Please try again after {round(error.retry_after / 60, 1)} minutes.", ephemeral=True)


def setup(bot):
    bot.add_cog(Economy(bot))

