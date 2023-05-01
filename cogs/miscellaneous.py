import discord
import json
from discord.ext import commands
from datetime import datetime as d

# New - The Cog class must extend the commands.Cog class
class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    #---------------------------------------------------------------------------------

    @commands.command(
        name='ping',
        description='The ping command',
        aliases=[]
    )

    async def ping_command(self, ctx):
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

    @commands.command(
        name='length',
        description='Tells you how many characters long your message is.',
        aliases=['len']
    )

    async def length_command(self, ctx, *, message: str):
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

    async def say_command(self, ctx, *, message: str):
        await ctx.send(message)
        await ctx.message.delete()

    # #---------------------------------------------------------------------------------
    #
    # @commands.command(
    #     name='addslapper',
    #     description='Add a slapper.',
    # )
    #
    # async def add_slapper(self, ctx, slapper: User):
    #     with open('data/data.json', 'w') as file:
    #         contents = json.load(file)
    #         contents["trolliliyan"]["slappers"].append(slapper.id)

    #---------------------------------------------------------------------------------

    @commands.group(
        name='trolliliyan',
        description='Trolls Iliyan.',
        aliases=['ti']
    )

    async def trolliliyan(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")
        pass

    @trolliliyan.command(
        name='toggle',
        description='Toggles the trolling of Iliyan.',
    )

    async def ti_toggle(self, ctx):
        contents: dict = {}
        with open("data/data.json", "r") as file:
            contents = json.load(file)
            enabled = contents["trolliliyan"]["enabled"]
            contents["trolliliyan"]["enabled"] = not enabled

        with open("data/data.json", "w") as file:
            json.dump(contents, file, indent=4)
        await ctx.send("Iliyan trolling set to " + str(not enabled))

    @trolliliyan.command(
        name='addinsult',
        description='Adds an insult to Iliyan trolling.'
    )

    async def ti_addinsult(self, ctx, *, message:str):
        contents: dict = {}
        with open("data/data.json", "r") as file:
            contents = json.load(file)
            contents["trolliliyan"]["insults"].append(f"{message}")

        with open("data/data.json", "w") as file:
            json.dump(contents, file, indent=4)
        await ctx.send("Added " + message)

    @trolliliyan.command(
        name='removeinsult',
        description='Removes an insult from Iliyan trolling.'
    )

    async def ti_removeinsult(self, ctx, *, number: int):
        contents: dict = {}
        with open("data/data.json", "r") as file:
            contents = json.load(file)
            try:
                insult = contents["trolliliyan"]["insults"][number - 1]
                await ctx.send("No more " + insult + "...")
                del contents["trolliliyan"]["insults"][number - 1]
            except:
                await ctx.send("Invalid insult index.")

        with open("data/data.json", "w") as file:
            json.dump(contents, file, indent=4)

    @trolliliyan.command(
        name='list',
        description='Shows all the insults.'
    )

    async def ti_list(self, ctx):
        insults: dict = {}
        with open("data/data.json", "r") as file:
            insults = json.load(file)["trolliliyan"]["insults"]

        embed = discord.Embed(color=0x00ff00)

        embed.set_author(name="U mad iliian?")
        for insult in insults:
            embed.add_field(name=insults.index(insult)+1, value=insult, inline=True)

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

async def setup(bot):
    await bot.add_cog(Misc(bot))