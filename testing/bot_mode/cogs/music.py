import discord
import youtube_dl
import datetime
from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

player = None
play_message = None

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data # Has lots of information about the YouTube video being played.
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel = None):
        """Joins a voice channel"""

        if channel is None:
            if ctx.voice_client is not None:
                if ctx.author.voice.channel is not None:
                    return await ctx.voice_client.move_to(ctx.author.voice.channel)
                else:
                    return commands.CommandError("You are not currently connected to a voice channel.")
            await ctx.author.voice.channel.connect()

        else:
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(channel)
            await channel.connect()

    @commands.command()
    async def localplay(self, ctx, *, query):
        """Plays a file from the local filesystem"""

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(query))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send(f'Now playing: {query}')

    @commands.command()
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""
        async with ctx.typing():
            global player
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            print(player.data)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        if ctx.guild.get_member(self.bot.user.id).permissions_in(ctx.channel).value & 0x4000 == 0x4000:
            embed = discord.Embed(color=0xff0000, url=player.data.get('webpage_url'))
            embed.set_author(name="YouTube", icon_url=ctx.author.avatar_url)
            embed.set_footer(text=f"👁️{player.data.get('view_count')}👍{player.data.get('like_count')}👎{player.data.get('dislike_count')}")
            embed.set_thumbnail(url=player.data.get('thumbnail'))

            embed.add_field(name=f"{player.data.get('uploader')}", value=f"[{player.title}]({player.data.get('webpage_url')})")
            embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=player.data.get('duration'))))

            global play_message
            play_message = await ctx.send(content="**Now Playing**", embed=embed)

        else:
            play_message = None
            await ctx.send(
            f'''>>> **Now playing: `{player.title}` by `{player.data.get('uploader')}`
            Duration: `{str(datetime.timedelta(seconds=player.data.get('duration')))}` **''')

    @commands.command()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send(f'Now playing: {player.title}')

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current video"""
        if ctx.voice_client.is_playing() == True:
            ctx.voice_client.pause()

            global play_message
            if play_message is not None:
                await play_message.edit(content=f"**Now Playing** (Paused by {ctx.author.mention})")
            await ctx.send("**Paused**")

        else:
            raise commands.CommandError("The music is already paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the current video"""
        if ctx.voice_client.is_paused() == True:
            ctx.voice_client.resume()

            global play_message
            if play_message is not None:
                await play_message.edit(content="**Now Playing**")
            await ctx.send("**Resumed**")
        else:
            raise commands.CommandError("The music is not currently paused.")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        if 0 < volume < 150:
            await ctx.send(f"Changed volume to {volume}%")
        elif volume >= 150:
            await ctx.send(f"Changed volume to 150% (Maximum)")
            volume = 150
        else:
            await ctx.send(f"Changed volume to 0% (Minimum)")
            volume = 0

        ctx.voice_client.source.volume = volume / 100

    @commands.command()
    async def songinfo(self, ctx):
        """Displays some info about the song"""
        if player is not None:
            if ctx.guild.get_member(self.bot.user.id).permissions_in(ctx.channel).value & 0x4000 == 0x4000:
                embed = discord.Embed(color=0xfff000)
                embed.set_author(name=player.data.get('title'), icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=player.data.get('thumbnail'))

                embed.add_field(name="Webpage Link", value=f"[{player.title}]({player.data.get('webpage_url')})")
                embed.add_field(name="Views", value=f"👁️{player.data.get('view_count')}")

                embed.add_field(name="Likes", value=f"👍{player.data.get('like_count')}")
                embed.add_field(name="Dislikes", value=f"👎{player.data.get('dislike_count')}")

                embed.add_field(name="Uploader", value=f"{player.data.get('uploader')}")
                embed.add_field(name="Duration", value=str(datetime.timedelta(seconds=player.data.get('duration'))))

                upload_date = player.data.get('upload_date')

                embed.add_field(name="Categories", value=f"{player.data.get('categories')}")
                embed.add_field(name="Average Rating", value=f"{player.data.get('average_rating')}/5")
                embed.add_field(name="Upload Date", value=f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}")

                embed.add_field(name="Tags", value=f"{player.data.get('tags')}", inline=False)

                await ctx.send(embed=embed)
        else:
            raise commands.CommandError("No music is currently being played.")

    @commands.command()
    async def songdesc(self, ctx):
        """Displays the description of the YouTube video"""
        exited = False
        x = 0
        descriptions = []
        if player is not None:
            if ctx.guild.get_member(self.bot.user.id).permissions_in(ctx.channel).value & 0x4000 == 0x4000:

                description = player.data.get('description')
                while exited != True:
                    descriptions.append(description[x:x+1024])
                    if len(description) >= x + 1024:
                        x += 1024
                    else:
                        exited = True
                print(str(descriptions))
                print("fuwefjrwiojiwejoirjo3eowriewjroiewjio")

                for y in range(0, len(descriptions)):
                    embed = discord.Embed(color=0xfff000)
                    embed.set_author(name=player.title)
                    embed.set_thumbnail(url=player.data.get('thumbnail'))
                    embed.add_field(name=f"Page {y+1}", value=descriptions[y])
                    await ctx.send(embed=embed)

    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @commands.command(
        name='move',
        help='Moves a member into a different voice channel.'
    )

    @commands.has_permissions(administrator=True)
    async def v_move(self, ctx, member: discord.Member, channel: discord.VoiceChannel=None):
        print(ctx.guild.get_member_named("Chungus").guild_permissions.value & 0x1000000 == 0x1000000)
        if member.voice is not None:
            await member.move_to(channel)
        else:
            raise commands.CommandError("This member is not currently connected to any voice channel.")

    @localplay.before_invoke
    @play.before_invoke
    @stream.before_invoke

    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")

        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

def setup(bot):
    bot.add_cog(Music(bot))
