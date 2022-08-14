import disnake
from disnake.ext import commands
import random
import asyncio
from utils import database as db, constants as const, blackjack

class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Checks user economy balance") 
    async def balance(self, inter:disnake.CommandInteraction, user:disnake.Member = None):
        if user is None:
            user = inter.author

        pfp = user.display_avatar 
        em = disnake.Embed(title = f"{user.name}'s balance", color = disnake.Color.blue())
        em.add_field(name = "Wallet balance:", value = f"**{db.wallet(user.id):,}**")
        em.add_field(name = "Bank balance:", value = f"**{db.bank(user.id):,}**" )
        em.set_thumbnail(url=pfp)
        await inter.send(embed = em)

    @commands.slash_command(description="Give a user an amount of money")
    async def give(self, inter:disnake.CommandInteraction, user:disnake.Member, amount):
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

    @commands.slash_command(description="Deposits money in your bank") 
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
                

    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")
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
        
    
        bj = blackjack.blackjack(inter, self.bot.user.name, bet)
        
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

