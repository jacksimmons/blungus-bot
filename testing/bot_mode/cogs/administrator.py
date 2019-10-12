import discord
from discord.ext import commands

from base import Base

dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Day of the week
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Month of the year

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

    @commands.group(
        name='advancedguildinfo',
        description='''Gives you all the available information about this guild.
        Note: it is recommended to use this in a private channel to prevent any unwanted information being seen by normal users.''',
        aliases=['agi','asi']
    )

    @commands.has_permissions(administrator=True)
    async def advanced_guild_info(self, ctx):
        guild = ctx.guild
        roles = ''
        categories = ''
        features = ''

        roles = Base.convert_long_list(guild.roles, 30, 250, guild.default_role)
        categories = Base.convert_long_list(guild.categories, 30, 250, guild.categories[len(guild.categories)-1])

        if guild.features == []:
            features = "None"
        else:
            for x in range(0, len(guild.features)):
                if features == '':
                    features = guild.features[x]
                else:
                    features += f', {guild.features[x]}'

        embed = discord.Embed(color=0x00ff00)
        embed.set_author(name=f"{guild.name}", icon_url=f"{guild.icon_url}")
        embed.set_footer(text=f"Guild ID: {guild.id} | Guild Owner: {guild.owner} | Guild Owner ID: {guild.owner_id} | Shard ID: {guild.shard_id} | Chunked: {guild.chunked}", icon_url=f"{ctx.author.avatar_url}")
#1
        embed.add_field(
        name="Region",
        value=f"{guild.region}")
#2
        embed.add_field(
        name=f"Emoji [Limit: {guild.emoji_limit}]",
        value=f"{len(guild.emojis)}")
#3
        embed.add_field(
        name=f"Channels [{len(guild.channels)}]",
        value=f"Text: {len(guild.text_channels)}, Voice: {len(guild.voice_channels)}")
#4
        embed.add_field(
        name=f"Members [{len(guild.members)}]",
        value=f"Human: number, Bot: number")
#5
        embed.add_field(
        name=f"Tier [Boosters: {len(guild.premium_subscribers)}]",
        value=f"{guild.premium_tier}")
#6
        embed.add_field(
        name="File Upload Limit",
        value=f"{guild.filesize_limit/1000000}MB")
#7
        embed.add_field(
        name="Bitrate Limit",
        value=f"{guild.bitrate_limit/1000} kbps")
#8
        embed.add_field(
        name=f"AFK Channel [AFK: {int(guild.afk_timeout/60)}m]",
        value=f"{guild.afk_channel}")
#9
        embed.add_field(
        name="2FA Level",
        value=f"{guild.mfa_level}")
#10
        embed.add_field(
        name="Default Notifications",
        value=f"{str(guild.default_notifications[0]).title()}")
#11
        embed.add_field(
        name="Verification Level",
        value=f"{str(guild.verification_level).title()}")
#12
        embed.add_field(
        name="Explicit Content Filter",
        value=f"{str(guild.explicit_content_filter).title()}")
#13
        embed.add_field(
        name="Guild Invite Splash",
        value=f"{guild.splash}")
#14
        embed.add_field(
        name="Extra Info",
        value=f"System Channel: <#{guild.system_channel.id}>, Large Guild: {guild.large}, Unavailable: {guild.unavailable}")
#before preantepenultimate 21
        embed.add_field(
        name="Guild Limits",
        value=f"Presences Limit: {guild.max_presences}, Member Limit: {guild.max_members}")
#preantepenultimate 22
        embed.add_field(
        name="Premium Guild Features",
        value=f"{features.title()}",
        inline=False)
#antepenultimate 23
        embed.add_field(
        name="Server created",
        value=f"{dotw[guild.created_at.weekday()-1]}, {guild.created_at.day} {moty[guild.created_at.month-1]} {guild.created_at.year} at {guild.created_at.hour}:{guild.created_at.minute}",
        inline=False)
#penultimate 24
        embed.add_field(
        name=f"Roles [{len(guild.roles)}]",
        value=f"{roles}",
        inline=False)
