import discord
import math
from decimal import *
from discord.ext import commands
from datetime import datetime as d

operator_dict = {
'+': 'Addition',
'-': 'Subtraction',
'*': 'Multiplication',
'/': 'Division',
'^': 'Exponent',
'%': 'Modulo',
'//': 'Floor Division',
}
inequality_dict = {
'==': 'Equals',
'!=': 'Does not equal',
'>': 'Is greater than',
'<': 'Is less than',
'>=': 'Is greater than or equal to',
'<=': 'Is less than or equal to'
}
single_value_operator_dict = {
'+': 'Unary plus: (x) [Yields the value you entered]',
'-': 'Unary minus: -(x) [Yields the value you entered * -1]',
'~': 'Bitwise Inversion: -(x+1) [Yields the bit-wise inversion of the value you entered]',
'ceil': 'Return the ceiling of x as a float, the smallest integer value greater than or equal to x.',
'fabs': 'Return the absolute value of x.',
'factorial': 'Return x factorial. For this to work, x must be integral and not negative.',
'floor': 'Return the floor of x as a float, the largest integer value less than or equal to x.',
'frexp': '''Return the mantissa and exponent of x as the pair (m, e).
            m is a float and e is an integer such that x == m * 2**e exactly.
            If x is zero, returns (0.0, 0), otherwise 0.5 <= abs(m) < 1.
            This is used to “pick apart” the internal representation of a float in a portable way.
            ''',
'isinf': 'Check if the float x is positive or negative infinity.',
'isnan': 'Check if the float x is a NaN (not a number). [Note: This should always be false]',
'modf': 'Return the fraction and integer parts of x. Both results carry the sign of x and are floats.',
'trunc': 'Return the Real value x truncated to an Integral'
}

