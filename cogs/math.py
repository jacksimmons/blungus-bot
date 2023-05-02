import math
import sympy
from decimal import Decimal
import sympy
from sympy.parsing.sympy_parser import\
parse_expr, standard_transformations,\
implicit_multiplication_application,\
convert_xor
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

class Math(commands.Cog):
    @commands.command(
            name="math2",
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
            aliases=["calc2"]
        )

    async def calculator(self, ctx: commands.Context, num1: Decimal, calc: str, num2: Decimal):
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
        
    @commands.command(
        name="math1",
        description=f'''Mathematical operations on a single decimal value.
        Compatible operators:
        'ceil': {single_value_operator_dict['ceil']}
        'fabs': {single_value_operator_dict['fabs']}
        ''',
        aliases=["calc1"]
    )

    async def single_calc(self, ctx: commands.Context, operator: str, x: Decimal):
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

    @commands.command(
        name="differentiate",
        description="Differentiate with respect to x.",
        aliases=["diff"]
    )

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

    @commands.command(
        name="integrate",
        description="Integrate with respect to x.",
        aliases=["int"]
    )

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