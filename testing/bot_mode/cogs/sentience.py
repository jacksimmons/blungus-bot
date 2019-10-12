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

    speaking_zone = None
    wait_for_response = False
    skip_value = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        global skip_value #If 0, bot will reply; if 1, bot will send the message later; if 2, bot will
        global speaking_zone
        global msg

        speaking_zone = 588320053708062731
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
            Base.csv_input_prune(file)
            print("OUTPUT")
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

            print(skip_value)

            if skip_value == 0:
                async with message.channel.typing():
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
                        else: #If the message is not recognised, change the topic and log user's response
                            if is_bot == False:
                                skip_value = 1
                                msg = message
                                send_output = True

            elif skip_value == 1 and message.channel == msg.channel: #Check the message was sent in the original channel
                skip_value = 2 #Increment the skip_value to progress the conversation
                output = msg.content
                send_output = True

            else:
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

def setup(bot):
    bot.add_cog(CleverChungus(bot))
