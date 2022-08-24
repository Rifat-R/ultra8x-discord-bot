from pydoc import describe
import disnake
from disnake.ext import commands
import datetime
from utils import database as db, blackjack, pagination, funcs, constants as const
import sqlite3
import random


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.slash_command(description="Creates an account so you can use the bot!")
    async def start(self, inter: disnake.CommandInteraction):
        try:
            user = inter.author
            db.create(user.id, str(user))
            print(f"User {user.id} has been created and stored in user_data table.")
            await inter.send(f"You have successfully created an account with this bot!", ephemeral = True)
        except sqlite3.IntegrityError:
            await inter.send(f"You already created an account!", ephemeral = True)
        
    
# BALANCE COMMAND
    @commands.slash_command(description="Get the balance amount of anyone in the server")
    async def balance(self, inter: disnake.CommandInteraction, user: disnake.Member = None):

        if user is None:
            user = inter.author

        if db.check_user(user.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        rank = db.get_rich_rank(user.id)
        rank = funcs.convert_to_ordinal(rank)

        em = disnake.Embed(description=f"Leaderboard Rank: {rank}") #title=f"{user.name}'s Balance", color=const.EMBED_COLOUR
        em.set_author(name=f"{inter.author.name}'s Balance", icon_url=inter.author.display_avatar)
        em.add_field(name="💵 __Cash__     ", value=f"£**{db.wallet(user.id):,}**")
        em.add_field(name="💳 __Bank__     ", value=f"£**{db.bank(user.id):,}**")
        em.add_field(name="🏦 __Total__     ", value=f"£**{db.wallet(user.id) + db.bank(user.id):,}**")
        em.set_thumbnail(url=user.display_avatar)
        em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
        await inter.send(embed=em)

# TRANSFER COMMAND
    @commands.slash_command(description="Transfer an amount of money to a user")
    async def transfer(self, inter: disnake.CommandInteraction, user: disnake.Member, amount):
        """
        Transfer an amount of money to a user.
        ----------
        user: The user you want send money to.
        """
        if db.check_user(inter.author.id) is False or db.check_user(user.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        amount = int(amount)
        if amount > 0:
            if amount <= db.wallet(inter.author.id):
                db.deduct_wallet(inter.author.id, amount)
                db.update_wallet(user.id, amount)

                em = disnake.Embed(title="Transferring Money", description=" ")
                em.set_author(name=f"{inter.author.name}", url=inter.author.display_avatar)
                em.add_field(name="From:", value=f"{inter.author.mention}", inline=True)
                em.add_field(name="->", value=f"£{amount:,}", inline=True)
                em.add_field(name="To:", value=f"{user.mention}", inline=True)
                em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")

                await inter.send(embed=em)
            else:
                await inter.send(f"{inter.author.mention} You don't have that much ! You only have £**{db.wallet(inter.author.id):,}** in your wallet!")
        else:
            await inter.send(f"{inter.author.mention} Please enter a **valid** value!")

# DEPOSIT COMMAND
    @commands.slash_command(description="Deposits money in your bank")
    async def deposit(self, inter: disnake.CommandInteraction, amount):
        """
        Deposit money from your cash balance
        Parameters
        ----------
        amount: The amount of money you want to deposit. Can also type 'all' to deposit all money from wallet.
        """
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        wallet_balance = db.wallet(inter.author.id)

        if amount == "all":
            if wallet_balance == 0:
                await inter.send(f"{inter.author.mention} You do **not** have any funds to deposit!")
            else:
                db.update_bank(inter.author.id, wallet_balance)
                em = disnake.Embed(description=f"{const.TICK_EMOJI} Deposited £{wallet_balance:,} to your bank!")
                em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                await inter.send(embed=em)
                #await inter.send(f"<@{inter.author.id}> You have deposited **{wallet_balance:,}**. " + f"Current wallet balance **{db.bank(inter.author.id):,}**.")
                db.deduct_wallet(inter.author.id, wallet_balance)
        else:
            if amount.isdecimal():
                amount_int = int(amount)
                if amount_int > wallet_balance:
                    em = disnake.Embed(description=f"{const.CROSS_EMOJI} You don't have that much money to deposit. You currently have £{wallet_balance:,}.")
                    em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                    em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                    await inter.send(embed=em)
                    #await inter.send(f"<@{inter.author.id}> You do not have the necessary funds to deposit.")
                else:
                    db.update_bank(inter.author.id, amount_int)
                    db.deduct_wallet(inter.author.id, amount_int)
                    em = disnake.Embed(description=f"{const.TICK_EMOJI} Deposited £{amount_int:,} to your bank!")
                    em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                    em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                    await inter.send(embed=em)
                    #await inter.send(f"<@{inter.author.id}> You have deposited **{amount_int:,}**. " + f"Current bank balance **{db.bank(inter.author.id):,}**.")
            else:
                await inter.send(f"<@{inter.author.id}> Please enter a valid number!")

# WITHDRAW COMMAND
    @commands.slash_command(description="Withdraws money from bank balance to wallet balance")
    async def withdraw(self, inter: disnake.CommandInteraction, amount):
        """
        Withdraw money from your bank balance
        Parameters
        ----------
        amount: The amount of money you want to withdraw. Can also type 'all' to withdraw all money from bank.
        """
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        bank_balance = db.bank(inter.author.id)
        if amount == "all":
            if bank_balance == 0:
                await inter.send(f"<@{inter.author.id}> You do **not** have any money to withdraw!")
            else:
                db.update_wallet(inter.author.id, bank_balance)
                em = disnake.Embed(description=f"{const.TICK_EMOJI} Withdrew £{bank_balance:,} from your bank!")
                em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                await inter.send(embed=em)
                #await ctx.send(f"<@{ctx.author.id}> You have withdrawn **{bank_balance:,}**. " + f"Current wallet balance **{db.wallet(ctx.author.id):,}**.")
                db.deduct_bank(inter.author.id, bank_balance)
        else:
            if amount.isdecimal():
                amount_transferred = int(amount)
                if amount_transferred > bank_balance:
                    em = disnake.Embed(description=f"{const.CROSS_EMOJI} You don't have that much money to withdraw. You currently have £{bank_balance:,} in the bank.")
                    em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                    em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                    await inter.send(embed=em)
                    #await inter.send(f"<@{inter.author.id}> You can only **withdraw** **{bank_balance:,}** or less.")
                else:
                    db.update_wallet(inter.author.id, amount_transferred)
                    db.deduct_bank(inter.author.id, amount_transferred)
                    em = disnake.Embed(description=f"{const.TICK_EMOJI} Withdrew £{amount_transferred:,} from your bank! Current balance: £{db.bank(inter.author.id):,}")
                    em.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
                    em.set_footer(text=f"Requested By: {inter.author.name} | {inter.user.id}")
                    await inter.send(embed=em)
                    #await inter.send(f"<@{inter.author.id}> You have withdrawn **{amount_transferred:,}**. " + f"Current wallet balance **{db.wallet(inter.author.id):,}**.")
            else:
                await inter.send(f"<@{inter.author.id}> Please enter a valid **number**!")

# RICH COMMAND / LEADERBOARD
    @commands.slash_command(description="Get top 10 richest players")
    async def rich(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        leaderboard_string = ""
        embeds = []
        leaderboard_list = db.get_rich_leaderboard()
        counter = 1
        divived_leaderboard_list = list(pagination.divide_list(leaderboard_list, 5))  # All infraction divided in lists of length 5 (so we can paginate)

        for leaderboard in divived_leaderboard_list:
            embed = disnake.Embed(title=f"Economy Leaderboard", description=leaderboard_string, color=const.EMBED_COLOUR)
            embeds.append(embed)

            for row in leaderboard:
                # indexes represent location of column in row log table
                user_mention = f"__{row[0]}__"
                networth = row[1]
                embed.add_field(name=f"{counter}. {user_mention}", value=f"Networth: £{networth:,}\n", inline=False)
                counter += 1

        if len(embeds) == 0:
            await inter.send(f"{const.CROSS_EMOJI} No one in this server has been registered to the bot. Start by creating your account with /create", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))

# BUY COMMAND
    @commands.slash_command(description="Buy an item from the shop")
    async def buy(self, inter: disnake.CommandInteraction, item_name):
        """
        Buy an item from the shop
        ----------
        item_name: The name of the item you want to buy.
        """
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
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

# SELL COMMAND
    @commands.slash_command(description="Sell an item from your inventory")
    async def sell(self, inter: disnake.CommandInteraction, item_name):
        """
        Sell an item from your inventory
        ----------
        item_name: The name of the item you want to sell.
        """
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        item_name = item_name.lower()
        user = inter.author

        if len(db.get_item(user.id, item_name)) == 0:
            await inter.send(f"You do not have that item in your inventory!", ephemeral=True)
            return
        db.sell_item(inter.author.id, item_name)
        await inter.send(f"You have sold `{item_name}` for **{funcs.get_item_sell_price(item_name)}**.")

# INVENTORY COMMAND
    @commands.slash_command(description="Shows your inventory")
    async def inventory(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        user = inter.author
        inventory_string = ""
        embeds = []
        inventory_list = db.get_user_inventory(user.id)
        counter = 1
        divided_inventory_list = list(pagination.divide_list(inventory_list, 5))  # All infraction divided in lists of length 5 (so we can paginate)
        for inventory in divided_inventory_list:
            for row in inventory:
                item = f"{row[1]}"
                inventory_string += f"• `{item.capitalize()}`\n"
                counter += 1
            embed = disnake.Embed(title=f"Economy inventory", description=inventory_string, color=const.EMBED_COLOUR)
            embeds.append(embed)
        if len(embeds) == 0:
            await inter.send(f"You have no items in your inventory! Start by looking at the shop!", ephemeral=True)
        else:
            await inter.send(embed=embeds[0], view=pagination.Menu(embeds))

# GIVE COMMAND (ADMIN ONLY)
    @commands.has_role(const.STAFF_ROLE)
    @commands.slash_command(description="Give user money")
    async def give(self, inter: disnake.CommandInteraction, amount: int, user: disnake.Member, location: str):
        """
        Give a user a sum of money in their wallet or bank
        ----------
        amount: Amount of money you want to give the user
        user: The user you want to give money to
        location: The location where you want to give money to. Must be either "wallet" or "bank".
        """
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        
        location = location.lower()
        if location != "wallet" and location != "bank":
            await inter.send("You must specify location as either `wallet` or `bank`.", ephemeral=True)
            return
        if location == "wallet":
            db.update_wallet(user.id, amount)
        if location == "bank":
            db.update_bank(user.id, amount)

        await inter.send(f"Gave **{amount:,}** to {user.mention}'s {location}", ephemeral=True)

# TAKE COMMAND (ADMIN ONLY)
    @commands.has_role(const.STAFF_ROLE)
    @commands.slash_command(description="Give user money")
    async def take(self, inter: disnake.CommandInteraction, amount: int, user: disnake.Member, location: str):
        """
        Take a sum of money from a user either from their wallet or bank
        ----------
        amount: Amount of money you want to take from the user
        user: The user you want to take money from
        location: The location where you want to take money from. Must be either "wallet" or "bank".
        """       
        if db.check_user(user.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        location = location.lower()
        if location != "cash" and location != "bank":
            await inter.send("You must specify location as either `cash` or `bank`.", ephemeral=True)
            return
        if location == "cash":
            db.deduct_wallet(user.id, amount)
        if location == "bank":
            db.deduct_bank(user.id, amount)

        await inter.send(f"Took **{amount:,}** from {user.mention}'s {location}", ephemeral=True)

# BLACKJACK COMMAND
    @commands.slash_command(description="Blackjack game")
    async def blackjack(self, inter: disnake.CommandInteraction, bet: int):
        """
        Game
        ----------
        bet: The amount of money you want to bet.
        """
        
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return

        user = inter.author
        wallet_balance = db.wallet(user.id)
        minimum_bet = 500
        maximum_bet = 500_000

        if bet < minimum_bet:
            await inter.send(f"You must bet at least £{minimum_bet:,}", ephemeral=True)
            return
        if bet > maximum_bet:
            await inter.send(f"Maximum bet limit is: £{maximum_bet:,}", ephemeral=True)
            return
        if wallet_balance < bet:
            await inter.send(f"You do not have £{bet:,} in your wallet!", ephemeral=True)
            return

        db.deduct_wallet(user.id, bet)
        bj = blackjack.blackjack(inter, self.bot.user.name, bet)
        description = f"You are now betting **{bet:,}**"

        embed = bj.gen_embed(user, self.bot.user.name, bj.user_cards, bj.bot_cards, description=description)

        await inter.send(embed=embed, view=bj)
        
#Job commands
    @commands.slash_command()
    async def job(self, ctx):
        pass
        
    @job.sub_command(description="Job list", name = "list")
    async def job_list(self, inter:disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        embeds = funcs.gen_job_list_embed()
        footer = "/job apply [job-name] to apply for a job. ─ "
        await inter.send(embed=embeds[0], view=pagination.Menu(embeds, footer=footer))
        
    @job.sub_command(description="Apply for a job. use /job list to find a job.")
    async def apply(self, inter:disnake.CommandInteraction, job_name):
        job_name = job_name.lower()
        user = inter.author
        user_level = db.get_level(user.id)
        try:
            job_level = funcs.get_job_level_needed(job_name)
        except KeyError:
            await inter.send(f"That job does not exist! Choose a job from `/job list`", ephemeral=True)
            return
        if db.check_if_has_job(user.id) is True:
            await inter.send(f"You already have a job. Please leave your current job with `/job leave`", ephemeral = True)
        else:
            if user_level < job_level:
                await inter.send(f"You are not high level enough to apply for this job.", ephemeral = True)
                return
            
            db.add_job(user.id, job_name)
            await inter.send(f"Congratulation. You got the job `{job_name.capitalize()}`", ephemeral = True)
            # embed = disnake.Embed(description=description)
            # embed.set_author(name=f"{inter.author.name}", icon_url=inter.author.display_avatar)
            # await inter.send(embed=embed)
            
    @job.sub_command(description = "Leave your current job")
    async def leave(self, inter:disnake.CommandInteraction):
        user = inter.author
        if db.check_if_has_job(user.id) is False:
            await inter.send(f"You don't have a job.", ephemeral = True)
            return
        job_name = db.get_job(user.id).capitalize()
        db.remove_job(user.id)
        await inter.send(f"You have successfully left your job `{job_name}`", ephemeral = True)
        
# WORK COMMAND
    @job.sub_command(description="Work for money. One hour cooldown")
    async def work(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return

        amount_of_work_money = random.randint(250, 5000)

        db.update_wallet(inter.author.id, amount_of_work_money)
        await inter.send(f"You worked and gained **{amount_of_work_money}**. Enjoy!", ephemeral=False)   
        
        

# SHOP COMMAND
    @commands.slash_command(description="Shop where you can buy products")
    async def shop(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return
        embeds = funcs.gen_shop_embed()
        await inter.send(embed=embeds[0], view=pagination.Menu(embeds))


# DAILY COMMAND
    @commands.slash_command()
    @commands.cooldown(1, 86400, type=commands.BucketType.user)
    async def daily(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return

        AMOUNT = 5000

        db.update_wallet(inter.author.id, AMOUNT)
        await inter.send(f"You claimed your daily and recieved **{AMOUNT}** Cash!")

# WEEKLY COMMAND
    @commands.slash_command()
    @commands.cooldown(1, 604800, type=commands.BucketType.user)
    async def weekly(self, inter: disnake.CommandInteraction):
        if db.check_user(inter.author.id) is False:
            await inter.send(const.REGISTER_ERROR, ephemeral = True)
            return

        AMOUNT = 25000

        db.update_wallet(inter.author.id, AMOUNT)
        await inter.send(f"You claimed your weekly and recieved **{AMOUNT}** Cash!")

    # Testing purposes (The id is Anom4ly's)
    
    # @commands.slash_command(description="pog")
    # async def test(self, ctx, user:disnake.Member):
    #     rank = db.get_rich_rank(user.id)
    #     await ctx.send(f"Their rank is: `{rank}`")

    # @commands.command()
    # async def money(self, ctx):
    #     db.update_wallet(338764415358861314,1000000)


# ERROR HANDLING
    @daily.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the daily command."""
        if isinstance(error, commands.CommandOnCooldown):
            time = str(datetime.timedelta(seconds = error.retry_after))[:-7]
            await ctx.send(f"This command is on cooldown. You will be able to use it in `{time}`", ephemeral=True)

    @weekly.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the weekly command."""
        if isinstance(error, commands.CommandOnCooldown):
            time = str(datetime.timedelta(seconds = error.retry_after))[:-7]
            await ctx.send(f"This command is on cooldown. You will be able to use it in `{time}`", ephemeral=True)

    @work.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors for the work command."""
        if isinstance(error, commands.CommandOnCooldown):
            time = str(datetime.timedelta(seconds = error.retry_after))[:-7]
            await ctx.send(f"This command is on cooldown. You will be able to use it in `{time}`", ephemeral=True)

    @give.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"You do not have the `{error.missing_role}` command to use this command", ephemeral=True)

    @take.error
    async def CommandOnCooldown(self, ctx: commands.Context, error: commands.CommandError):
        """Handle errors"""
        if isinstance(error, commands.MissingRole):
            await ctx.send(f"You do not have the `{error.missing_role}` command to use this command", ephemeral=True)

    #@balance.error
    #async def CommandOnBalance(self, ctx: commands.Context, error: commands.CommandError):
    #    """Handle errors"""
    #    if isinstance(error, commands.CommandError):
    #        await ctx.send(f"You are currently not registeredy to play economy. To start playing simply say something in the chat.", ephemeral=True)


def setup(bot):
    bot.add_cog(Economy(bot))
