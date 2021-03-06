import asyncio
import discord
import configparser
import time
from discord.ext import commands
from tinydb import TinyDB, Query
from tinydb.operations import set

'''
TODO: Add admin check for purge and add tournament command.
TODO: Add a way for a team to leave a tournament.
TODO: Add a way for an admin to add a team to a tournament.
'''

class Manager:
    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.db = TinyDB(self.config['db']['path'])

    @commands.command(pass_context=True, no_pm=True)
    async def help(self, ctx, *args):
        author = ctx.message.author
        amention = author.mention
        has_privs = self.userIsAdmin(author)
        trigger = self.config['bot']['trigger']
        msg = (
            '{0} Below is a list of example commands. If you want to pass additional arguments to the commands that accept arguments, you might have to wrap quotes around those arguments. '
            'If you don\'t wrap the additinoal arguments in quotes, there\'s a chance I won\'t understand the command and I\'ll just ignore them and ask you for the information I need.\n\n'
            '{1} u <any insult>    - Returns "no u"\n'
            '{1} suggestion <sugggestion>    - Submits a suggestion for this bot.\n'
            '{1} add team "<tournament name>" "<team name>" "<@Members, @on, this, team>"    - Joints your team to a tournament (Notice the quotes)'
        )
        if has_privs:
            msg = msg + (
                '\n\n As an admin, you also have the ability to do these commands:\n\n'
                '{1} add tournament "<tournament name>"    - Creates a tournament\n'
                '{1} purge    - Delete ALL tournament data. Do this at the end of TigerLan'
            )

        await self.bot.send_message(ctx.message.channel, msg.format(amention, trigger))

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
        await self.bot.send_message(ctx.message.channel, '{} about to kill all tournament data, are you sure? (y/n)'.format(amention))

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
            await self.bot.send_message(answer.channel, '{} tournaments killed!'.format(amention))
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

    def userIsAdmin(self, user):
        roles = [str(role) for role in user.roles]
        return 'Mods' in roles or 'Admins' in roles or '@everyone' in roles

    @commands.group(pass_context=True, no_pm=True)
    async def add(self, ctx):
        if ctx.invoked_subcommand is None:
            author = ctx.message.author
            amention = author.mention
            has_privs = self.userIsAdmin(author)

            msg = '{} No subcommand found! Please call '
            if has_privs: msg = msg + 'either "add tournament" or '
            msg = msg + '"add team". Alternatively call "' + self.config['bot']['trigger'] + ' help" for a list of all commands!'
            await self.bot.send_message(ctx.message.channel, msg.format(amention))

    @add.command(pass_context=True, no_pm=True)
    async def tournament(self, ctx, *arg):
        amention = ctx.message.author.mention
        if len(arg) == 1:
            self.db.insert({
                'tournament': arg[0],
                'teams': []
            })
            msg = '{} tournament ' + arg[0] + ' has been created!'
            await self.bot.send_message(ctx.message.channel, msg.format(amention))
            return
        
        await self.bot.send_message(ctx.message.channel, '{} what is the name of the tournament?'.format(amention))
        tournament = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
        
        if tournament is None:
            await self.bot.send_message(ctx.message.channel, '{} No input recieved! No tournament has been created.'.format(amention))
            return

        tournament = tournament.content
        self.db.insert({
            'tournament': tournament,
            'teams': []
        })
        msg = '{} tournament ' + tournament + ' has been created!'
        await self.bot.send_message(ctx.message.channel, msg.format(amention))

    @add.command(pass_context=True, no_pm=True)
    async def team(self, ctx, *arg):
        amention = ctx.message.author.mention
        tournament = None
        team = None
        members = None

        tournaments = self.db.all()
        tournament_names = [vals['tournament'] for vals in tournaments]
        if len(tournament_names) == 0:
            await self.bot.send_message(ctx.message.channel, '{} No tournaments have been created yet! Please talk to an admin or mod.'.format(amention))
            return

        if len(arg) == 3:
            tournament = arg[0]
            team = arg[1]
            members = arg[2]
            members = amention + ", " + members
            if tournament not in tournament_names:
                msg = '{} That tournament has not been created yet. Please try that again. Here are the Tornaments you can join:'
                for val in tournament_names:
                    msg = msg + '\n' + val
                msg = msg + '\nPlease try running that command again with one of these tournaments. Or contact an admin/mod for help.'
                await self.bot.send_message(ctx.message.channel, msg.format(amention))
                return
        else:
            msg = '{} What tournament would you like to join? Here are your options:'
            for val in tournament_names:
                msg = msg + '\n' + val
            await self.bot.send_message(ctx.message.channel, msg.format(amention))
            tournament = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
            if tournament is not None: tournament = tournament.content

            while tournament is not None and tournament not in tournament_names and tournament != 'stop':
                await self.bot.send_message(ctx.message.channel, \
                    '{} That tournament does not exist! Please try again or contact an admin/mod.\n Alternatively, type "stop" to cancel this command.'.format(amention))
                tournament = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
                if tournament is not None: tournament = tournament.content

            if tournament is None:
                await self.bot.send_message(ctx.message.channel, '{} No input recieved. Action canceled. Please try again.'.format(amention))
                return
            elif tournament == 'stop':
                await self.bot.send_message(ctx.message.channel, '{} Action canceled. Nothing was done!'.format(amention))
                return

            await self.bot.send_message(ctx.message.channel, '{} What is the name of your team?'.format(amention))
            team = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
            if team is None:
                await self.bot.send_message(ctx.message.channel, '{} No input recieved. Action canceled. Please try again.'.format(amention))
                return
            team = team.content

            msg = '{} Who all is in your team? You can either @ them in discord or just provide a name. Don\'t write your own name down. I know who you are ;).'
            msg = msg + '\nExample: @Botson, @Botty, playerone, playertwo'
            await self.bot.send_message(ctx.message.channel, msg.format(amention))
            members = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
            if members is None:
                await self.bot.send_message(ctx.message.channel, '{} No input recieved. Action canceled. Please try again.'.format(amention))
                return
            members = members.content
            members = amention + ", " + members

        msg = '{} Alright, let me make sure I got that right...\n'
        msg = msg + 'You want to join the ' + tournament + ' tournament.\n'
        msg = msg + 'Your team name is ' + team + '.\n'
        msg = msg + 'Your team members are ' + members + '.\n'
        msg = msg + 'Is this information correct? (y/n)'
        await self.bot.send_message(ctx.message.channel, msg.format(amention))
        answer = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
        if answer is not None: answer = answer.content

        while answer is not None and answer != 'y' and answer != 'n':
            await self.bot.send_message(answer.channel, '{} Uhhh... I did not understand that. Please just say "y" or "n".'.format(amention))
            answer = await self.bot.wait_for_message(timeout=30,author=ctx.message.author)
            if answer is not None: answer = answer.content

        if answer is None:
            await self.bot.send_message(ctx.message.channel, '{} No input recieved. Action canceled. Please try again.'.format(amention))
            return
        elif answer == 'n':
            await self.bot.send_message(ctx.message.channel, '{} Action canceled!'.format(amention))
            return

        entry = Query()
        result = self.db.search(entry.tournament == tournament)
        teams = result[0]['teams']
        teams.append({
            'team': team,
            'players': members
        })
        self.db.update(set('teams', teams), entry.tournament == tournament)

        msg = '{} I have you and your team down for the ' + tournament + ' tournament! Good luck!'
        await self.bot.send_message(ctx.message.channel, msg.format(amention))