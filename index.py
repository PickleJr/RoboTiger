import discord
import logging
import configparser
from manager import Manager
from discord.ext import commands

config = configparser.ConfigParser()
config.read('config.ini')

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='./logs/discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Opus file is not needed if we aren't using the discord voice plugin
if not discord.opus.is_loaded():
    #Load opus file
    #discord.opus.load_opus('opus')
    print("Opus is not loaded!")

print("Hello, World!")

bot = commands.Bot(command_prefix=commands.when_mentioned_or(config['bot']['trigger'] + " "), description='Tornament/Admin bot for the TigerLan discord server.')
bot.add_cog(Manager(bot))

@bot.event
async def on_ready():
    print('Logged in as: \n{0} (ID: {0.id})'.format(bot.user))

bot.run(config['discord']['token'])
