import discord
import json
from discord import app_commands
from discord.ext import commands
from datetime import datetime as d

# New - The Cog class must extend the commands.Cog class
class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="ping")
    async def ping_command(self, ctx):
        """Used to display connection latency."""
        start = d.timestamp(d.now())
        # Gets the timestamp when the command was used

        msg = await ctx.send('Pinging')
        # Sends a message to the user in the channel the message with the command was received.
        # Notifies the user that pinging has started

        await msg.edit(content=f'Pong!\nOne message round-trip took {( d.timestamp( d.now() ) - start ) * 1000 }ms.')
        # Ping completed and round-trip duration show in ms
        # Since it takes a while to send the messages
        # it will calculate how much time it takes to edit an message.
        # It depends usually on your internet connection speed
        return

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="length")
    @app_commands.describe(message="The message to find the length of.")
    async def length_command(self, ctx: commands.Context, *, message: str):
        if len(message) <= 500:
            await ctx.send(f'"{message}" is {len(message)} characters long.')
        else:
            await ctx.send(f"That message is {len(message)} characters long.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='say',
        description='Make the bot say something.',
        aliases=['parrot','repeat','copy']
    )

    @commands.hybrid_command(name="say")
    @app_commands.describe(message="The message to repeat.",
                           delete="Whether I should try and delete your message afterwards.")
    async def _say(self, ctx: commands.Context, *, message: str, delete: bool):
        await ctx.send(message)
        if delete:
            await ctx.message.delete()

    #---------------------------------------------------------------------------------


async def setup(bot):
    await bot.add_cog(Misc(bot))