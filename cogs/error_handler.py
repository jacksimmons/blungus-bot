import traceback
import sys
import discord
import yt_dlp

from discord import app_commands
from discord.ext import commands


"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx: commands.Context, error)

For examples of cogs see:
Rewrite:
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
Async:
https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

This example uses @rewrite version of the lib. For the async version of the lib, simply swap the places of ctx: commands.Context, and error.
e.g: on_command_error(self, error, ctx)

For a list of exceptions:
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#errors
"""
class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, err):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.
        if hasattr(ctx.command, 'on_error'):
            return

        # This prevents any cogs with an overwritten cog_command_error being handled here.
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return

        ignored = (commands.CommandNotFound, )

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(err, 'original', err)
        error_msg = ""

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return
        
        #-----------------------------------------------------------------------------
        # Default discord.py exceptions
        elif isinstance(error, discord.Forbidden):
            error_msg = f"❗ {ctx.author.mention}, I am not permitted to do that."

        elif isinstance(error, discord.HTTPException):
            if error.text == 'Invalid Form Body\nIn nick: Must be 32 or fewer in length.':
                error_msg = f"❗ {ctx.author.mention}, please enter a nickname between 0 and 32 characters inclusive."
            else:
                error_msg = f"❗ {ctx.author.mention}, your request failed: `{error.text}`"

        elif isinstance(error, commands.DisabledCommand):
            error_msg = "❗ This command is disabled."

        elif isinstance(error, commands.NoPrivateMessage):
            error_msg = f"❗ {ctx.message.author.name}, `{ctx.command}` can not be used in Private Messages."

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tags':
                error_msg = "❗ I could not find that member. Please try again."
            else:
                error_msg = f"❗ {ctx.author.mention}, `{ctx.command}` failed due to a bad argument: `{str(error.args)}`"

        elif isinstance(error, commands.BotMissingPermissions):
            error_msg = f"❗ {ctx.author.mention}, I cannot do that: `{error.missing_perms}`"

        elif isinstance(error, commands.MissingPermissions):
            error_msg = f"❗ {ctx.author.mention}, you need the following permissions to use this command: `{error.missing_perms}`"

        elif isinstance(error, commands.MissingRequiredArgument):
            error_msg = f"❗ {ctx.author.mention}, your request is missing the `{error.param}` argument."

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            error_msg = f"❗ {ctx.author.mention}, one of your arguments is missing a closing \"."

        elif isinstance(error, commands.NotOwner):
            error_msg = f"❗ {ctx.author.mention}, you are not allowed to use this command."
        
        else:
            error_msg = f"❗Command error: {str(error)}"

        #-----------------------------------------------------------------------------
        
        # # All other Errors not returned come here. And we can just print the default TraceBack.
        # else:
        #     print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        #     traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        error_view = ErrorHandlerView(err)
        await ctx.send(content=error_msg, view=error_view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))


class ErrorHandlerView(discord.ui.View):
    def __init__(self, error):
        super().__init__()
        self.error = error
    
    @discord.ui.button(label="View full error", style=discord.ButtonStyle.grey)
    # Reference: https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4
    async def view_full_err_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.style=discord.ButtonStyle.success
        await interaction.response.send_message(content=str(self.error), view=self, ephemeral=True)
