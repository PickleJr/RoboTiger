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
            return msg.content == 'y' or msg.content == 'n'

        answer = await self.bot.wait_for_message(author=ctx.message.author, check=check)
        if answer.content == 'y':
            self.db.purge_tables()
            await self.bot.send_message(ctx.message.channel, '{} tornaments killed!'.format(amention))
        elif answer.content == 'n':
            await self.bot.send_message(ctx.message.channel, '{} okay. I\'ll do nothing then.'.format(amention))
        else:
            await self.bot.send_message(ctx.message.channel, '{} Uhhh... Whatever you typed confused me. Please try again.'.format(amention))