# New - The Cog class must extend the commands.Cog class
class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    #---------------------------------------------------------------------------------

    @commands.command(
        name='ping',
        description='The ping command',
        aliases=['p']
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

    @commands.group(
        name='math',
        description=f'''Solves math problems.
        Compatible operators:
        '+': {operator_dict['+']}
        '-': {operator_dict['-']}
        '*': {operator_dict['*']}
        '/': {operator_dict['/']}
        '^' or '**': {operator_dict['^']}
        '%': {operator_dict['%']}
        '//': {operator_dict['+']}
        ''',
        aliases=['calc']
    )

    async def calculator(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")
        pass

    @calculator.command(
        name='integer',
        description='''Calculations with two integers.
        Integer: An Integer (aka "whole number") is a number that can be written without a fractional component.''',
        aliases=['int','i']
    )

    async def int_calc(self, ctx, num1: int, calc: str, num2: int):
        if calc in operator_dict:
            if len(str(num1)) <= 30 and len(str(num2)) <= 30:
                try:
                    if calc == '+':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 + num2}.')
                    elif calc == '-':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 - num2}.')
                    elif calc == '*':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 * num2}.')
                    elif calc == '/':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 / num2}.')
                    elif calc == '**':
                        if num2 <= 50:
                            await ctx.send(f'{ctx.author.mention}, your answer is {num1 ** num2}.')
                        else:
                            await ctx.send(f'{ctx.author.mention}, exponents of values are limited to 50 or lower for `{ctx.command}`.')
                    elif calc == '%':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 % num2}.')
                    elif calc == '//':
                        await ctx.send(f'{num1 // num2}')
                except ZeroDivisionError:
                    await ctx.send(f'{ctx.author.mention}, you cannot carry out `{operator_dict[calc]}` of an integer by zero.')
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `num1` and `num2`.')

    @calculator.command(
        name='float',
        description='''Calculations with two floating-point values.
        Float: Think of a floating-point value as a value that can contain decimal points. Similar to the 'decimal' data type, but less user-friendly. Accurate to 15 decimal points. (e.g. 1.3, 4.0, 12.49349)
        Note: The Float data type can be quite confusing, expect unusual answers and lengthy, untruncated values.''',
        aliases=['f']
    )

    async def float_calc(self, ctx, num1: float, calc: str, num2: float):
        if calc in operator_dict:
            if len(str(num1)) <= 30 and len(str(num2)) <= 30:
                try:
                    if calc == '+':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 + num2}.')
                    elif calc == '-':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 - num2}.')
                    elif calc == '*':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 * num2}.')
                    elif calc == '/':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 / num2}.')
                    elif calc == '**':
                        if num2 <= 50:
                            await ctx.send(f'{ctx.author.mention}, your answer is {num1 ** num2}.')
                        else:
                            await ctx.send(f'{ctx.author.mention}, exponents of values are limited to 50 or lower for `{ctx.command}`.')
                    elif calc == '%':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 % num2}.')
                    elif calc == '//':
                        await ctx.send(f'{num1 // num2}')
                except ZeroDivisionError:
                    await ctx.send(f'{ctx.author.mention}, you cannot carry out `{operator_dict[calc]}` of a float by zero.')
                except OverflowError:
                    await ctx.send(f'{ctx.author.mention}, your answer is too large!')
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `num1` and `num2`.')

    @calculator.command(
        name='decimal',
        description='''Calculations with two decimals.
        Decimal: Basic numbers (e.g. 1, 3.14, -50.401)
        ''',
        aliases=['d','dec','denary']
    )

    async def decimal_calc(self, ctx, num1: Decimal, calc: str, num2: Decimal):
        if calc in operator_dict:
            if len(str(num1)) <= 30 and len(str(num2)) <= 30:
                try:
                    if calc == '+':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 + num2}.')
                    elif calc == '-':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 - num2}.')
                    elif calc == '*':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 * num2}.')
                    elif calc == '/':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 / num2}.')
                    elif calc in ('^', '**'):
                        if num2 <= 50:
                            await ctx.send(f'{ctx.author.mention}, your answer is {num1 ** num2}.')
                        else:
                            await ctx.send(f'{ctx.author.mention}, exponents of values are limited to 50 or lower for `{ctx.command}`.')
                    elif calc == '%':
                        await ctx.send(f'{ctx.author.mention}, your answer is {num1 % num2}.')
                    elif calc == '//':
                        await ctx.send(f'{num1 // num2}')
                except ZeroDivisionError:
                    await ctx.send(f'{ctx.author.mention}, you cannot carry out `{operator_dict[calc]}` of a decimal by zero.')
                except OverflowError:
                    await ctx.send(f'{ctx.author.mention}, your answer is too large!')
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `num1` and `num2`.')

    @calculator.command(
        name='single',
        description=f'''Mathematical operations on a single decimal value.
        Compatible operators:
        'ceil': {single_value_operator_dict['ceil']}
        'fabs': {single_value_operator_dict['fabs']}
        ''',
        aliases=['s']
    )

    async def single_calc(self, ctx, operator: str, x: Decimal):
        if operator in single_value_operator_dict:
            if len(str(x)) <= 30:
                try:
                    if operator == '+':
                        await ctx.send(f'{ctx.author.mention}, your answer is {+x}.')
                    elif operator == '-':
                        await ctx.send(f'{ctx.author.mention}, your answer is {-x}.')
                    elif operator == '~':
                        await ctx.send(f'{ctx.author.mention}, your answer is {~int(x)}.')
                    elif operator == 'ceil':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.ceil(x)}.')
                    elif operator == 'fabs':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.fabs(x)}.')
                    elif operator == 'factorial':
                        if x <= 100:
                            await ctx.send(f'{ctx.author.mention}, your answer is {math.factorial(x)}.')
                        else:
                            await ctx.send(f'{ctx.author.mention}, `factorial` is limited to 100 or lower for `{ctx.command}`.')
                    elif operator == 'floor':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.floor(x)}.')
                    elif operator == 'frexp':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.frexp(x)}.')
                    elif operator == 'isinf':
                        await ctx.send(f'{ctx.author.mention}, is your value infinite? {math.isinf(float(x))}.')
                    elif operator == 'isnan':
                        await ctx.send(f'{ctx.author.mention}, is your value a NaN? {math.isnan(float(x))}.')
                    elif operator == 'modf':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.modf(x)}.')
                    elif operator == 'trunc':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.trunc(x)}.')
                except:
                    pass
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `x`.')

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

    #---------------------------------------------------------------------------------

def setup(bot):
    bot.add_cog(Misc(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
