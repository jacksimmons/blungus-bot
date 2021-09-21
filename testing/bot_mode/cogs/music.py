import asyncio

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
    def __init__(self, source, *, data, volume=1):
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
        self.source_channel = None
        self.bound_member = None
        self.queue = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild = member.guild
        if guild.voice_client is not None:
            if guild.voice_client.channel is not None:
                print(guild.voice_client.channel.name)
                if before.channel != after.channel:
                    if member == self.bound_member:
                        if after.channel is None:
                            await guild.voice_client.disconnect()
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

    def after_song(self, ctx, e):
        print("Player error % e", e)
        self.queue.pop(0)
        if len(self.queue) > 0:
            ctx.voice_client.play(player, after=lambda e: self.after_song(ctx,e))

    @commands.command()
    async def join(self, ctx):
        """Joins your voice channel"""

        if ctx.author.voice is not None:
            if ctx.voice_client is not None:
                return await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                await ctx.author.voice.channel.connect()
        else:
            raise commands.CommandError(f"{ctx.author.mention}, you are not currently connected to a voice channel.")

    @commands.command(
        name="skip",
        description="Skips the current song.")

    async def skip(self, ctx):
        async with ctx.typing():
            await ctx.voice_client.stop()
            self.after_song(ctx, None)
            await ctx.send(">>>**Skipped.")

    @commands.command(
        name="play",
        description="Plays from a url (almost anything youtube_dl supports)",
        aliases=['p'])

    async def play(self, ctx, *, url):
        async with ctx.typing():
            stream = False # Will the play command download to computer or stream it?

            data = await self.bot.loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

            if 'entries' in data:
                # take first item from a playlist
                data = data['entries'][0]

            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            self.queue.append(player)

            if len(self.queue) == 1:
                ctx.voice_client.play(player, after=lambda e: self.after_song(ctx,e))
                await ctx.send(f'''>>> **Now playing: `{data['title']}` by `{data['uploader']}`
Duration: `{str(datetime.timedelta(seconds=data['duration']))}` **''')

            else:
                await ctx.send(f'''>>> **Added to queue [Position {len(self.queue)}]: `{data['title']}` by `{data['uploader']}`
Duration: `{str(datetime.timedelta(seconds=data['duration']))}` **''')

    @commands.command()
    async def pause(self, ctx):
        """Pauses the current video"""
        if ctx.voice_client.is_playing() == True:
            ctx.voice_client.pause()

            await ctx.send(f"The player is now **paused**. Use **resume** to unpause.")

        else:
            raise commands.CommandError("The music is already paused.")

    @commands.command()
    async def resume(self, ctx):
        """Resumes the current video"""
        if ctx.voice_client.is_paused() == True:
            ctx.voice_client.resume()

            await ctx.send("**Resumed**")
        else:
            raise commands.CommandError("The music is not currently paused.")

    @commands.command(name='volume', aliases=['v','vol'])
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            raise commands.CommandError("I am not connected to any voice channels.")

        elif ctx.author.voice.channel == ctx.voice_client.channel:
            if 0 < volume < 200:
                await ctx.send(f"Changed volume to {volume}%")
            elif volume >= 200:
                await ctx.send(f"Changed volume to 200% (Maximum)")
                volume = 200
            else:
                await ctx.send(f"Changed volume to 0% (Minimum)")
                volume = 0

            ctx.voice_client.source.volume = volume / 100

        else:
            raise commands.CommandError("No music currently playing.")

    @commands.command()
    async def bind(self, ctx):
        """Binds the music bot to you, so when you join a new voice channel, it will follow you.
        While you are the bound member, you have a lot of control over the bot's voice status."""

        if ctx.author.voice is not None:

            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            else:
                await ctx.author.voice.channel.connect()

            self.bound_member = ctx.author
            self.source_channel = ctx.channel

            await ctx.send(f"I am now bound to you, {ctx.author.name}. If you **disconnect**, I will become unbound from you, but feel free to **move** from one voice channel to another.")
        else:
            raise commands.CommandError("You aren't connected to a voice channel.")

    @commands.command()
    async def unbind(self, ctx):
        """Unbinds any bound member that may exist."""

        if self.bound_member is not None:
            self.bound_member = None
            await ctx.send("I am no longer bound to anyone.")
        else:
            raise commands.CommandError(f"{ctx.author.mention}, I am not currently bound to anyone.")

    @commands.command()
    async def leave(self, ctx):
        """Stops and disconnects the bot from voice"""

        if self.bound_member is not None:
            await ctx.send(f"I am no longer bound to {ctx.author.name}.")
            self.bound_member = None

        if ctx.voice_client is not None:
            if ctx.voice_client.is_playing():
                await ctx.send("The player has stopped.")

        await ctx.voice_client.disconnect()

    @commands.command(
        name='move',
        help='Moves a member into a different voice channel.'
    )

    async def v_move(self, ctx, member: discord.Member, *, channel: discord.VoiceChannel):
        if ctx.author.permissions_in(ctx.author.voice.channel).move_members == True:
            if member.voice is not None:
                await member.move_to(channel)
            else:
                raise commands.CommandError("This member is not currently connected to any voice channel.")
        else:
            raise commands.CommandError("You do not have the `move members` permission required for this command.")

    @commands.command(
        name='pull',
        help='Pulls a member into your current voice channel.',
        aliases=['summon']
    )

    async def _pull(self, ctx, member: discord.Member):
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

    async def ensure_voice(self, ctx):
        if ctx.author.voice:
            if ctx.guild.me.permissions_in(ctx.author.voice.channel).connect == True:
                if ctx.guild.me.permissions_in(ctx.author.voice.channel).speak == True:
                    if ctx.voice_client is None:
                        await ctx.author.voice.channel.connect()
                    else:
                        if ctx.voice_client.is_playing():
                            ctx.voice_client.stop()
                        await ctx.voice_client.move_to(ctx.author.voice.channel)
                else:
                    raise commands.CommandError(f"{ctx.author.name}, I am not permitted to play audio in that channel.")
            else:
                raise commands.CommandError(f"{ctx.author.name}, I am not permitted to join that channel.")

        else:
            raise commands.CommandError("You are not connected to a voice channel.")

        self.source_channel = ctx.channel

def setup(bot):
    bot.add_cog(Music(bot))
