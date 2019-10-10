from datetime import datetime as d
start = d.timestamp(d.now())

import discord
import math
import sys
import random

from discord.ext import commands

cogs = ['cogs.basic','cogs.music','cogs.godmode','cogs.administrator','cogs.error_handler','cogs.sentience']

def get_prefix(bot, message):

    prefixes = ["."]

    if not message.guild:
        prefixes = ["."] #For bot commands via DMs

    return commands.when_mentioned_or(*prefixes)(bot, message) #Allow users to mention the bot instead of using a prefix when using a command.
    #Replace with 'return prefixes' to prevent mentions instead of prefix.

max_message_length = 500
master_chat = 613399504602923009
stalk_channel = 0
output_channel = 0
remove_id = 403633892680138763

# Create a new bot, set the prefix, set the description, set the Owner ID and determine whether the bot is case-sensitive or not.
bot = commands.Bot(
    command_prefix=get_prefix,
    description='Description',
    owner_id=354995879565852672,
    case_insensitive=True # The bot is not case-sensitive.
)

@bot.event
async def on_ready():
    print(f'Load time: {( d.timestamp( d.now() ) - start ) } seconds.')
    print(f'Logged in as {bot.user} [id: {bot.user.id}]')
    print(f'Latency: {bot.latency}')
    print(f'Created at: {bot.user.created_at.hour}:{bot.user.created_at.minute} {bot.user.created_at.day}/{bot.user.created_at.month}/{bot.user.created_at.year}')
    print('---Ready---')
    await bot.change_presence(activity=discord.Activity(name=f'{len(bot.users)*1337} chungas', type=3))
    for cog in cogs:
        bot.load_extension(cog)
    bot.remove_command('math')
    channel = ''
    guild = ''
    return

@bot.event
async def on_member_join(member):
    await welcome_channel.send(f'{member} [User ID: {member.id}] has joined {member.guild} [Guild ID: {member.guild.id}]')

@bot.event
async def on_member_remove(member):
    print(f'{member} [User ID: {member.id}] has left {member.guild} [Guild ID: {member.guild.id}]')

@bot.event
async def on_guild_join(guild):
    await guild.text_channels[0].send(f"I have arrived.")

@bot.event
async def on_command_completion(ctx):
    try:
        await ctx.message.add_reaction(emoji='✅')
    except:
        pass

@bot.event
async def on_message(message):
    if message.author.id != bot.user.id: #This bot's id
        stalk_channel = 'all'
        try:
            output_channel = int(bot.get_channel(master_chat).topic)
        except ValueError:
            pass
            #await bot.get_channel(master_chat).send("Output channel ID invalid.")

        await bot.process_commands(message)

    if message.author.id == remove_id: #Removes messages
        if random.randint(1,5) == 5:
            await message.delete()
            await bot.get_guild(584487882799054849).get_channel(586216189517234304).send(f"[{message.guild}][<#{message.channel.id}>][{message.author}]: '{message.content}' was deleted.")

    if message.channel.id == master_chat and message.author != bot.user:
        try:
            await bot.get_channel(output_channel).send(message.content)
        except NameError:
            await bot.get_channel(master_chat).send("Output Channel is not defined.")

#@bot.command()
#async def scopeto(ctx):
#    message = ctx.message
#    channel = message.channel
#    await channel.send("Hi")
#    print(channel)

bot.run('NjIxNzQxNTc2OTAwNTc1Mjcz.XZ-K9w.ccbcgQXMxOyO3-OnseQYI2CSSQk', bot=True, reconnect=True)
