import os
import discord
import pyshorteners
from discord.ext import commands
from discord.utils import find
from keep_running import keep_alive


def getshorturl(url):
    shortener = pyshorteners.Shortener()
    return shortener.tinyurl.short(url)


help_msg = "**This is Just a BOT**\nWritten in _Python_ and trying to keep it simple for the time being here's the list of commands:```\n$hello -> Says Hello\n\n$bye -> Says Bye\n\n$ping -> Returns Bot Latency in miliseconds\n\n$shorten <url1> <url2> ... -> Shortens provided urls with tinyurl\n\n$help -> Shows this help message\n\n(More Coming Soon)\n```\n_Invite Link_:** https://tinyurl.com/yf6t3zky **"

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')


@bot.event
async def on_ready():
    print('\n-----------------------------')
    print('Logged in as:')
    print('-----------------------------')
    print('Name : ', bot.user.name)
    print('ID : ', bot.user.id)
    print('Discord Version : ', discord.__version__)
    print('-----------------------------')
    print('Servers connected to:')
    print('-----------------------------')
    for guild in bot.guilds:
        print(guild.name)
    print('-----------------------------')
    print('Total : ', len(bot.guilds))
    print('-----------------------------\n')
    print(
        f'Ping : {round(bot.latency * 1000)}ms\nInvite Link: https://tinyurl.com/yf6t3zky'
    )
    await bot.change_presence(activity=discord.Activity(type = discord.ActivityType.listening, name = f'{len(bot.guilds)} servers'))


#Migrated to Bot which is a subclass of Client so not much has changed


@bot.command(pass_context=True)
async def help(message):
    await message.send(help_msg)


@bot.command(pass_context=True)
async def hello(message):
    await message.send(f'Hello! {message.author.mention}')
    print(f'Hello requested from {message.guild.name}')


@bot.command(pass_context=True)
async def bye(message):
    await message.send(f'Bye bye {message.author.mention}!!')


@bot.command(pass_contexr=True)
async def ping(message):
    await message.send(f'Pong! in {round(bot.latency * 1000)}ms')
    print(f'Pinged from Guild : {message.guild.name} ID : {message.guild.id}')


@bot.command(pass_context=True)
async def shorten(message, *args):
    if len(args) == 0:
        await message.send(
            'Please a provide _atleast one link_ to generate short link\n**Syntax**:\n```$shorten link1 ...```'
        )
        return
    for arg in args:
        url = getshorturl(arg)
        await message.send(f'Shortened {arg} -> {url}\n')
    print(
        f'Generated {len(args)} shortened links\nRequested by: {message.guild.name}, {message.author.name}'
    )

'''
@bot.event
async def on_message(message):
#    To override on_message use the below line to avoid problems
#    await bot.process_commands(message)
#    if message.author == bot.user:
#        return
'''

#Introduces itself after joining a server
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(
            f'**Hello @everyone at {guild.name}!** Let us all have a great time!!\n _Please use **$help** for the list commands_'
        )


TOKEN = os.environ['TOKEN']

keep_alive()
bot.run(TOKEN)
