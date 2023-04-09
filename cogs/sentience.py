import discord
import random
import csv
import json
from discord.ext import commands

registered_inputs = []

def find_indices(list, item):
    indices = []
    for idx, value in enumerate(list):
        if value == item:
            indices.append(idx)
    return indices

def get_message_content(msg):
    content = msg.content
    first_attachment = True
    for atm in msg.attachments:
        if first_attachment:
            content += atm.url
            first_attachment = False
        else:
            content += " " + atm.url
    return content

class Sentience(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.TextChannel) and message.author.id != self.bot.user.id:
            guild_id = message.guild.id

            with open('data/guilds.json', 'r') as f: #Determines speaking_zone value; this is set to 0 if a channel was not found in 'guilds.json'
                data = json.load(f)

                speaking_zone = None

                if str(guild_id) in data:
                    if 'channels' in data[str(guild_id)]:
                        if 'chatbot' in data[str(guild_id)]['channels']:
                            speaking_zone = data[str(guild_id)]['channels']['chatbot']

            log_response = False
            response = None
            send_response = False

            if message.channel.id == speaking_zone:
                messages = []
                with open('data/guilds.json', 'r') as f:
                    guilds = json.load(f)
                    if str(message.guild.id) not in guilds:
                        guilds[str(guild_id)] = {}
                    if "sentience" not in guilds[str(guild_id)]:
                        guilds[str(guild_id)]["sentience"] = []
                    messages = guilds[str(guild_id)]["sentience"]

                send_response = False
                content = message.content
                print(messages)
                print(content)
                if content in messages: # Search for the message in messages
                    send_response = True
                    if messages.count(content) == 1:
                        if not (messages.index(content) == len(messages) - 1):
                            response = messages[messages.index(content) + 1]
                        else:
                            # Reached the end of the read conversation
                            send_response = False
                    else:
                        indices = find_indices(messages, content)
                        index = random.choice(indices)
                        if not (index == len(messages) - 1):
                            response = messages[index + 1]
                        else:
                            # The random choice was the final message! So just pick another.
                            indices.pop(index)
                            response = messages[indices[0] + 1]

                else: #If the message is not recognised
                    with open("data/guilds.json", "w") as f:
                        # We know "sentience" was previously added to the guild data.
                        sentience = guilds[str(guild_id)]["sentience"]
                        sentience.append(content)
                        guilds[str(guild_id)]["sentience"] = sentience
                        json.dump(guilds, f, indent=4)
                    send_response = False # We need to wait for a response to learn what a valid response to that message is.

                if response is not None:
                    if send_response == True:
                        #response.replace('@everyone', '@ everyone')
                        #response.replace('@here', '@ here')
                        await message.channel.send(response)

    @commands.guild_only()
    @commands.command(name='setchatchannel', help='Sets the channel that the bot will respond to your messages in.')
    async def _setchatchannel(self, ctx, channel_id:int):
        with open('data/guilds.json', 'r+') as f:
            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(f)
            guild_id = ctx.guild.id

            f.seek(0) # Reset file position to the beginning

            if str(guild_id) in data:
                if 'channels' not in data[str(guild_id)]:
                    data[str(guild_id)]['channels'] = {}
                data[str(guild_id)]['channels']['chatbot'] = channel_id

            else:
                data[str(guild_id)]['channels'] = {}
                data[str(guild_id)]['channels']['chatbot'] = channel_id

            json.dump(data, f, indent=4)

            f.truncate() #Remove remaining part

        await ctx.send(f'Chat channel has been set to {self.bot.get_channel(channel_id).mention}!')

    @commands.command(name='removechatchannel', help='Removes the channel that the bot previously used for responding to your messages in, if there was one.')
    async def _removechatchannel(self, ctx):
        with open('data/guilds.json', 'r+') as f: #Determines speaking_zone value; this is set to 0 if a channel was not found in 'guilds.json'
            #Using 'r+' mode to allow writing and reading to the file.
            #Sources: see '_setchatchannel' (above)
            data = json.load(f)
            guild_id = ctx.guild.id

            f.seek(0) # Reset file position to the beginning

            if str(guild_id) in data:
                data[str(guild_id)]['channels'].pop('chatbot', None)
                #This removes the need to check if this variable exists;
                #If there is a 'bot_chat_channel', it will get removed.
                #If not, it will remove None, which removes nothing.
                #Source: https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary
            json.dump(data, f, indent=4)

            f.truncate() # Remove remaining part

        await ctx.send('Chat channel disabled.')

    @commands.guild_only()
    @commands.command(name='feed', help='Feeds the bot all of the inputs and responses from a specific channel.')
    @commands.is_owner()
    async def _feed(self, ctx, channel_id:int=None):
        target = self.bot.get_channel(channel_id)
        await ctx.send(f"Preparing feast from {target.mention}.")

        messages = await target.history(limit=None).flatten()
        messages.reverse() # So that the most recent message is at the end of the list
        read_messages = []

        ids = [Message.id for Message in messages]

        #The following code is based on the fact that the message ID with index '0' is the most recent message that was sent

        await ctx.send(f"Feast has been prepared. Feeding from channel {target.mention}.")

        m = await ctx.send("Reading messages from chat...")

        for x in range(0, len(ids)):
            print("Reading messages: " + str(x) + f'/{len(ids)}')

            msg = await target.fetch_message(ids[x])
            content = get_message_content(msg)

        await m.edit(content="Reading messages from chat... **Done**")

        n = await ctx.send("Writing messages to file...")

        with open('data/guilds.json', 'r') as f:
            guilds = json.load(f)
            if str(ctx.guild.id) not in guilds:
                guilds[str(ctx.guild.id)] = {}
            if "sentience" not in guilds[str(ctx.guild.id)]:
                guilds[str(ctx.guild.id)]["sentience"] = []
            prev_messages = guilds[str(ctx.guild.id)]["sentience"]

        with open("data/guilds.json", "w") as f:
            prev_messages.extend(read_messages)
            guilds[str(ctx.guild.id)]["sentience"] = prev_messages
            json.dump(guilds, f, indent=4)
        print("Done")

        await n.edit(content="Writing messages... **Done**")
        await ctx.send("Feeding complete.")

async def setup(bot):
    await bot.add_cog(Sentience(bot))
