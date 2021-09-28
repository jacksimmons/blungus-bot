import discord
import random
import csv
import json
from base import Base
from discord.ext import commands

registered_inputs = []

class CleverChungus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    speaking_zone = None
    wait_for_response = False
    skip_value = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.TextChannel) and message.author.id != self.bot.user.id:
            global skip_value #If 0, bot will reply; if 1, bot will send the message later; if 2, bot will
            global speaking_zone
            global msg

            with open('data/guilds.json', 'r') as file: #Determines speaking_zone value; this is set to 0 if a channel was not found in 'guilds.json'
                data = json.load(file)
                id = message.guild.id

                speaking_zone = None

                if str(id) in data:
                    if 'channels' in data[str(id)]:
                        if 'chatbot' in data[str(id)]['channels']:
                            speaking_zone = data[str(id)]['channels']['chatbot']

            log_response = False
            output = None
            send_output = False

            if message.channel.id == speaking_zone:

                #Sort out the file so that any repeated inputs are merged

                file = 'data/responses.csv'
                await Base.check_for_blanks(file)
                await Base.csv_input_prune(file)
                await Base.csv_output_prune(file)

                inputs, outputs = [], []

                try:
                    if skip_value == 2: #Message by the User
                        print("hi")
                        with open('data/responses.csv', 'a') as csvdata:
                            writer = csv.writer(csvdata)
                            print(str(msg.content + message.content))
                            writer.writerow((msg.content, message.content))
                            del msg
                        skip_value = 0

                except NameError:
                    skip_value = 0

                print(str(skip_value))

                if skip_value == 0:
                    with open('data/responses.csv', 'r') as csvdata:
                        reader = csv.reader(csvdata)
                        for row in reader:
                            if row != []:
                                inputs.append(row[0])
                                outputs.append(row[1:])

                        if message.content in inputs: #Search for the message in inputs
                            index = inputs.index(message.content)
                            output = outputs[index][random.randint(0,len(outputs[index])-1)]
                            send_output = True

                        else: #If the message is not recognised, change the topic and log user's response
                            skip_value = 1
                            msg = message
                            send_output = True

                elif skip_value == 1 and message.channel == msg.channel: #Check the message was sent in the original channel
                    skip_value = 2 #Increment the skip_value to progress the conversation
                    output = msg.content
                    send_output = True

                    if message.content in inputs: #Then the bot can just reply with one of its responses
                        index = inputs.index(message.content)
                        output = outputs[index][random.randint(0,len(outputs[index])-1)]

                elif skip_value > 1:
                    skip_value = 0
                    send_output = False

                if output is not None:
                    if send_output == True:
                        #output.replace('@everyone', '@ everyone')
                        #output.replace('@here', '@ here')
                        await message.channel.send(output)

    @commands.guild_only()
    @commands.command(name='setchatchannel', help='Sets the channel that the bot will respond to your messages in.')
    async def _setchatchannel(self, ctx, channel:discord.TextChannel):
        with open('data/guilds.json', 'r+') as file:
            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) in data:
                if 'channels' not in data[str(id)]:
                    data[str(id)]['channels'] = {}
                data[str(id)]['channels']['chatbot'] = target.id

            else:
                data[str(id)]['channels'] = {}
                data[str(id)]['channels']['chatbot'] = target.id

            json.dump(data, file, indent=4)

            file.truncate() #Remove remaining part

        await ctx.send(f'Chat channel has been set to {target.mention}!')

    @commands.command(name='removechatchannel', help='Removes the channel that the bot previously used for responding to your messages in, if there was one.')
    async def _removechatchannel(self, ctx):
        with open('data/guilds.json', 'r+') as file: #Determines speaking_zone value; this is set to 0 if a channel was not found in 'guilds.json'
            #Using 'r+' mode to allow writing and reading to the file.
            #Sources: see '_setchatchannel' (above)
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) in data:
                data[str(id)].pop('bot_chat_channel', None)
                #This removes the need to check if this variable exists;
                #If there is a 'bot_chat_channel', it will get removed.
                #If not, it will remove None, which removes nothing.
                #Source: https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary
            json.dump(data, file, indent=4)

            file.truncate() # Remove remaining part

        await ctx.send('Chat channel disabled.')

    @commands.guild_only()
    @commands.command(name='feed', help='Feeds the bot all of the inputs and responses from a specific channel.')
    @commands.is_owner()
    async def _feed(self, ctx, channel, guild_id:int=None, channel_id:int=None):

        ignore_last = False
        inputs = []
        responses = []

        tc_converter = commands.TextChannelConverter()

        if channel != '~':
            target = await tc_converter.convert(ctx, channel)
        else:
            target = self.bot.get_guild(guild_id).get_channel(channel_id)

        messages = await target.history(limit=None).flatten()
        ids = [Message.id for Message in messages]

        if len(ids) % 2 == 0: #If the number of messages in the channel is even...
            ignore_last = True #...then the last message has no response and so it should not be added to the inputs list

        #The following code is based on the fact that the message ID with index '0' is the most recent message that was sent

        await ctx.send(f"Feeding from channel {target.mention}.")
        m = await ctx.send("Reading messages...")

        for x in range(0, len(ids)):
            print("Reading messages: " + str(x) + f'/{len(ids)}')

            msg = await target.fetch_message(ids[x])
            if x % 2 == 0: #i.e. if the index is EVEN, by default it is a response (not necessarily an input)
             #Append the value, since this function gets messages from newest to oldest, always placing the oldest value to the end of the list
             #This allows us to easily identify whether it is an output or not.
                if x != len(ids) - 1 or ignore_last == False:
                    responses.append(msg)
                    if x != 0: #If the index is 0, we can assume it cannot be an input, as it was supposedly the last message
                        inputs.append(msg) #If the index is not 0, it can be both an input and a response

            else: #The index is ODD, by default it is both a response and an input
                responses.append(msg)
                if x != 0:
                    inputs.append(msg)

        await m.edit(content="Reading messages... **Done**")
        n = await ctx.send("Writing messages...")

        with open('data/responses.csv', 'a') as csvdata:
            writer = csv.writer(csvdata)
            for x in range(0, len(inputs)-1):
                try:
                    print(f"Writing messages: {str(x+1)}/{len(inputs)}")
                    writer.writerow((inputs[x].content, responses[x].content))
                except UnicodeEncodeError:
                    await ctx.send(f"Error writing exchange `{x}/{len(inputs)}`: Cannot store Unicode symbols") #Exchange as in an exchange of 1 message each
        print("Done")

        await n.edit(content="Writing messages... **Done**")
        await ctx.send("Feeding complete.")

def setup(bot):
    bot.add_cog(CleverChungus(bot))
