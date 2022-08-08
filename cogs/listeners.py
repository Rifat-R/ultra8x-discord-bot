from disnake.ext import commands
from utils import database as db
import sqlite3

class listeners_Cog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     if "." in message.content: #If it starts with the prefix, meaning if a user sent a command
    #         pass #Do nothing
    #     else:
    #         try:
    #             db.create(message.author.id) #Create the account and register the user in the database
    #             print("User has been created") #Check if the code worked.
    #         except(sqlite3.IntegrityError): #This error handler is if two of the same user_id's has been put in the user_data table.
    #             #If the user already exist's and try's to put another user of the same id, it would not add the user as the user_id
    #             #Fieldname is a PRIMARY KEY therefore will not accept duplicate user_id's
    #             pass

    @commands.Cog.listener()
    async def on_message(self, message):
        # print(message.content[0])
        if not message.author.bot: #This should now check whether the message author is not a bot, then it will
            #Run the code block underneath and do nothing if it is a bot.
            if message.content[0] != ".":
                try:
                    db.create(message.author.id)
                    print(f"User {message.author.id} has been created and stored in user_data table.")
                except(sqlite3.IntegrityError):
                    pass

def setup(bot):
    bot.add_cog(listeners_Cog(bot))
