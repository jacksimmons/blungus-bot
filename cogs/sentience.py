import discord
import random
import csv
import json
from discord.ext import commands

registered_inputs = []
banned_chars = ["", "\n"]

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
                responses = []
                with open("data/messages.csv", "r") as f:
                    reader = csv.reader(f, delimiter=",", quotechar="|")
                    for row in reader:
                        if row != []:
                            print(row)
                            messages.append(row[0])
                            responses.append(row[1])

                send_response = False
                content = message.content

                if content in messages: # Search for the message in messages
                    send_response = True
                    if messages.count(content) == 1:
                        if not (messages.index(content) == len(responses) - 1):
                            response = responses[messages.index(content)]
                        else:
                            # Reached the end of the read conversation
                            send_response = False
                    else:
                        indices = find_indices(messages, content)
                        index = random.choice(indices)
                        if not (index == len(messages) - 1):
                            response = responses[index]
                        else:
                            # The random choice was the final message! So just pick another.
                            indices.pop(index)
                            response = responses[indices[0]]

                else: #If the message is not recognised
                    with open("data/messages.csv") as f:
                        f.write(content)
                    send_response = False # We need to wait for a response to learn what a valid response to that message is.

                if response is not None:
                    if send_response == True:
                        response.replace('@everyone', '@ everyone')
                        response.replace('@here', '@ here')
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
                data[str(guild_id)] = {}
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
    async def _feed(self, ctx, channel_id:int, limit:int=None):
        target = self.bot.get_channel(channel_id)
        await ctx.send(f"Preparing feast from {target.mention}.")

        messages = [message async for message in target.history(limit=limit)]
        messages.reverse()
        read_messages = []

        await ctx.send(f"Feast has been prepared. Feeding from channel {target.mention}.")
        reading_msg = await ctx.send("Reading messages from chat...")

        for i in range(0, len(messages)):
            content = messages[i].content
            if content not in ["", "\n"]:
                read_messages.append(content)

        await reading_msg.edit(content="Reading messages from chat... **Done**")
        writing_msg = await ctx.send("Writing messages to file...")

        with open("data/messages.csv", "w") as f:
            writer = csv.writer(f, delimiter=',', quotechar="|")
            for i in range(0, len(read_messages) - 1):
                try:
                    writer.writerow([read_messages[i], read_messages[i+1]])
                except:
                    pass
        
        lines = []
        with open("data/messages.csv", "r") as f:
            lines = f.readlines()
            for line in lines:
                if line in banned_chars:
                    lines.remove(line)
        
        with open("data/messages.csv", "w") as f:
            f.write(lines)

        await writing_msg.edit(content="Writing messages... **Done**")
        await ctx.send("Feeding complete.")

async def setup(bot):
    await bot.add_cog(Sentience(bot))
