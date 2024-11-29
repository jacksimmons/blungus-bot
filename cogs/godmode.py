import sys
import discord

from typing import Literal, Optional
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy, Context

import json


class Godmode(commands.Cog):

    def __init__(self, bot):
        self.bot:commands.Bot = bot

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="setpresence")
    @app_commands.describe(status = "The message displayed on the bot's profile. E.g. 'Verbing [x]'",
                           activity_type = "The activity type displayed with the status. E.g. '[Verbing] x'",
                           name = "The name of the activity.",
                           url = "Optional URL which can be provided for activites like 'streaming'.")
    @commands.is_owner()
    async def set_presence(self, ctx: Context,
                           status:str,
                           activity_type:Literal['playing', 'streaming', 'watching', 'listening', 'competing', 'custom'],
                           name:str,
                           url:str=None):
        'Changes the bot\'s discord presence [may take a while]'
        if activity_type == "playing":
            final_activity_type = discord.ActivityType.playing
        elif activity_type == "streaming":
            final_activity_type = discord.ActivityType.streaming
        elif activity_type == "watching":
            final_activity_type = discord.ActivityType.watching
        elif activity_type == "listening":
            final_activity_type = discord.ActivityType.listening
        elif activity_type == "competing":
            final_activity_type = discord.ActivityType.competing
        elif activity_type == "custom":
            final_activity_type = discord.ActivityType.custom
        else:
            final_activity_type = discord.ActivityType.unknown
        
        await self.bot.change_presence(status=status, activity=discord.Activity(name=name, type=final_activity_type, url=url))


    #---------------------------------------------------------------------------------


    @commands.hybrid_command(name='setstream')
    @app_commands.describe(url = "The URL of the stream.",
                           name = "The name of the stream.",
                           game = "The name of the game being streamed.")
    @commands.is_owner()
    async def set_stream(self, ctx: Context, url: str, name: str=None, game: str=None):
        '''Sets the bot\'s current stream and its details.'''
        await self.bot.change_presence(activity=discord.Streaming(name=name, game=game, url=url))


    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='setgame')
    @app_commands.describe(name = "The name of the game to set as being played.")
    @commands.is_owner()
    async def set_game(self, ctx: Context, name: str): #@todo try to add start and end
        await self.bot.change_presence(activity=discord.Game(name=name))

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='createguild')
    @app_commands.describe(name = "Name of the guild.", icon = "An image for the guild's icon.")
    @commands.is_owner()
    async def create_guild(self, ctx: Context, name: str, icon: discord.Attachment=None):
        'Creates a guild. Bots cannot create guilds if they are already in at least 10 guilds.'
        try:
            guild = await self.bot.create_guild(name=name, icon=icon)
            await ctx.send(f"The guild `{name}` has been created, with id {guild.id}.")
        except:
            raise commands.CommandError(f"I can't make a new guild, because I am already in `{len(self.bot.guilds)}` guilds.")

        # Send the user an invite to the new guild
        channel = await guild.create_text_channel("general")
        invite = await channel.create_invite()
        await ctx.send(f"Invite:\n{invite.url}")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='gimmerole')
    @app_commands.describe(
        role = "The role to give out.",
        member = "The member to give the role to."
    )
    @commands.is_owner()
    async def gimme_role(self, ctx: Context, role: discord.Role, member: discord.Member=None):
        'In a guild the bot has permission to give the role in, gives the role to a member.'
        if member:
            await member.add_roles(role)
        else:
            await ctx.author.add_roles(role)

        await ctx.send(f"Added role to {member.discriminator}: {role.mention}.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='createadminrole')
    @commands.is_owner()
    async def create_admin_role(self, ctx: Context):
        'Creates an admin role in a guild the bot owns.'
        guild = ctx.guild
        admin_role = await guild.create_role(name="Admin", permissions=discord.Permissions.all(), reason="Requested by bot owner.")
        await ctx.send(f"Created role {admin_role.mention}")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='bc')
    @app_commands.describe(
        channel_id = "The channel ID you are sending this message to (any channel the bot has access to).",
        quantity = "The number of times to broadcast this message.",
        message = "The message to broadcast."
    )
    @commands.is_owner()
    async def broadcast_command(self, ctx: Context, channel_id: int, quantity: int, *, message: str):
        '''Broadcasts a specific message a number of times to a specific channel.'''
        channel = self.bot.get_channel(channel_id)
        msg = await ctx.send(f"Broadcasting '{message}' {quantity} times to Channel <#{channel.id}>.")
        for _ in range(quantity):
            await channel.send(message)
        await msg.delete()


    @commands.hybrid_command(name='mess')
    @app_commands.describe(
        arg = "Testing arg"
    )
    @commands.is_owner()
    async def mess(self, ctx: Context, *, arg): #Command for testing
        "Command for testing."
        with open('data.json', 'r') as file:
            all_data = json.load(file)
        all_data['guilds']['id'] = {}
        all_data['guilds']['id']['name'] = arg

        with open('data.json', 'w') as outfile:
            json.dump(all_data, outfile, indent=4)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='eval')
    @app_commands.describe(
        code = "The code to execute."
    )
    @commands.is_owner()
    #https://stackoverflow.com/questions/44859165/async-exec-in-python
    async def evaluate(self, ctx: Context, *, code: str):
        'Evaluate and run python code'
        try:
            # Make an async function with the code and `exec` it
            exec(
                f'async def __ex(self, ctx: Context): ' +
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

    @commands.hybrid_command(name='guildcount')
    @commands.is_owner()
    async def guild_count(self, ctx: Context):
        'Returns the number of guilds the bot is a member of.'
        await ctx.send(f"I am in `{len(self.bot.guilds)}`.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='guildlist')
    @commands.is_owner()
    async def guild_list(self, ctx: Context):
        'Returns a list of guilds the bot is a member of.'
        guilds = ''
        for x in range(0, len(self.bot.guilds)):
            if guilds == '':
                guilds = self.bot.guilds[x].name + f" [{self.bot.guilds[x].id}]"
            else:
                guilds += ", " + self.bot.guilds[x].name + f" [{self.bot.guilds[x].id}]"
        await ctx.send(guilds)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='deleteguild')
    @app_commands.describe(
        guild = "Guild ID of the guild to delete"
    )
    @commands.is_owner()
    async def del_guild(self, ctx: Context, guild: int):
        'Deletes a guild the bot is an owner of'
        await self.bot.get_guild(guild).delete()
        await ctx.send(f"Deleted {guild}")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name='quit')
    @commands.is_owner()
    async def quit_command(self, ctx: Context):
        'Shuts down the bot.'
        await ctx.send("Quitting...")
        await self.bot.close()
        sys.exit(0)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="sync")
    @commands.is_owner()
    async def _sync(self, ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
        "Syncs slash commands."
        if not guilds:
            if spec == "~":
                synced = await self.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                self.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                self.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        ret = 0
        for guild in guilds:
            await self.bot.tree.sync(guild=guild)
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Godmode(bot))
