import os
import discord
import firebase_admin
import pyshorteners
from discord.ext import commands
from discord.utils import find
from firebase_admin import credentials
from firebase_admin import firestore
from keep_running import keep_alive

KEY_NOTE_VAL = 'message'
KEY_NOTE = 'notes'

credentials_certificate = credentials.Certificate(
    'firebase-admin-sdk-key.json')
firebase_admin.initialize_app(credentials_certificate)
db = firestore.client()
servers_ref = db.collection('servers')


def getshorturl(url):
    shortener = pyshorteners.Shortener()
    return shortener.tinyurl.short(url)


help_msg = "**This is Just a BOT**\nWritten in _Python_ and trying to keep it simple for the time being here's the list of commands:```\n$hello -> Says Hello\n\n$bye -> Says Bye\n\n$ping -> Returns Bot Latency in miliseconds\n\n$notes -> Shows list of saved notes\n\n$save <note name> -> Saves the mentioned menssage with provided name to be retreived later\n\n$get <note name> -> Retreives to queried note\n\n$shorten <url1> <url2> ... -> Shortens provided urls with tinyurl\n\n$help -> Shows this help message\n\n(More Coming Soon)\n```\n_Invite Link_:** https://tinyurl.com/yf6t3zky **"

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
    print('-----------------------------\n')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name=f'{len(bot.guilds)} servers')
                              )


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


@bot.command(pass_context=True)
async def ping(message):
    await message.send(f'Pong! in {round(bot.latency * 1000)}ms')
    print(f'Pinged from Guild : {message.guild.name} ID : {message.guild.id}')


@bot.command(pass_context=True)
async def save(ctx, *arg):
    if len(arg) == 1:
        note_ref = servers_ref.document('{}'.format(
            ctx.guild.id)).collection(KEY_NOTE).document(arg[0])
        if note_ref.get().exists:
            await ctx.send(f'"{arg[0]}" already exists')
        else:
            msgReferred = ctx.message.reference
            if msgReferred:
                msg = await ctx.fetch_message(msgReferred.message_id)
                if len(msg.content) <= 2000:
                    note_ref.set({KEY_NOTE_VAL: msg.content})
                    await ctx.send(f'Saved Note: "{arg[0]}"')
                else:
                    await ctx.send(
                        'Message exceeds 2000 characters limit I cannot afford Nitro XD'
                    )
            else:
                await ctx.send('Reply to the message to be saved as note')
    else:
        await ctx.send('Please provide a name of the note as well')


@bot.command(pass_context=True)
async def get(ctx, *arg):
    if len(arg) == 0:
        await ctx.send('Please provide name of the note to fetch')
    else:
        note_ref = servers_ref.document('{}'.format(
            ctx.guild.id)).collection(KEY_NOTE).document(arg[0])
        if note_ref.get().exists:
            await ctx.send(note_ref.get().to_dict()[KEY_NOTE_VAL])
        else:
            await ctx.send(f'_{arg[0]}_ does not exist as a saved note')


@bot.command(pass_conext=True)
async def notes(ctx):
    notes_collection = servers_ref.document('{}'.format(
        ctx.guild.id)).collection(KEY_NOTE)
    notes_stream = notes_collection.stream()
    notes_list = []
    for note in notes_stream:
        notes_list.append(note.id)
    if len(notes_list) > 0:
        msg_text = 'List of notes for this server:\n```\n'
        i = 1
        for item in notes_list:
            msg_text += f'{i}. {item}\n'
            i += 1
        msg_text += '```\nUse **$get <note name>** to retreive a note'
        await ctx.send(msg_text)
    else:
        ctx.send(
            'No notes saved for this server use **$save <note name>** while replying to a message to save that message'
        )


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
