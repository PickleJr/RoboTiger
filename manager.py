import asyncio
import discord
import configparser
from discord.ext import commands
from tinydb import TinyDB, Query

class Manager:
    def __init__(self, bot):
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.db = TinyDB(self.config['db']['path'])
        self.tornaments = {}

    @commands.command(pass_context=True, no_pm=True)
    async def test(self, ctx, *args):
        await self.bot.send_message(ctx.message.channel,'{} arguments: {}'.format(len(args), ', '.join(args)))

    @commands.command(pass_context=True, no_pm=True)
    async def u(self, ctx, *args):
        amention = ctx.message.author.mention
        await self.bot.send_message(ctx.message.channel, '{} no u'.format(amention))

    @commands.command(pass_context=True, no_pm=True)
    async def purge(self, ctx):
        amention = ctx.message.author.mention
        await self.bot.send_message(ctx.message.channel, '{} about to kill all tornament data, are you sure? (y/n)'.format(amention))

        def check(msg):
            msgBool = msg.content == 'y' || msg.content == 'n'
            if not msgBool:
                self.bot.send_message(message.channel, '{} I didn\'t understand that. Please just say "n" or "y"')
            return msgBool

        answer = await self.bot.wait_for_message(author=ctx.message.author.mention, check=check)
        if answer == 'y':
            await self.bot.send_message(ctx.message.channel, '{} tornaments killed!'.format(amention))
        elif answer == 'n':
            await self.bot.send_message(ctx.message.channel, '{} okay. I\'ll do nothing then.'.format(amention))
        else:
            await self.bot.send_message(ctx.message.channel, '{} Lol how did you get here?'.format(amention))
