import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from discord.ui import View, Modal

import random
import json

emoji = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","🆑","🆎","🅾️","🆘","❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","💔","💯","💢","♨️","❗️","❓","‼️","⁉️","🔅","〽️","⚠️","🚸","🔱","⚜️","➡️","⬅️","⬆️","⬇️","↗️","↘️","↙️","↖️","↪️","↩️","🔄","🎵","🔴","🟠","🟡","🟢","🔵","🟣","⚫️","⚪️","🔔","📢","♾️"]
MAX_EMOJI = 20
# (num_chars) / INSULT_RANDOM_LIMIT chance of being insulted.
INSULT_RANDOM_LIMIT = 1000


class RPSView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.my_score = 0
        self.your_score = 0


    @discord.ui.select(
        placeholder = "Pick a move...", # the placeholder text that will be displayed if nothing is selected
        min_values = 1, # the minimum number of values that must be selected by the users
        max_values = 1, # the maximum number of values that can be selected by the users
        options = [ # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="🪨",
                value="Rock",
                description="Rock"
            ),
            discord.SelectOption(
                label="📄",
                value="Paper",
                description="Paper"
            ),
            discord.SelectOption(
                label="✂️",
                value="Scissors",
                description="Scissors"
            )
        ]
    )
    async def callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        your_move = select.values[0]
        my_move = random.choice(["Rock", "Paper", "Scissors"])
        outcome = 0
        if (your_move == "Rock"):
            if (my_move == "Paper"):
                outcome = 1
            elif (my_move == "Scissors"):
                outcome = -1
        elif (your_move == "Paper"):
            if (my_move == "Scissors"):
                outcome = 1
            elif (my_move == "Rock"):
                outcome = -1
        else:
            if (my_move == "Rock"):
                outcome = 1
            elif (my_move == "Paper"):
                outcome = -1

        output = ""
        if outcome == 1:
            output = "I win."
            self.my_score += 1
        elif outcome == 0:
            output = "It's a draw."
            self.my_score += 0.5
            self.your_score += 0.5
        else:
            output = "You win."
            self.your_score += 1

        await interaction.message.edit(content=f"Rock Paper Scissors\nWins - You: {str(self.your_score)}, Me: {str(self.my_score)}")
        await interaction.response.send_message(content=f"You played {select.values[0]}.\nI played {my_move}.\n{output}", ephemeral=True)


