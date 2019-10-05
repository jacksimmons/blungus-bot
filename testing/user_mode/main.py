from datetime import datetime as d
start = d.timestamp(d.now())

import discord
import sys

from discord.ext import commands

watch_channels = 'all'
max_message_length = 2000

remove_id = 403633892680138763

cogs = []

def get_prefix(bot, message):

    prefixes = ["."]

    if not message.guild:
        prefixes = ["."] #For bot commands via DMs

    return commands.when_mentioned_or(*prefixes)(bot, message) #Allow users to mention the bot instead of using a prefix when using a command.
    #Replace with 'return prefixes' to prevent mentions instead of prefix.

# Create a new bot, set the prefix, set the description, set the Owner ID and determine whether the bot is case-sensitive or not.
bot = commands.Bot(
    command_prefix=get_prefix,
    description='User Mode',
    owner_id=354995879565852672,
    case_insensitive=True # The bot is not case-sensitive.
)

@bot.event
async def on_ready():
    print(f'Load time: {( d.timestamp( d.now() ) - start ) } seconds.')
    print(f'Logged in as {bot.user} [id: {bot.user.id}] [USER MODE]')
    print(f'Latency: {bot.latency}')
    print(f'Created at: {bot.user.created_at.hour}:{bot.user.created_at.minute} {bot.user.created_at.day}/{bot.user.created_at.month}/{bot.user.created_at.year}')
    print('---Ready---')
    #for cog in cogs:
    #    bot.load_extension(cog)
    return

@bot.event
async def on_message(message):
    if message.author.id == remove_id: #Removes messages
        await message.delete()
        await bot.get_guild(584487882799054849).get_channel(586216189517234304).send(f"[{message.guild}][<#{message.channel.id}>][{message.author}]: '{message.content}' was deleted.")
    if watch_channels == 'all':
        print_content = ''
        if message.author.bot == True:
            print_content += '[BOT]'
        if message.tts == True:
            print_content += '[tts]'
        if message.mention_everyone == True:
            print_content += '[@]'
        if len(message.content) <= max_message_length:
            print_content += f'[{message.guild.name} <#{message.channel.id}>] [{message.created_at}] [{message.id}] [{message.author}]: {message.content}'
        elif len(message.content) > max_message_length:
            print_content += f'[{message.guild.name} <#{message.channel.id}>] [{message.created_at}] [{message.id}] [{message.author}] [Long message]'
        print(print_content)

#@bot.command()
#async def scopeto(ctx):
#    message = ctx.message
#    channel = message.channel
#    await channel.send("Hi")
#    print(channel)

bot.run('NjIxNzQxNTc2OTAwNTc1Mjcz.XXpwPQ.O3gLeqbxtwH5AVBb_8TYqwuFBTU', bot=True, reconnect=True)
