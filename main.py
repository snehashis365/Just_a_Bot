import os
import discord
import firebase_admin
import pyshorteners
from discord.ext import commands
from discord.utils import find
from firebase_admin import credentials
from firebase_admin import firestore
from keep_running import keep_alive
from music_cog import music_cog
from deep_translator import GoogleTranslator
#import pytz
#from datetime import datetime

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


help_msg = "**This is Just a BOT**\nWritten in _Python_ and trying to keep it simple for the time being here's the list of commands:```\n$hello -> Says Hello\n\n$bye -> Says Bye\n\n$ping -> Returns Bot Latency in miliseconds\n\n$play <song name/youtube link> -> Plays the song from youtube\n\n$pause -> Pause the current song\n\n$resume -> Resume playback\n\n$stop -> Stops the song and disconnects from VC\n\n$queue -> Shows the upcoming queued songs\n\n$notes -> Shows list of saved notes\n\n$save <note name> -> Saves the mentioned menssage with provided name to be retreived later\n\n$get <note name> -> Retreives to queried note\n\n$shorten <url1> <url2> ... -> Shortens provided urls with tinyurl\n\n$translate -> Translated the mentioned message to english\n\n$exams -> Shows 4th Semester 2021 Exam Schedule and countdown\n\n$help -> Shows this help message\n\n(More Coming Soon)\n```\n_Invite Link_:** https://tinyurl.com/yfqh7ac5 **"

bot = commands.Bot(command_prefix='$')
bot.remove_command('help')
translator = GoogleTranslator(source='auto', target='en')

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
    bot.add_cog(music_cog(bot))
    print('-----------------------------')
    print('Total : ', len(bot.guilds))
    print('-----------------------------\n')
    print(
        f'Ping : {round(bot.latency * 1000)}ms\nInvite Link: https://tinyurl.com/yfqh7ac5'
    )
    print('-----------------------------\n')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, name=f'{len(bot.guilds)} servers')
                              )


@bot.command(pass_context=True)
async def help(ctx):
    await ctx.send(help_msg)


@bot.command(pass_context=True)
async def hello(ctx):
    await ctx.send(f'Hello! {ctx.author.mention}')
    print(f'Hello requested from {ctx.guild.name}')


@bot.command(pass_context=True)
async def bye(ctx):
    await ctx.send(f'Bye bye {ctx.author.mention}!!')


@bot.command(pass_context=True)
async def ping(ctx):
    await ctx.send(f'Pong! in {round(bot.latency * 1000)}ms')
    print(f'Pinged from Guild : {ctx.guild.name} ID : {ctx.guild.id}')


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
async def del_note(ctx, *args):
  if ctx.message.author.guild_permissions.administrator:
    if len(args) == 0:
      await ctx.send('Please provide atleast one note to be deleted')
    else:
      count = 0
      for arg in args:
        note_ref = servers_ref.document('{}'.format(ctx.guild.id)).collection(KEY_NOTE).document(arg)
        if note_ref.get().exists:
          note_ref.delete()
          count += 1
        else:
          await ctx.send(f'Alert !!!" {arg}" does not exist')
      await ctx.send(f'Deleted {count} notes')
  else:
    await ctx.send('You lack permissions to delete a note ask your server admin/moderator for help')
                  

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
        await ctx.send(
            'No notes saved for this server use **$save <note name>** while replying to a message to save that message'
        )


@bot.command(pass_context=True)
async def shorten(ctx, *args):
    if len(args) == 0:
        await ctx.send(
            'Please a provide _atleast one link_ to generate short link\n**Syntax**:\n```$shorten link1 ...```'
        )
        return
    for arg in args:
        url = getshorturl(arg)
        await ctx.send(f'Shortened {arg} -> {url}\n')
    print(
        f'Generated {len(args)} shortened links\nRequested by: {ctx.guild.name}, {ctx.author.name}'
    )

@bot.command(pass_context=True)
async def translate(ctx):
  msgReferred = ctx.message.reference
  if msgReferred:
    msg = await ctx.fetch_message(msgReferred.message_id)
    print(msg.content)
    result = translator.translate(msg.content)
    await ctx.send(result)
  else:
    await ctx.send('Mention a message to be translated')

@bot.command(pass_context=True)
async def exams(ctx):
  await ctx.send('**Exam khatam ho gaya BSDK**')


'''additional_msg =''
IST = pytz.timezone('Asia/Kolkata')
time_now = datetime.now(IST)
exam_time = datetime(2021, 8, time_now.day, 14, 0)
if(time_now.hour>=14 and ((time_now.hour == 15 and time_now.minute<=30) or time_now.hour<15)):
  additional_msg = 'Exam Ongoing'
elif(time_now.hour>=16):
  exam_time = datetime(2021, 8, time_now.day+1, 14, 0)
exam_time = IST.localize(exam_time)
diff = exam_time - time_now
if(additional_msg != 'Exam Ongoing'):
  additional_msg = 'Starts in ' + str(diff.seconds//3600) + ' hours, ' + str((diff.seconds//60)%60) + ' minutes'
await ctx.send('List Of All Subjects(4th Semester):\n```4514 : DATABASE MANAGEMENT SYSTEM ( 10-08-2021 : 2.00PM-3.30PM )[DONE]\n4515 : PROGRAMMING WITH JAVA ( 11-08-2021 : 2.00PM-3.30PM )[DONE]\n4516 : COMPUTER NETWORKING ( 12-08-2021 : 2.00PM-3.30PM )[DONE]\n4517 : NUMERICAL ANALYSIS ( 13-08-2021 : 2.00PM-3.30PM )[DONE]```\nStatus : **' + additional_msg + '**')'''

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
