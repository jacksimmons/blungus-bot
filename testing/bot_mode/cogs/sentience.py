import discord
import random
from discord.ext import commands

messages = []
speaking_zone = 0

class CleverChungus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        global speaking_zone
        if message.channel.id == speaking_zone and message.author.id != self.bot.user.id:
            text = message.content.lower()
            global messages
            messages.append(text)
            if messages != []:
                await message.channel.send(messages[random.randint(0,len(messages)-1)])
                print(messages)
            #with open("data/responses.text","r") as file:
            #    data = file.readlines()
        else:
            pass

    @commands.command(name='setbotchannel', help='Sets the channel that the bot will respond to your messages in.')
    async def _setbotchannel(self, ctx, channel: discord.TextChannel):
        global speaking_zone
        speaking_zone = channel.id
        await ctx.send('Bot channel has been set!')

def setup(bot):
    bot.add_cog(CleverChungus(bot))