class VoteDropdown(discord.ui.Select):
    def __init__(self, title, fields):
        self.fields = [discord.SelectOption(label=field) for field in fields]
        super().__init__(placeholder=title, min_values=1, max_values=1, options=self.fields)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class UserDropdown(discord.ui.UserSelect):
    def __init__(self, title):
        super().__init__(placeholder=title, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    #---------------------------------------------------------------------------------
    # INSULTS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.id == self.bot.user.id):
            return

        if len(message.content) > INSULT_RANDOM_LIMIT or random.randint(INSULT_RANDOM_LIMIT) < len(message.content):
            with open("data/data.json", "r") as file:
                str_id = str(message.author.id)
                if (str_id in json.load(file)["insults"]):
                    with open("data/data.json", "r") as file:
                        data = json.load(file)
                        insult = random.choice(data["insults"][str_id]["messages"])
                        await message.channel.send(insult)
                        if "emoji" in data["insults"][str_id]:
                            emoji: str = data["insults"][str_id]["emoji"]
                            await message.add_reaction(emoji)


    @commands.hybrid_group(name="insult")
    async def _insults(self, ctx):
        """Handles the messages sent when a particular user speaks, which 'insult' them."""
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")
        

    @_insults.command(name="add")
    @app_commands.describe(message="The message to add.",
                           user="The user to 'insult'.")
    async def _add_insult(self, ctx: commands.Context, user: discord.User, *, message:str):
        """Adds an insult to the database."""
        contents: dict = {}
        with open("data/data.json", "r") as file:
            contents = json.load(file)
            if (str(user.id) not in contents["insults"]):
                contents["insults"][str(user.id)] = {"emoji": str(ord("💩")), "messages": [message]}
            else:
                contents["insults"][str(user.id)]["messages"].append(message)

        with open("data/data.json", "w") as file:
            json.dump(contents, file, indent=4)
        await ctx.send(f"Added insult `{message}` for user `{user.name}`.")


    @_insults.command(name="remove")
    @app_commands.describe(index="The insult index to remove. Use `insult list` to see indices.")
    async def _remove_insult(self, ctx: commands.Context, user: discord.User, index: int):
        """Removes an insult from the database by index."""
        contents: dict = {}
        with open("data/data.json", "r") as file:
            contents = json.load(file)
            try:
                insult = contents["insults"][str(user.id)]["messages"][index]
                await ctx.send("No more " + insult + "...")
                del insult
            except:
                await ctx.send("Invalid insult index or user.")

        with open("data/data.json", "w") as file:
            json.dump(contents, file, indent=4)


    @_insults.command(name="list")
    @app_commands.describe(user="The user to list insults for.")
    async def _list_insults(self, ctx: commands.Context, user: discord.User):
        """Shows all insults for a given user, and each insult's index."""
        data: dict = {}
        with open("data/data.json", "r") as file:
            content = json.load(file)
            if str(user.id) in content["insults"]:
                data = content["insults"][str(user.id)]
            else:
                await ctx.send(f"`{user.name}` has no insults.")
                return

        emoji = ""
        if "emoji" in data:
            emoji = data["emoji"]
        
        insults = None
        if "messages" in data:
            insults = data["messages"]

        embed = discord.Embed(color=0x00ff00)
        embed.set_author(name=f"{user.name} {emoji}")

        if insults:
            for insult in insults:
                embed.add_field(name=insults.index(insult), value=insult, inline=True)
        else:
            embed.add_field(name="Insults", value="User has no insults.")

        await ctx.send(embed=embed)


    @_insults.command(name="emoji")
    @app_commands.describe(user="The user this applies to.",
                           emoji="The emoji to react with on an insult (usually 💩).")
    async def _insult_emoji(self, ctx: commands.Context, user: discord.User, emoji: str):
        """Sets the emoji which I will react with when insulting a given user."""
        try:
        # Try Custom
            discord.utils.get(self.bot.emojis, name=emoji)
        except:
            try:
            # Try Unicode
                emoji = "\\" + emoji
                discord.utils.get(self.bot.emojis, name=emoji)
            except Exception as e:
                print(e)
                raise commands.EmojiNotFound(emoji)

        with open("data/data.json", "r") as file:
            data = json.load(file)
            if str(user.id) not in data["insults"]:
                data["insults"][str(user.id)] = {"emoji": emoji, "messages": []}
            else:
                data["insults"][str(user.id)]["emoji"] = emoji

        with open("data/data.json", "w") as file:
            json.dump(data, file, indent=4)

        await ctx.send(f"Set emoji for user `{user.name}` to `{emoji}`")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="poll")
    @app_commands.describe(
        message="The message to poll on."
    )
    async def _poll(self, ctx: commands.Context, *, message: str):
        """A standard yes/no system with emojis."""
        embed = discord.Embed(colour=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.add_field(name="Poll", value=message)
        message = await ctx.send(embed=embed)
        await message.add_reaction('👍')
        await message.add_reaction('👎')
    
    
    @commands.hybrid_command(name="vote")
    @app_commands.describe(
        title="The title of the voting panel.",
        space_separated_options="The options, each separated by a space. Use quotation marks for options with multiple words."
    )
    async def _vote(self, ctx: commands.Context, title: str, *, space_separated_options: str):
        """An option picking system with emojis."""
        embed = discord.Embed(colour=0x0000ff)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
        embed.set_footer(text="React to vote.")
        embed.add_field(name="Vote", value=title, inline=False)
        fields = space_separated_options.split(" ")
        if len(fields) <= MAX_EMOJI:
            for i in range(0, len(fields)):
                embed.add_field(name=emoji[i], value=fields[i])
        else:
            raise commands.CommandError(f"Pick a number of choices below {MAX_EMOJI}, as discord has a reaction limit of 50.\
Make sure you\
enclose your options in speech marks so that several word options\
don't get picked up as multiple options.\n For example, your options were\
 {str(fields)}.")
        message = await ctx.send(embed=embed)
        for i in range(0, len(fields)):
            await message.add_reaction(emoji[i])
    

    @commands.hybrid_command(name="ddvote")
    @app_commands.describe(
        title="The title of the voting panel.",
        space_separated_choices="The dropdown choices, separated by spaces. Use quotation marks for multiple-word choices."
    )
    async def _dropdown_vote(self, ctx: commands.Context, title: str, *, space_separated_choices: str):
        """Makes a dropdown voting system."""
        view = View()
        view.add_item(VoteDropdown(title, space_separated_choices.split(" ")))
        await ctx.send("Pick an option:", view=view)


    @commands.hybrid_command(name="uservote")
    @app_commands.describe(
        title="The title of the voting panel."
    )
    async def _dropdown_user_vote(self, ctx: commands.Context, title: str):
        """Makes a dropdown voting system."""
        view = View()
        view.add_item(UserDropdown(title))
        await ctx.send("Pick a user:", view=view)
    

    @commands.hybrid_command(name="rockpaperscissors")
    async def _rock_paper_scissors(self, ctx: commands.Context):
        """Plays an interactive game of rock-paper-scissors."""
        view = RPSView()
        await ctx.send("Rock Paper Scissors", view=view, ephemeral=False)


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))