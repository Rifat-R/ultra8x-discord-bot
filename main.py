import disnake
from disnake.ext import commands
import os
from utils import init_database

BOT_KEY = 'NzQwMTg1NTk2NTI1NTQzNDI0.G92hI3.qvqaed90aJW9xKJWx9mwq5dDL5KLxYaKWihGiw'
# Enable all intents except for members and presences
intents = disnake.Intents.default()
intents.members = True  # Subscribe to the privileged members intent.
intents.message_content = True

# bot = commands.Bot(intents=intents, activity=disnake.Game(name="Type in .help"))
bot = commands.Bot(command_prefix = ".", intents=intents,activity=disnake.Game(name="Type in .help"), reload=True)


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        print(f"cogs.{filename[:-3]} Loaded")
        bot.load_extension(f"cogs.{filename[:-3]}",) #Loads up all the cogs (modules) in the /cogs directory


async def tasks():
    init_database.restore_database() #importing init_database module in utils and using the create_tables() function we created to check if anything is needed to be
    #restored

def main():
    bot.loop.create_task(tasks())
    bot.run(BOT_KEY) #Starts up the discord bot with an API key
    
if __name__ == "__main__":
    main()

