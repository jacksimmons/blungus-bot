import discord
import random
import csv
import os
from base import Base
from discord.ext import commands

registered_inputs = []

class CleverChungus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.tc_converter = None

    speaking_zone = None
    wait_for_response = False
    skip_value = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        global skip_value #If 0, bot will reply; if 1, bot will send the message later; if 2, bot will
        global speaking_zone
        global msg

        speaking_zone = 586216189517234304
        log_response = False
        output = None
        is_bot = False
        send_output = False

        if message.channel.id == speaking_zone:

            if message.author.id == self.bot.user.id:
                is_bot = True

            #Sort out the file so that any repeated inputs are merged

            file = 'data/responses.csv'
            os.chdir('../bot_mode')
            Base.check_for_blanks(file)
            Base.csv_input_prune(file)
            Base.csv_output_prune(file)

            inputs, outputs = [], []

            try:
                prev_skip_value = skip_value
                if skip_value == 2:
                    if bot == False:
                        os.chdir('../bot_mode')
                        with open('data/responses.csv', 'a') as csvdata:
                            writer = csv.writer(csvdata)
                            writer.writerow((msg.content, message.content))
                            del msg
                        skip_value = 0

            except NameError:
                skip_value = 0

            if skip_value == 0:
                os.chdir('../bot_mode')
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
                        if is_bot == False:
                            skip_value = 1
                            msg = message
                            send_output = True

            elif skip_value == 1 and message.channel == msg.channel: #Check the message was sent in the original channel
                if message.content in inputs:
                    index = inputs.index(message.content)
                    output = outputs[index][random.randint(0,len(outputs[index])-1)]
                skip_value = 2 #Increment the skip_value to progress the conversation
                output = msg.content
                send_output = True

            elif skip_value > 1:
                skip_value = 0
                send_output = False

            if output is not None:
                if is_bot == False:
                    if send_output == True:
                        await message.channel.send(output)
                else:
                    skip_value = prev_skip_value

    @commands.command(name='setbotchannel', help='Sets the channel that the bot will respond to your messages in.')
    async def _setbotchannel(self, ctx, channel: discord.TextChannel):
        global speaking_zone
        speaking_zone = channel.id
        await ctx.send('Bot channel has been set!')

    @commands.command(name='feed', help='Feeds the bot all of the inputs and responses from a specific channel.')
    @commands.is_owner()
    async def _feed(self, ctx, channel, guild_id:int=None, channel_id:int=None):

        ignore_last = False
        inputs = []
        responses = []

        if channel != '~':
            self.tc_converter = commands.TextChannelConverter()
            target = await self.tc_converter.convert(ctx, channel)
        else:
            target = self.bot.get_guild(guild_id).get_channel(channel_id)

        messages = await target.history(limit=None).flatten()
        ids = [Message.id for Message in messages]

        if len(ids) % 2 == 0: #If the number of messages in the channel is even...
            ignore_last = True #...then the last message has no response and so it should not be added to the inputs list

        #The following code is based on the fact that the message ID with index '0' is the most recent message that was sent
        for x in range(0, len(ids)):
            print("Reading messages: " + str(x))

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

        os.chdir('../bot_mode')
        with open('data/responses.csv', 'a') as csvdata:
            writer = csv.writer(csvdata)
            for x in range(0, len(inputs)-1):
                try:
                    print(f"Writing messages: {str(x+1)}/{len(inputs)}")
                    writer.writerow((inputs[x].content, responses[x].content))
                except UnicodeEncodeError:
                    print("Error: Cannot store Unicode symbols")
        print("Done")

def setup(bot):
    bot.add_cog(CleverChungus(bot))
