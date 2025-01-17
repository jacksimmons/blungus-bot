import asyncio

import discord
import yt_dlp

import datetime
import random
import os

from discord import app_commands
from discord.ext import commands

embed_colour = 0xFFFF00

# Suppress noise about console usage from errors
#yt_dlp.utils.bug_reports_message = lambda: ''
pbs: float = 1
PBS_MIN: float = 0
PBS_MAX: float = 10

# No reason to change these - these are the actual limits of ffmpeg.
VOL_MIN: float = 0
VOL_MAX: float = 2

ffmpeg_path: str = os.getcwd() + "/ffmpeg/bin/ffmpeg.exe"

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

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

#---------------------------------------------------------------------------------

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)
        self.data = data # Has lots of information about the YouTube video being played.
        self.uploader = data.get('uploader')
        self.title = data.get('title')
        self.url = data.get('url')
        
    @classmethod
    async def from_url_extract(cls, data, loop=None, stream=False, ffmpeg_options={}):
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(
            discord.FFmpegPCMAudio(source=filename,
            **ffmpeg_options), data=data)

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        global pbs
        ffmpeg_options = {
            'options': f'-vn -filter:a "atempo={pbs}"',
            "executable": ffmpeg_path,
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        songs = []
        if 'entries' in data:
            for entry in data['entries']:
                songs.append(await cls.from_url_extract(entry, loop, stream, ffmpeg_options))
        else:
            songs.append(await cls.from_url_extract(data, loop, stream, ffmpeg_options))
        return songs

#---------------------------------------------------------------------------------

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.source_channel = None
        self.bound_member = None
        self.queue = []
        self.prev = None
        
    #---------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        guild = member.guild
        if guild.voice_client is not None:
            if guild.voice_client.channel is not None:
                print(guild.voice_client.channel.name)
                if before.channel != after.channel:
                    if member == self.bound_member:
                        if after.channel is None:
                            await guild.voice_client.disconnect()
                            await guild.voice_client.cleanup()
                            await self.source_channel.send("You disconnected from voice, so I am no longer bound to you.")
                            self.bound_member = None
                        elif guild.me.permissions_in(after.channel).connect is True and guild.me.permissions_in(after.channel).speak is True:
                            await guild.voice_client.move_to(after.channel)
                        else:
                            await self.source_channel.send(f"{member.name}: I can't join that channel; waiting here...")
                    elif guild.voice_client.is_playing():
                        if before.channel == guild.voice_client.channel: #i.e. if they moved out of the bot's current channel
                            channel_members = guild.voice_client.channel.members # This is for code simplification
                            if len(channel_members) == 1 and guild.me in channel_members: #Check the bot is alone
                                await guild.voice_client.disconnect()
                                await self.source_channel.send("All members have left the voice chat, so the player has stopped.")
                            else:
                                await self.source_channel.send("I was disconnected from voice, so the player has stopped.")

    #---------------------------------------------------------------------------------

    def after_song(self, ctx: commands.Context, e):
        print("Player error % e", e) if e else None
        if len(self.queue) > 0:
            self.queue.pop(0)
            if len(self.queue) > 0:
                ctx.guild.voice_client.play(self.queue[0], after=lambda e: self.after_song(ctx, e))

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="queue")
    async def _queue(self, ctx: commands.Context,):
        """Displays the song queue."""
        embed = discord.Embed(color=embed_colour)

        embed.set_author(name=f"Queue ({len(self.queue)})")
        for song in self.queue:
            embed.add_field(name=self.queue.index(song)+1, value=f'{song.title}', inline=False)

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="clear")
    @commands.has_permissions(manage_channels=True)
    async def _clear_queue(self, ctx: commands.Context):
        """Clears the song queue."""
        self.queue = []
        await ctx.send("Queue has been cleared")

    #---------------------------------------------------------------------------------

    # @todo Fix
    @commands.hybrid_command(name="play")
    @app_commands.describe(
        url_or_query="The url or search query to use."
    )
    async def _play(self, ctx: commands.Context, *, url_or_query: str):
        """Plays YouTube audio from a URL or search query using yt-dlp."""
        global pbs
        await ctx.defer()

        players = await YTDLSource.from_url(url_or_query, loop=self.bot.loop, stream=True)
        for player in players:
            self.queue.append(player)
        self.prev = players[-1]

        embed: discord.Embed = discord.Embed(colour=embed_colour, description=f"{str(pbs)}x speed")

        embed.set_author(name="Playing music with yt-dlp")

        if not ctx.guild.voice_client.is_playing():
            ctx.guild.voice_client.play(self.queue[0], after=lambda e: self.after_song(ctx, e))
            embed.add_field(name="Now playing", value=f"{self.prev.data.get('uploader')} - {self.prev.title}")
        else:
            send_str = "position"
            if len(players) > 1:
                send_str += f's {len(self.queue)-len(players)} to {len(self.queue)}'
            else:
                send_str += f' {len(self.queue)}'
            embed.add_field(name="Added to queue, " + send_str, value=f"{self.prev.data.get('uploader')} - {self.prev.title}")

        embed.set_footer(text=str(datetime.timedelta(seconds=player.data.get('duration'))))

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    # @todo Fix
    @commands.hybrid_command(name="localplay")
    @commands.is_owner()
    async def _local_play(self, ctx: commands.Context, *, path):
        """Plays a song from the local filesystem."""
        await ctx.defer()
        path = os.getcwd() + "\\" + path
        print(path)
        player = await YTDLSource.from_url(path, loop=self.bot.loop, stream=False)
        self.queue.append(player)

        self.prev = player

        if not ctx.voice_client.is_playing():
            ctx.voice_client.play(path, after=lambda e: self.after_song(ctx, e))
            sendStr = '>>> **Now playing locally: '
        else:
            sendStr = f'>>> **Added local file to queue, position {len(self.queue)}'

        await ctx.send(sendStr)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="prev")
    async def _prev(self, ctx):
        """Adds the song which was just played to the queue."""
        await ctx.defer()
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.guild.me.voice.channel:
                if ctx.voice_client.is_playing():
                    if self.prev != None:
                        ctx.voice_client.stop()
                        await ctx.voice_client.play(self.prev, after=lambda e: self.after_song(ctx, e))
                        await ctx.send("**Replaying previous audio.**")
                    else:
                        raise commands.CommandError("I have not played any audio in this server since my last startup.")
                else:
                    raise commands.CommandError("No music is playing.")
            else:
                raise commands.CommandError("You are not connected to this vc.")
        else:
            raise commands.CommandError("I am not connected to a vc.")

    #---------------------------------------------------------------------------------
    
    @commands.hybrid_command(name="skip")
    async def _skip(self, ctx):
        """Skips the current song."""
        await ctx.defer()
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.guild.me.voice.channel:
                if ctx.voice_client.is_playing():
                    ctx.voice_client.stop()
                    await ctx.send(f"Done. Remaining items in queue: {str(len(self.queue))}")
                else:
                    raise commands.CommandError("No music is playing.")
            else:
                raise commands.CommandError("You are not connected to this vc.")
        else:
            raise commands.CommandError("I am not connected to a vc.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="stop")
    async def _stop(self, ctx):
        """Skips the current song and clears the queue."""
        self.queue = []
        await self._skip(ctx)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="pause")
    async def _pause(self, ctx):
        """Pauses the current song, if it isn't already paused."""
        await ctx.defer()
        if ctx.voice_client.is_playing() == True:
            ctx.voice_client.pause()
            await ctx.send(f"The player is now **paused**. Use **resume** to unpause.")
        else:
            raise commands.CommandError("The music is already paused.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="resume")
    async def _resume(self, ctx):
        """Resumes the current song, if it was paused."""
        if ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("**Resumed**")
        else:
            raise commands.CommandError("The music is not currently paused.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="playbackspeed")
    async def _playback_speed(self, ctx):
        """Displays the current audio playback speed."""
        global pbs
        await ctx.send(f"**Playback speed: `{pbs}x`**")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="setplaybackspeed")
    @app_commands.describe(playback_speed = f"The speed multiplier, in the range ({PBS_MIN}, {PBS_MAX}), exclusive.")
    @commands.has_permissions(manage_channels=True)
    async def _set_playback_speed(self, ctx: commands.Context, playback_speed: float):
        """Sets the audio playback speed. This only takes effect on the next song."""
        global pbs
        global PBS_MIN
        global PBS_MAX
        if ctx.voice_client is None:
            raise commands.CommandError("I am not connected to any voice channels.")

        elif ctx.author.voice.channel == ctx.voice_client.channel:
            # If the user is in the same channel as me...
            if PBS_MIN < playback_speed < PBS_MAX:
                pbs = playback_speed
                await ctx.send(f"**Set playback speed to `{pbs}x`. Effects will be applied on the next play command.**")
            else:
                raise commands.CommandError(f"Playback speed must be in range ({PBS_MIN}, {PBS_MAX}), exclusive.")

        else:
            raise commands.CommandError("No trooling.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="volume")
    async def _volume(self, ctx):
        """Displays the current audio volume multiplier."""
        await ctx.send(f"**Audio volume: `{ctx.voice_client.source.volume}x`**")

    #---------------------------------------------------------------------------------
                
    @commands.hybrid_command(name="setvolume")
    @app_commands.describe(volume = f"The value for the volume, in the range [{VOL_MIN}, {VOL_MAX}], inclusive.")
    async def _set_volume(self, ctx: commands.Context, volume: float):
        """Sets the audio volume multiplier."""
        global VOL_MIN
        global VOL_MAX

        if ctx.voice_client is None:
            raise commands.CommandError("I am not connected to any voice channels.")

        elif ctx.author.voice.channel == ctx.voice_client.channel:
            if VOL_MIN <= volume <= VOL_MAX:
                ctx.voice_client.source.volume = volume
            else:
                raise commands.CommandError(f"Volume must be in range [{VOL_MIN}, {VOL_MAX}], inclusive.")

        else:
            await ctx.reply("You must be in my voice channel to do this.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="join")
    async def _join(self, ctx: commands.Context):
        """Joins your voice channel."""
        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                await ctx.author.voice.channel.connect()
            
            await ctx.send("I have come.")
        else:
            raise commands.CommandError("You aren't in a voice channel.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="leave")
    async def _leave_voice(self, ctx: commands.Context):
        """Stops playing audio and disconnects from the voice channel."""
        if ctx.voice_client is not None:
            if ctx.author.voice.channel == ctx.guild.me.voice.channel:
                if ctx.voice_client.is_playing():
                    await ctx.send("The player has stopped.")
                self.queue = []
                await ctx.voice_client.disconnect()
                await ctx.voice_client.cleanup()
            else:
                raise commands.CommandError("No trooling.")
        else:
            raise commands.CommandError("I am not currently in any voice channels.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="move")
    @app_commands.describe(member = "The member to move.",
                           voice_channel = "The voice channel to move them to.")
    @commands.has_permissions(move_members=True)
    async def _move_voice(self, ctx: commands.Context, member: discord.Member, *, voice_channel: discord.VoiceChannel):
        """Attempts to move a user to a vc. Only works if they are in another vc in the same server."""
        if ctx.author.permissions_in(ctx.author.voice.channel).move_members == True:
            if member.voice is not None:
                await member.move_to(voice_channel)
            else:
                raise commands.CommandError("This member is not currently connected to any voice channel.")
        else:
            raise commands.CommandError("You do not have the `move members` permission required for this command.")

    @commands.hybrid_command(name="pull")
    @app_commands.describe(member = "The member to pull into the voice channel.")
    @commands.has_permissions(move_members=True)
    async def _pull_voice(self, ctx: commands.Context, member: discord.Member):
        """Attempts to move a member into your vc. Only works if they are in another vc in the same server."""
        if ctx.author.voice is not None:
            if ctx.author.permissions_in(ctx.author.voice.channel).move_members == True:
                if ctx.guild.me.permissions_in(ctx.author.voice.channel).move_members == True:
                    if member.voice is not None:
                        await member.move_to(ctx.author.voice.channel)
                    else:
                        raise commands.CommandError(ctx.author.name + ": This member is not currently connected to any voice channel.")
                else:
                    raise commands.CommandError(ctx.author.name + ": I do not have the `move members` permission required to pull users.")
            else:
                raise commands.CommandError(ctx.author.name + ": You do not have the `move members` permission required for this command.")
        else:
            raise commands.CommandError(ctx.author.name + ": You are not connected to a voice channel.")

    @_play.before_invoke
    async def ensure_voice(self, ctx: commands.Context):
        if ctx.author.voice: #If the user is in a voice channel...
            in_user_vc = False #Default value - if voice_client is None then it stays False.
            if ctx.guild.voice_client is not None:
                in_user_vc = ctx.guild.me.voice.channel == ctx.author.voice.channel

            if not in_user_vc:
                if ctx.guild.voice_client is None:
                    try:
                        await ctx.author.voice.channel.connect()
                    except:
                        raise commands.CommandError(f"{ctx.author.mention}, I am not permitted to play audio in that channel.")
                else: #...If I am already in a vc, then switch to their vc (as I cannot already be in their vc)
                    if ctx.guild.me.voice.channel != ctx.author.voice.channel: #... provided that I am not already in THEIR vc.
                        if ctx.guild.voice_client.is_playing(): #!!!
                            ctx.guild.voice_client.stop()
                        try:
                            await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
                        except:
                            raise commands.CommandError(f"{ctx.author.mention}, I am not permitted to play audio in that channel.")
            else:
                pass #When I am already in the user's channel.
        else:
            raise commands.CommandError("You are not connected to a voice channel.")

        self.source_channel = ctx.channel

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
