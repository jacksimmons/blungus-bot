import traceback
import sys
from discord.ext import commands
import discord
import youtube_dl

"""
If you are not using this inside a cog, add the event decorator e.g:
@bot.event
async def on_command_error(ctx, error)

For examples of cogs see:
Rewrite:
https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
Async:
https://gist.github.com/leovoel/46cd89ed6a8f41fd09c5

This example uses @rewrite version of the lib. For the async version of the lib, simply swap the places of ctx, and error.
e.g: on_command_error(self, error, ctx)

For a list of exceptions:
http://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html#errors
"""


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        # This prevents any commands with local handlers being handled here in on_command_error.

        #if hasattr(ctx.command, 'on_error'):
        #    return

        try:
            await ctx.message.add_reaction(emoji='❗')
        except:
            pass

        ignored = (commands.CommandNotFound)

        # Allows us to check for original exceptions raised and sent to CommandInvokeError.
        # If nothing is found. We keep the exception passed to on_command_error.
        error = getattr(error, 'original', error)

        # Anything in ignored will return and prevent anything happening.
        if isinstance(error, ignored):
            return

        #-----------------------------------------------------------------------------
        # Default discord.py exceptions

        elif isinstance(error, commands.CommandError):
            return await ctx.send(error)

        elif isinstance(error, discord.Forbidden):
            return await ctx.send(f'{ctx.author.mention}, I do not have sufficient permissions to carry out `{ctx.command}` on this user.')

        elif isinstance(error, discord.HTTPException):
            if error.text == 'Invalid Form Body\nIn nick: Must be 32 or fewer in length.':
                return await ctx.send(f'{ctx.author.mention}, failed to `{ctx.command}`. The username you entered was longer than the nickname character limit.')

            else:
                return await ctx.send(f'''{ctx.author.mention}, failed to `{ctx.command}`: `{error.text}`''')

        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.message.author.name}, `{ctx.command}` can not be used in Private Messages.')
            except:
                pass

        # For this error example we check to see where it came from...
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':  # Check if the command being invoked is 'tag list'
                return await ctx.send('I could not find that member. Please try again.')
            else:
                return await ctx.send(f"{ctx.author.mention}, `{ctx.command}` failed due to a bad argument: `{error.args[0]}`")

        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"{ctx.author.mention}, you are lacking the following permissions required for this command: `{error.missing_perms}`.")

        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"{ctx.author.mention}, your request is missing the `{error.param}` argument.")

        elif isinstance(error, commands.ExpectedClosingQuoteError):
            return await ctx.send(f"{ctx.author.mention}, your `{ctx.command}` command failed since one of your perameters is missing a closing \".")

        elif isinstance(error, commands.NotOwner):
            return await ctx.send(f"{ctx.author.mention}, this command is reserved for the owner of the bot.")
        #-----------------------------------------------------------------------------

        # All other Errors not returned come here... And we can just print the default TraceBack.

        elif isinstance(error, youtube_dl.utils.DownloadError):
            return await ctx.send(f"No video results.")

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
    bot.add_cog(CommandErrorHandler(bot))
