from datetime import datetime as d
#'start' is to be determined as early as possible so module loading times do not affect
#the load time displayed when the script has loaded.
start = d.timestamp(d.now())

#Import the discord module
import discord
import random
import json

#Import 'commands' which allows the creation of commands that are 'invoked' by a certain keyword
#e.g. 'help', which displays the default help command. This keyword must have the 'prefix' before it
#for example if the prefix is '.', then the command would be activated by sending '.help' in a Discord
#channel that the bot has access to and can send messages to.
from discord.ext import commands

cogs = ['cogs.miscellaneous','cogs.music','cogs.godmode','cogs.administrator','cogs.information','cogs.error_handler']

global efpe
efpe = 0

def get_prefix(bot, message):

    prefixes = ["."]

    if not message.guild:
        prefixes = ["."] #For bot commands via DMs

    return commands.when_mentioned_or(*prefixes)(bot, message) #Allow users to mention the bot instead of using a prefix when using a command.
    #Replace with 'return prefixes' to prevent mentions instead of prefix.

intents = discord.Intents.all()

# Create a new bot, set the prefix, set the description, set the Owner ID and determine whether the bot is case-sensitive or not.
bot = commands.Bot(
    command_prefix=get_prefix, # Set the command prefix equal to the prefix defined earlier
    description='Description', # Set the description to describe what the bot does
    owner_id=354995879565852672, # Set the Owner ID so the bot knows who the owner is
    case_insensitive=True, # The bot is not case-sensitive
    intents=intents
)

@bot.event
async def on_ready():
    print(f'Load time: {( d.timestamp( d.now() ) - start ) } seconds.')
    print(f'Logged in as {bot.user} [id: {bot.user.id}]')
    print(f'Latency: {bot.latency}')
    print(f'Created at: {bot.user.created_at.hour}:{bot.user.created_at.minute} {bot.user.created_at.day}/{bot.user.created_at.month}/{bot.user.created_at.year}')
    print('---Ready---')
    await bot.change_presence(activity=discord.Activity(name=f'{(len(bot.users)*4201337)}i chungas', status=discord.Status.offline, type=3))
    for cog in cogs:
        bot.load_extension(cog)
    return

@bot.event
async def on_member_join(member):
    import os
    os.chdir('../bot_mode')
    with open('data/guilds.json', 'r') as file:
        theguild = json.load(file)[str(member.guild.id)]

        if 'channels' in theguild:
            if 'welcome' in theguild['channels']:
                try:
                    await member.guild.get_channel(theguild['channels']['welcome']).send(f'{member} [{member.mention}] has joined the server.')
                except discord.Forbidden:
                    pass #Nothing we can do about this

@bot.event
async def on_member_remove(member):
    import os
    os.chdir('../bot_mode')
    with open('data/guilds.json', 'r') as file:
        theguild = json.load(file)[str(member.guild.id)]

        if 'channels' in theguild:
            if 'welcome' in theguild['channels']: #Not required but included just in case
                try:
                    await member.guild.get_channel(theguild['channels']['welcome']).send(f'{member} [{member.mention}] has left the server.')
                except discord.Forbidden:
                    pass #Nothing we can do about this

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.TextChannel):
        if message.author != bot.user:
            if message.guild.me.permissions_in(message.channel).send_messages:
                #This code checks whether the bot has the permission 'send messages' in the current channel
                #If the bot can see this message, then it must have the 'read messages' command.
                #It can be assumed that if a member doesn't want the bot to talk in their channel, then they won't
                #want commands to be able to be used from that channel.
                await bot.process_commands(message)
                #This is to prevent spam of the discord API (invalid requests being sent)
                if message.author.id == 267395298370781194:
                    with open("data/data.json", "r") as file:
                        try:
                            insult = random.choice(json.load(file)["trolliliyan"]["insults"])
                            await message.channel.send(insult)
                            await message.add_reaction(await message.guild.fetch_emoji('882070759869120593'))
                        except:
                            pass
        
    else:
        await bot.process_commands(message)

#The bot-specific token used to log into Discord. A different application will have a different token,
#and this token is not specific to this code but to the bot account itself (this can change).
bot.run('NjIxNzQxNTc2OTAwNTc1Mjcz.XXpv9w.gwh8PFVfPSNgSFWeTJ86PW9ZqKQ', bot=True, reconnect=True)
