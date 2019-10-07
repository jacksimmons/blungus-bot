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
dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Day of the week
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Month of the year

lyric1 = '''He's a big chungus
He’s a big chunky boi
Such a big bun, yes
We are so overjoyed
To have a big chunky boi
A big and wonderful chungus such as he
Oh such as he'''

lyric2 = '''He's a big chungus
He's a big chunky boi
Such a big bun, yes
We are so overjoyed
To have a big chunky boi
A big and wonderful chungus such as he
Oh such as he
Huh!'''

lyric3 = '''Buns come in all shapes and sizes
This one has so many surprises
I’ve never seen a giant quite like him
There's no one like him
Nobody like chungus!
Huh!'''

lyric4 = '''Get the game for PS4
For a limited time
Huh!
Don't miss what it has in store
You're running out of time
Play the game of the year
The game with that colossal boi!'''

lyric5 = '''He's a big chungus
He's a big chunky boi
Such a big bun, yes
We are so overjoyed
To have a big chunky boi
A big and wonderful chungus such as he
Oh such as he
Huh!'''

lyric6 = '''Huh!
Buns come in all shapes and sizes
This one has so many surprises
I've never seen a giant quite like him
There's no one like him
Nobody like chungus!
Huh!'''


# New - The Cog class must extend the commands.Cog class
class Basic(commands.Cog):

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

    @commands.command(
        name='chungus',
        description='Chunga',
        aliases=[]
    )

    async def chungachunga(self, ctx):
        await ctx.send(lyric1)
        await ctx.send(lyric2)
        await ctx.send(lyric3)
        await ctx.send(lyric4)
        await ctx.send(lyric5)
        await ctx.send(lyric6)


    #---------------------------------------------------------------------------------

    @commands.command(
        name='guildinfo',
        description='Returns some basic info about this guild.',
        aliases=['serverinfo','server','guild']
    )

    async def guildinfo_command(self, ctx):
        roles = ''
        categories = ''
        guild = ctx.guild

        for x in range(0, len(guild.roles)):
            if len(roles) < 250:
                if len(guild.roles[len(guild.roles)-(x+1)].name) >= 30:
                    roles += f', {guild.roles[len(guild.roles)-(x+1)].name[:30]}...'
                else:
                    if roles == '':
                        roles += f'{guild.roles[len(guild.roles)-(x+1)].name}'
                    else:
                        roles += f', {guild.roles[len(guild.roles)-(x+1)].name}'
            elif len(roles) >= 250:
                roles += f' ... {guild.default_role}'
                break

        for x in range(0, len(guild.categories)):
            if len(categories) < 250:
                if len(guild.categories[len(guild.categories)-(x+1)].name) >= 30:
                    categories += f'{guild.categories[len(guild.categories)-(x+1)].name[:30]}...'
                else:
                    if categories == '':
                        categories += f'{guild.categories[x]}'
                    else:
                        categories += f', {guild.categories[x]}'
            elif len(categories) >= 250:
                categories += f' ... {guild.categories[len(guild.categories)-(x+1)]}'
                break

        embed = discord.Embed(color=0x00ff00)
        embed.set_author(name=f"{guild.name} | ID: {guild.id}", icon_url=f"{guild.icon_url}")
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=f"{ctx.author.avatar_url}")
#1
        embed.add_field(
        name="Owner",
        value=f"{guild.owner}",
        inline=True)
#2
        embed.add_field(
        name="Region",
        value=f"{guild.region}",
        inline=True)
#3
        embed.add_field(
        name="Categories",
        value=f"{len(guild.categories)}",
        inline=True)
#4
        embed.add_field(
        name="Members",
        value=f"{len(guild.members)}",
        inline=True)
#5
        embed.add_field(
        name="Bots",
        value="Bots",
        inline=True)
#6
        embed.add_field(
        name="Humans",
        value="Humans",
        inline=True)
#7
        embed.add_field(
        name="Channels",
        value=f"{len(guild.channels)}",
        inline=True)
#8
        embed.add_field(
        name="Text Channels",
        value=f"{len(guild.text_channels)}",
        inline=True)