#ultimate 25
        embed.add_field(
        name=f"Categories [{len(guild.categories)}]",
        value=f"{categories}",
        inline=False)

        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='rename',
        description='Changes a user\'s nickname',
        aliases=['nick']
    )

    @commands.has_permissions(manage_nicknames=True)
    async def _rename(self, ctx, who: discord.Member, *, nickname):
        if who.top_role < ctx.message.author.top_role or ctx.message.author.id == ctx.guild.owner_id:
            changed = False
            if nickname == 'None':
                nickname = None
            await who.edit(nick=nickname)
        else:
            await ctx.send(f"<@{ctx.message.author.id}>, you cannot perform action `{ctx.command}` on a user with an equal or higher top role.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='kick',
        description='Kicks a user',
        aliases=[]
    )

    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, who: discord.Member, *, reason = None):
        if who.top_role < ctx.message.author.top_role or ctx.message.author.id == ctx.guild.owner_id:
            await ctx.guild.kick(user=who, reason=reason)
            await ctx.send(f'{who} was kicked for {reason}.\nID: `{who.id}`')

        elif who.id == self.bot.user.id:
            await ctx.send(f'I cannot kick myself! If you want me to leave, you can use `{self.bot.get_prefix(ctx.message)}leave`.')

        elif who.id != ctx.message.author.id:
            await ctx.send(f'<@{ctx.message.author.id}>, you are unable to kick someone with an equal or higher rank to you.')

        else:
            await ctx.send(f'<@{ctx.message.author.id}>, you cannot kick yourself!')

    #---------------------------------------------------------------------------------

    #@commands.command(
    #    name='role',
    #    description='Gives a user a role',
    #    aliases=[]
    #)

    #@commands.has_permissions(manage_)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='ban',
        description='Bans a user',
        aliases=[]
    )

    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, who: discord.Member, *, reason = None):
        ban = False
        if who.top_role < ctx.message.author.top_role or ctx.message.author.id == ctx.guild.owner_id:
            await ctx.guild.ban(user=who, reason=reason)
            await ctx.send(f'{who} was banned for {reason}.\nID: `{who.id}`')

        elif who.id == self.bot.user.id:
            await ctx.send(f'I cannot kick myself! If you want me to leave, you can use {self.bot.get_prefix(ctx.message)}leave.')

        elif who.id != ctx.message.author.id:
            await ctx.send(f'<@{ctx.message.author.id}>, you are unable to ban someone with an equal or higher rank to you.')

        else:
            await ctx.send(f'<@{ctx.message.author.id}>, you cannot ban yourself!')

    #---------------------------------------------------------------------------------

    #@commands.command(
    #    name='leave',
    #    description='Makes the bot leave the server',
    #    aliases=[]
    #)

    #@commands.has_permissions(administrator=True)
    #async def leave_command(self, ctx):
    #    await ctx.send("Are you sure you want me to leave? [y/n]")
    #    await ctx.message.add_reaction(emoji='💬')

    #    def check(msg):
    #        return msg.author == ctx.message.author

    #    msg = await self.bot.wait_for('message', check=check)
    #    await ctx.send("Bye mom!")
    #    await ctx.guild.leave()

    #@_ban.before_invoke()

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
    name='textchannel',
    help='Creates a Text Channel in your current guild. Requires the Manage Channels permission.',
    aliases=['tc'])

    async def _textchannel(self, ctx):
        pass

    @commands.has_permissions(manage_channels=True)
    async def _createtextchannel(self, ctx, name: str="Text Channel", category: discord.CategoryChannel=None, position: int=None, topic: str=None, nsfw: bool=None, slowmode_delay: int=None, reason: str=None):
        if 1 < len(name) < 100:
            if topic is not None:
                if len(topic) > 1024:
                    raise commands.CommandError("Please choose a channel topic that is 1024 or less characters in length.")

    #---------------------------------------------------------------------------------

            if slowmode_delay is not None:
                if slowmode_delay < 0 or slowmode_delay > 21600:
                    raise commands.CommandError("Please choose a delay between 0 and 21600 seconds.")

            c = await ctx.guild.create_text_channel(name=name, position=position, slowmode_delay=slowmode_delay, nsfw=nsfw, topic=topic, category=category, reason=reason)
            await ctx.send(f"The text channel {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")

    @commands.command(
        name='voicechannel',
        help='Creates a Voice Channel in your current guild. Requires the Manage Channels permission.',
        aliases=['voice','vc']
    )

    @commands.has_permissions(manage_channels=True)
    async def _createvoicechannel(self, ctx, name: str="Voice Channel", category: discord.CategoryChannel=None, position: int=None, user_limit: int=None, bitrate: int=None, reason: str=None):
        if 1 < len(name) < 100:
            c = await ctx.guild.create_voice_channel(name=name, category=category, position=position, user_limit=user_limit, bitrate=bitrate, reason=reason)
            await ctx.send(f"The voice channel {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")

    @commands.command(
        name='category',
        help='Creates a Channel Category in the current guild.',
        aliases=['cc']
    )

    @commands.has_permissions(manage_channels=True)
    async def _createcategory(self, ctx, name: str="Category", reason: str=None):
        if 1 < len(name) < 100:
            c = await ctx.guild.create_category(name=name, reason=reason)
            await ctx.send(f"The category {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------

def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Setup(bot))
