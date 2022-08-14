import disnake
from disnake.ext import commands
import os
from utils import init_database, constants as const

BOT_KEY = const.BOT_KEY

intents = disnake.Intents.default()
intents.members = True  
intents.message_content = True


bot = commands.Bot(command_prefix = ".", intents=intents,activity=disnake.Game(name="Type in .help"))


for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        print(f"cogs.{filename[:-3]} Loaded")
        bot.load_extension(f"cogs.{filename[:-3]}",) 


async def tasks():
    init_database.restore_database() 
    

def main():
    bot.loop.create_task(tasks())
    bot.run(BOT_KEY) 
    
if __name__ == "__main__":
    main()