#9
        embed.add_field(
        name="Voice Channels",
        value=f"{len(guild.voice_channels)}",
        inline=True)
#10
        embed.add_field(
        name="File Upload Limit",
        value=f"{guild.filesize_limit/1000000}MB",
        inline=True)
#11
        embed.add_field(
        name="Emoji Limit",
        value=f"{guild.emoji_limit} emoji",
        inline=True)
#12
        embed.add_field(
        name="Bitrate Limit",
        value=f"{guild.bitrate_limit/1000} kbps",
        inline=True)
#13
        embed.add_field(
        name="Roles",
        value=f"{len(guild.roles)}",
        inline=True)
#14
        embed.add_field(
        name="Nitro Boosters",
        value=f"{guild.premium_subscription_count}",
        inline=True)
#15
        embed.add_field(
        name="Guild Premium Tier",
        value=f"{guild.premium_tier}",
        inline=True)
#antepenultimate
        embed.add_field(
        name="Server created",
        value=f"{dotw[guild.created_at.weekday()-1]}, {guild.created_at.day} {moty[guild.created_at.month-1]} {guild.created_at.year} at {guild.created_at.hour}:{guild.created_at.minute}",
        inline=False)
#penultimate
        embed.add_field(
        name="Roles List",
        value=f"{roles}",
        inline=False)
#ultimate
        embed.add_field(
        name="Categories List",
        value=f"{categories}",
        inline=False
        )

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='userinfo',
        description='Returns some basic information about a user.',
        aliases=['memberinfo','whois']
    )

    # Member mention: <@id>
    # Role mention: <@&id>
    # Channel mention: <#id>
    async def user_info(self, ctx, user: discord.Member):
        roles = ''
        perms = ''
        reached_end_of_user_perms = False
        for x in range(0, len(user.roles)):
            if roles == '':
                roles += f'{user.roles[x]}'
            else:
                roles += f', <@&{user.roles[x].id}>'

        perm_dict = iter(user.guild_permissions)
        while reached_end_of_user_perms != True:
            try:
                perm = next(perm_dict)
                if perm[1] == True:
                    if perms == '':
                        perms += f'{perm[0]}'
                    else:
                        perms += f', {perm[0]}'
            except StopIteration:
                reached_end_of_user_perms = True

        embed = discord.Embed(color=0x00ff00, title=f'<@{user.id}>')
        embed.set_author(name=f"{user}", icon_url=user.avatar_url)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="Name", value=user.name, inline=True)
        embed.add_field(name="ID", value=user.id, inline=True)

        embed.add_field(name="Account created", value=f"{dotw[user.created_at.weekday()-1]}, {user.created_at.day} {moty[user.created_at.month-1]} {user.created_at.year}", inline=True)
        embed.add_field(name="User joined", value=f"{dotw[user.joined_at.weekday()-1]}, {user.joined_at.day} {moty[user.joined_at.month]} {user.joined_at.year}", inline=True)

        embed.add_field(name="Bot", value=user.bot, inline=True)

        embed.add_field(name=f"Roles [{len(user.roles)}]", value=roles, inline=False)

        embed.add_field(name=f"Permissions", value=perms, inline=False)

        await ctx.send(embed=embed)

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
        await ctx.send(f'"{message}" is {len(message)} characters long.')

    #---------------------------------------------------------------------------------

    @commands.command(
        name='embed',
        help='Embeds a message with an optional title and hex colour',
    )

    async def embed_command(self, ctx, colour:int, title, *, content):
        embed = discord.Embed(color=colour)
        embed.add_field(
            name=title,
            value=content,
            inline=False
        )

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='say',
        description='Make the bot say something.',
        aliases=['parrot','repeat','copy']
    )

    async def say_command(self, ctx, *, message: str):
        await ctx.send(message)

    #---------------------------------------------------------------------------------

    #@commands.command(
    #    name='react',
    #    description='Reacts to your msg',
    #    aliases=[]
    #)

    #async def react_command(self, ctx):

    #---------------------------------------------------------------------------------

def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
