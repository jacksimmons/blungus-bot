import asyncio
import discord
import json
import os
import dotenv
import math

from datetime import datetime as d
from discord.ext import commands

# Set the starting timestamp.
start = d.timestamp(d.now())

# Define cogs. For a cog to be used it must be here.
cogs = [
    'cogs.admin',
    'cogs.error_handler',
    'cogs.fun',
    'cogs.godmode',
    'cogs.info',
    'cogs.math',
    'cogs.miscellaneous',
    'cogs.music',
    'cogs.sentience',
    'cogs.server'
    ]

# The intents of the bot - what it intends to do.
intents = discord.Intents.all()

# All valid prefixes which can be used to call commands.
prefixes = ["."]

def get_prefix(bot: commands.Bot, message: str):
    return commands.when_mentioned_or(*prefixes)(bot, message) #Allow users to mention the bot instead of using a prefix when using a command.
    #Replace with 'return prefixes' to prevent mentions instead of prefix.

# Create a new bot with the following parameters.
bot = commands.Bot(
    command_prefix=get_prefix,
    description='Description',
    owner_id=354995879565852672,
    case_insensitive=True,
    intents=intents
)

# Load the cogs.
async def load_extensions():
    for cog in cogs:
        await bot.load_extension(cog)

# Start the bot (load extensions, then start the bot)
async def main(token: str):
    async with bot:
        await load_extensions()
        await bot.start(token, reconnect=True)

@bot.event
async def on_ready():
    print(f'Load time: {( d.timestamp( d.now() ) - start ) } seconds.')
    print(f'Logged in as {bot.user} [id: {bot.user.id}]')
    print(f'Latency: {bot.latency}')
    print(f'Created at: {bot.user.created_at.hour}:{bot.user.created_at.minute} {bot.user.created_at.day}/{bot.user.created_at.month}/{bot.user.created_at.year}')
    print('---Ready---')
    await bot.change_presence(activity=discord.Activity(name=f'{len(bot.users)} chungi', status=discord.Status.idle, type=discord.ActivityType.watching))

@bot.event
async def on_member_join(member):
    with open('data/guilds.json', 'r') as file:
        guild = json.load(file)[str(member.guild.id)]

        if 'channels' in guild:
            if 'welcome' in guild['channels']:
                try:
                    await member.guild.get_channel(guild['channels']['welcome']).send(f'{member} [{member.mention}] joined.')
                except discord.Forbidden:
                    pass #Nothing we can do about this

@bot.event
async def on_member_remove(member):
    with open('data/guilds.json', 'r') as file:
        guild = json.load(file)[str(member.guild.id)]

        if 'channels' in guild:
            if 'welcome' in guild['channels']: #Not required but included just in case
                try:
                    await member.guild.get_channel(guild['channels']['welcome']).send(f'{member} [{member.mention}] left.')
                except discord.Forbidden:
                    pass #Nothing we can do about this


# Entry Point
if __name__ == "__main__":
    dotenv.load_dotenv()
    token = os.getenv("TOKEN")
    if token is None:
        print("No token provided. See README for more info.")
    else:
        asyncio.run(main(token))