import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Greedy, Context
from discord.ui import View, Modal

emoji = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟","🆑","🆎","🅾️","🆘","❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","💔","💯","💢","♨️","❗️","❓","‼️","⁉️","🔅","〽️","⚠️","🚸","🔱","⚜️","➡️","⬅️","⬆️","⬇️","↗️","↘️","↙️","↖️","↪️","↩️","🔄","🎵","🔴","🟠","🟡","🟢","🔵","🟣","⚫️","⚪️","🔔","📢","♾️"]
MAX_EMOJI = 20


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
        self.bot:commands.Bot = bot

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


async def setup(bot: commands.Bot):
    await bot.add_cog(Fun(bot))