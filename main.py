import os
import pyshorteners
from discord.ext import commands
from discord.utils import find
from keep_running import keep_alive

def getshorturl(url):
  shortener = pyshorteners.Shortener()
  return shortener.tinyurl.short(url)

help_msg = "**This is Just a BOT**\nWritten in _Python_ and trying to keep it simple for the time being here's the list of commands:```\n$hello -> Says Hello\n\n$shorten <url> -> Shortens provided url with tinyurl\n\n$help -> Shows this help message\n\n(More Coming Soon)\n```"

bot = commands.Bot(command_prefix = '$')

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

#Migrated to Bot which is a subclass of Client so not much has changed
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send(f'Hello! {message.author.mention}')
        print(f'Hello requested from {message.guild.name}')

    if message.content.startswith('$shorten'):
        url = getshorturl(message.content[9:])
        await message.channel.send('Shortened URL: {}'.format(url))
        print(f'Shorten request from {message.guild.name}, {message.author.name} generated: {url}')

    #Help message
    if message.content.startswith('$help'):
      await message.channel.send(help_msg)

#Introduces itself after joining a server
@bot.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send(f'**Hello everyone at {guild.name}! Let us all have a great time!!**\n _Please use **$help** for list commands_') 

TOKEN = os.environ['TOKEN']

keep_alive()
bot.run(TOKEN)