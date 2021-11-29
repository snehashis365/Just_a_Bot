import discord
from discord.ext import commands

from youtube_dl import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        #all the music related stuff
        self.is_playing = []

        # 2d array containing [song, channel]
        self.music_queue = {}
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.vc = {}
        for guild in bot.guilds:
          self.vc[guild.id] = ""
          self.music_queue[guild.id] = []

     #searching the item on youtube
    def search_yt(self, item):
        with YoutubeDL(self.YDL_OPTIONS) as ydl:
            try: 
                info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            except Exception: 
                return False

        return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self, guild_id):
        if len(self.music_queue[guild_id]) > 0:
            self.is_playing.append(guild_id)

            #get the first url
            m_url = self.music_queue[guild_id][0][0]['source']

            #remove the first element as you are currently playing it
            self.music_queue[guild_id].pop(0)

            self.vc[guild_id].play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(guild_id))
        else:
            self.is_playing.remove(guild_id)

    # infinite loop checking 
    async def play_music(self, guild_id):
        if len(self.music_queue[guild_id]) > 0:
            self.is_playing.append(guild_id)

            m_url = self.music_queue[guild_id][0][0]['source']
            
            #try to connect to voice channel if you are not already connected

            if self.vc[guild_id] == "" or not self.vc[guild_id].is_connected() or self.vc[guild_id] == None:
                self.vc[guild_id] = await self.music_queue[guild_id][0][1].connect()
            else:
                await self.vc[guild_id].move_to(self.music_queue[guild_id][0][1])
            
            print(self.music_queue[guild_id])
            #remove the first element as you are currently playing it
            self.music_queue[guild_id].pop(0)

            self.vc[guild_id].play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(guild_id))
        else:
            self.is_playing.remove(guild_id)

    @commands.command(name="play", help="Plays a selected song from youtube")
    async def p(self, ctx, *args):
        query = " ".join(args)
        voice_channel = None
        if ctx.author.voice and ctx.author.voice.channel:
          voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            #you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue[ctx.guild.id].append([song, voice_channel])
                
                if ctx.guild.id not in self.is_playing:
                    await self.play_music(ctx.guild.id)

    @commands.command(name="queue", help="Displays the current songs in queue")
    async def q(self, ctx):
        retval = ""
        for i in range(0, len(self.music_queue[ctx.guild.id])):
            retval += self.music_queue[ctx.guild.id][i][0]['title'] + "\n"

        print(retval)
        if retval != "":
            await ctx.send(retval)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="skip", help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc[ctx.guild.id] != "" and self.vc[ctx.guild.id]:
            self.vc[ctx.guild.id].stop()
            #try to play next in the queue if it exists
            await self.play_music(ctx.guild.id)

    @commands.command(name="pause", help="Pause the current song")
    async def pause(self, ctx):
      if ctx.guild.id in self.is_playing:
        self.vc[ctx.guild.id].pause()
        await ctx.send("Paused")

    @commands.command(name="resume", help="Resume the current song")
    async def resume(self, ctx):
      if ctx.guild.id in self.is_playing and self.vc[ctx.guild.id].is_paused():
        self.vc[ctx.guild.id].resume()
        await ctx.send("Resumed")

    @commands.command(name="stop", help="Stops and disconnects")
    async def stop(self, ctx):
        if self.vc[ctx.guild.id] != "" and self.vc[ctx.guild.id]:
            self.vc[ctx.guild.id].stop()
            self.is_playing.remove(ctx.guild.id)
            await self.vc[ctx.guild.id].disconnect()
            await ctx.send("Stopped")