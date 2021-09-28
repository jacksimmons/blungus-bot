import discord
from discord.ext import commands

import json

min_messages = 1
max_messages = 10

class Godmode(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

    @commands.command(
        name='setstatus',
        description='Changes the bot\'s discord presence [may take a while]',
        aliases=[]
    )

    @commands.is_owner()
    async def set_status(self, ctx, status: str, afk: bool=None):

        if status == 'online':
            await self.bot.change_presence(status=discord.Status.online, afk=afk)

        elif status == 'offline':
            await self.bot.change_presence(status=discord.Status.offline, afk=afk)

        elif status == 'idle':
            await self.bot.change_presence(status=discord.Status.idle, afk=afk)

        elif status == 'dnd':
            await self.bot.change_presence(status=discord.Status.dnd, afk=afk)

        elif status == 'invisible':
            await self.bot.change_presence(status=discord.Status.invisible, afk=afk)

        else:
            await ctx.send("Invalid status entered.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='setgame',
        description='Sets the bot\'s current game and its details.',
        aliases=[]
    )

    @commands.is_owner()
    async def set_game(self, ctx, name: str): #try to add start and end
        await self.bot.change_presence(activity=discord.Game(name=name))

    #---------------------------------------------------------------------------------

    @commands.command(
        name='setstream',
        description='''Sets the bot\'s current stream and its details.
        This will default to an empty activity when a twitch.tv url is not passed.''',
        aliases=[]
    )

    @commands.is_owner()
    async def set_stream(self, ctx, name: str,  url: str=None, details: str=None, twitch_name: str=None):
        await self.bot.change_presence(activity=discord.Streaming(name=name, details=details, url=url, twitch_name=twitch_name))

    #---------------------------------------------------------------------------------

    @commands.command(
        name='setactivity',
        description='''Sets the bot\'s current activity and its details.
        The Game activity requires [name], [type=0]
        The Streaming activity requires [name], [type=1] and [url]
        The Listening activity requires [name], [type=2]
        The Watching activity requires [name], [type=3]''',
        aliases=[]
    )

    @commands.is_owner()
    async def set_activity(self, ctx, name: str, type: int, url: str=None, details: str=None, state: str=None, application_id: int=None):
        if 0 <= type <= 3:
            await self.bot.change_presence(activity=discord.Activity(name=name, type=type, application_id=application_id, url=url, state=state, details=details))
        else:
            raise BadArgument(f"There is no activity type {type}.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='createguild',
        description='Creates a guild. Bots cannot create guilds if they are already in at least 10 guilds.',
        aliases=[]
    )

    @commands.is_owner()
    async def createguild(self, ctx, name: str, region: discord.VoiceRegion=None, icon: bytes=None):
        await self.bot.create_guild(name=name, region=region, icon=icon)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='broadcast',
        description=f'''Broadcasts a specific message a number of times to a specific channel.
        Takes 3 arguments:
                           channel [discord.TextChannel]- the channel you are sending this message to
                           quantity [integer] - the number of times this message is to be sent (min: {min_messages}, max: {max_messages})
                           message [string] - what you want the bot to send''',
        aliases=['broad']
    )

    @commands.is_owner()
    async def broadcast_command(self, ctx, channel_id: int, quantity: int, *, message: str):
        channel = self.bot.get_channel(channel_id)
        i = 0
        msg = await ctx.send(f"Broadcasting '{message}' {quantity} times to Channel <#{channel.id}>, {ctx.message.author}.")
        while i < quantity:
            await channel.send(message)
            i += 1
        await msg.delete()


    @commands.command(name='mess', aliases=['m'])
    @commands.is_owner()
    async def mess(self, ctx, *, arg): #Command for testing
        with open('data.json', 'r') as file:
            all_data = json.load(file)
        all_data['guilds']['id'] = {}
        all_data['guilds']['id']['name'] = arg

        with open('data.json', 'w') as outfile:
            json.dump(all_data, outfile, indent=4)

    #---------------------------------------------------------------------------------

    @commands.command(name='eval', description='Evaluate and run python code')
    @commands.is_owner()
    #https://stackoverflow.com/questions/44859165/async-exec-in-python
    async def evaluate(self, ctx, *, code):
        try:
            # Make an async function with the code and `exec` it
            exec(
                f'async def __ex(self, ctx): ' +
                ''.join(f'\n {l}' for l in code.split('\n'))
            )

            # Get `__ex` from local variables, call it and return the result
            return await locals()['__ex'](self, ctx)
        except Exception as e:
            if len(str(e)) <= 2000:
                await ctx.send(f"{type(e)}: {e}")
            else:
                await ctx.send(f"{type(e)}: Check the console.")


    #---------------------------------------------------------------------------------

    @commands.command(
        name='guildlist',
        description='Returns the list of guilds I am a member of',
        aliases=['serverlist']
    )

    @commands.is_owner()
    async def guild_list(self, ctx):
        guilds = ''
        for x in range(0, len(self.bot.guilds)):
            if guilds == '':
                guilds = self.bot.guilds[x].name
            else:
                guilds += ", " + self.bot.guilds[x].name
        await ctx.send(guilds)

    @commands.command(
        name='deleteguild',
        description='Deletes one of the guilds the bot is an owner of',
        aliases=[]
    )

    @commands.is_owner()
    async def del_guild(self, ctx, guild: int):
        await guild.delete()
        await ctx.send(f"Deleted {guild}")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='quit',
        description='Shuts down the bot.',
		aliases=['exit']
    )

    @commands.is_owner()
    async def quit_command(self, ctx):
        await ctx.send("Quitting...")
        await self.bot.close()

    #---------------------------------------------------------------------------------

def setup(bot):
    bot.add_cog(Godmode(bot))
