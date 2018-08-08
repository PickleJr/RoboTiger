import asyncio
import discord
import configparser
import time
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

        answer = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
        content = answer.content if answer is not None else ""

        while answer is not None and content != "y" and content != "n":
            await self.bot.send_message(answer.channel, '{} Uhhh... I did not understand that. Please just say "y" or "n".'.format(amention))
            answer = await self.bot.wait_for_message(timeout=30, author=answer.author)
            if answer is not None: content = answer.content

        if answer is None:
            await self.bot.send_message(ctx.message.channel, '{} Took too long to answer, action canceled'.format(amention))
        elif answer.content == 'y':
            self.db.purge_table('_default')
            await self.bot.send_message(answer.channel, '{} tornaments killed!'.format(amention))
        elif answer.content == 'n':
            await self.bot.send_message(answer.channel, '{} okay. I\'ll do nothing then.'.format(amention))


    @commands.command(pass_context=True, no_pm=True)
    async def suggestion(self, ctx, *arg):
        suggestion = " ".join(arg)
        amention = ctx.message.author.mention

        if len(arg) == 0:
            await self.bot.send_message(ctx.message.channel, '{} what is your suggestion?'.format(amention))
            suggestion = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
            suggestion = suggestion.content if suggestion is not None else ""
        if suggestion == "":
            await self.bot.send_message(ctx.message.channel, '{} no suggestion reported. Action canceled.'.format(amention))
            return

        suggestions = self.db.table('suggestions')
        suggestions.insert({
            'userid': ctx.message.author.id,
            'username': ctx.message.author.name,
            'suggestion': suggestion
        })
        await self.bot.send_message(ctx.message.channel, '{} suggestion noted. Thanks!'.format(amention))


    @commands.group(pass_context=True, no_pm=True)
    async def add(self, ctx):
        if ctx.invoked_subcommand is None:
            author = ctx.message.author
            amention = author.mention
            has_privs = 'Mods' in author.roles or 'Admins' in author.roles

            msg = '{} No subcommand found! Please call '
            if has_privs: msg = msg + 'either "add tornament" or '
            msg = msg + '"add team". Alternatively call "' + self.config['bot']['trigger'] + ' help" for a list of all commands!'
            await self.bot.say(ctx.message.channel, '{} No subcommand found! Please call '.format(amention))
