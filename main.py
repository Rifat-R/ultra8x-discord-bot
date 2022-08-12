import disnake
from disnake.ext import commands
import os
from utils import init_database

BOT_KEY = 'NzQwMTg1NTk2NTI1NTQzNDI0.G92hI3.qvqaed90aJW9xKJWx9mwq5dDL5KLxYaKWihGiw'

intents = disnake.Intents.default()
intents.members = True  
intents.message_content = True


bot = commands.Bot(command_prefix = ".", intents=intents,activity=disnake.Game(name="Type in .help"), reload=True)


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

