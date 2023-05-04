import math
import sympy
from decimal import Decimal
import sympy
from sympy.parsing.sympy_parser import\
parse_expr, standard_transformations,\
implicit_multiplication_application,\
convert_xor
from discord import app_commands
from discord.ext import commands

transformations = (standard_transformations\
                + (implicit_multiplication_application,)\
                + (convert_xor,))

operator_dict = {
'+': 'Addition',
'-': 'Subtraction',
'*': 'Multiplication',
'/': 'Division',
'^': 'Exponent',
'%': 'Modulo',
'//': 'Floor Division',
}
single_value_operator_dict = {
'+': 'Unary plus: (x) [Yields the value you entered]',
'-': 'Unary minus: -(x) [Yields the value you entered * -1]',
'~': 'Bitwise Inversion: -(x+1) [Yields the bit-wise inversion of the value you entered]',
'ceil': 'Return the ceiling of x as a float, the smallest integer value greater than or equal to x.',
'abs': 'Return the absolute value of x.',
'!': 'Return x factorial. For this to work, x must be integral and not negative.',
'floor': 'Return the floor of x as a float, the largest integer value less than or equal to x.',
'frexp': '''Return the mantissa and exponent of x as the pair (m, e).
            m is a float and e is an integer such that x == m * 2**e exactly.
            If x is zero, returns (0.0, 0), otherwise 0.5 <= abs(m) < 1.
            This is used to “pick apart” the internal representation of a float in a portable way.
            ''',
'modf': 'Return the fraction and integer parts of x. Both results carry the sign of x and are floats.',
'trunc': 'Return the Real value x truncated to an Integral'
}

class Math(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
    
    #---------------------------------------------------------------------------------
    
    @commands.hybrid_command(name="math2")
    @app_commands.describe(num1="The first number.",
                           operator="The operator, e.g. +, -, *, /",
                           num2="The second number.")
    async def _math2(self, ctx: commands.Context, num1: Decimal, operator: str, num2: Decimal):
        """Compatible operators: +, -, *, /, ^ (POW), % (MOD), // (DIV)"""
        if operator in operator_dict:
            if len(str(num1)) <= 30 and len(str(num2)) <= 30:
                try:
                    answer = "NAN"
                    if operator == '+':
                        answer = num1 + num2
                    elif operator == '-':
                        answer = num1 - num2
                    elif operator == '*':
                        answer = num1 * num2
                    elif operator == '/':
                        answer = num1 / num2
                    elif operator == '^':
                        answer = math.pow(num1, num2)
                    elif operator == '%':
                        answer = num1 % num2
                    elif operator == '//':
                        answer = num1 // num2
                    await ctx.send(f"{ctx.author.mention}, your answer is {answer}")
                except ZeroDivisionError:
                    await ctx.send(f'{ctx.author.mention}, you cannot carry out `{operator_dict[operator]}` of a decimal by zero.')
                except OverflowError:
                    await ctx.send(f'{ctx.author.mention}, your answer is too large!')
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `num1` and `num2`.')
        

    @commands.hybrid_command(name="math1")
    @app_commands.describe(operator="The operator, e.g. +, -, ~, abs.",
                           x="The input in the calculation.")
    async def _math1(self, ctx: commands.Context, operator: str, x: Decimal):
        """Compatible operators: + (unary), - (unary), ~ (bitwise inversion), ceil, abs, !, floor, frexp, modf, trunc"""
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
                    elif operator == 'abs':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.fabs(x)}.')
                    elif operator == '!':
                        if x <= 100:
                            await ctx.send(f'{ctx.author.mention}, your answer is {math.factorial(x)}.')
                        else:
                            await ctx.send(f'{ctx.author.mention}, `factorial` is limited to 100 or lower for `{ctx.command}`.')
                    elif operator == 'floor':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.floor(x)}.')
                    elif operator == 'frexp':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.frexp(x)}.')
                    elif operator == 'modf':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.modf(x)}.')
                    elif operator == 'trunc':
                        await ctx.send(f'{ctx.author.mention}, your answer is {math.trunc(x)}.')
                except:
                    pass
            else:
                await ctx.send(f'{ctx.author.mention}, `{ctx.command}` has a 30 character limit for `x`.')


    @commands.hybrid_command(name="differentiate")
    @app_commands.describe(equation="The equation to differentiate, with respect to x.")
    async def differentiate(self, ctx: commands.Context, equation: str):
        x = sympy.symbols("x")
        d = ""
        expr = sympy.parse_expr(equation,
        transformations=transformations)
        try:
            d = sympy.diff(expr, x)
            await ctx.send(f"`{d}`")
        except sympy.SympifyError as e:
            await ctx.send("Parsing error: " + e.expr)


    @commands.hybrid_command(name="integrate")
    @app_commands.describe(equation="The equation to integrate, with respect to x.")
    async def integrate(self, ctx: commands.Context, equation: str):
        x = sympy.symbols("x")
        d = ""
        expr = sympy.parse_expr(equation,
        transformations=transformations)
        try:
            d = sympy.integrate(expr, x)
            await ctx.send(f"`{d}`")
        except sympy.SympifyError as e:
            await ctx.send("Parsing error: " + e.expr)


async def setup(bot):
    await bot.add_cog(Math(bot))