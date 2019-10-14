import discord
import json
from discord.ext import commands

from base import Base

dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Day of the week
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Month of the year

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ban_entries = []
        self.m_converter = None #Will convert from string to discord.Member object type
        self.u_converter = None #Will convert from string to discord.User object type
        self.info = {} #Information dictionary for this Guild
    
    #---------------------------------------------------------------------------------

    @commands.group(
        name='advancedguildinfo'
        description='''Gives you a large amount of available information about this guild.
        Note: it is recommended to use this in a private channel to prevent any unwanted information being seen by normal users.''',
        aliases=['agi','asi']
    )

    @commands.has_permissions(administrator=True)
    #We don't want normal users to see this information, so this check() ensures only users with the 'administrator'
    #permission can use this command.
    async def advanced_guild_info(self, ctx):
        
        #This variable (ctx.guild) is used a lot, so this helps simplify the code below
        guild = ctx.guild
        
        #Variable definitions
        roles = ''
        categories = ''
        features = ''
        
        self.update_info(ctx)
        
        #Uses a function in the Base module to convert the list (guild.roles) into a string
        roles = Base.convert_long_list(guild.roles, 30, 250, guild.default_role)
        
        #Uses a function in the Base module to convert the list (guild.categories) into a string
        categories = Base.convert_long_list(guild.categories, 30, 250, guild.categories[len(guild.categories)-1])

        #The (guild.features) list is much shorter, so it can be converted to a string right here:
        if guild.features == []:
            features = "None"
        else:
            for x in range(0, len(guild.features)):
                if features == '':
                    features = guild.features[x]
                else:
                    features += f', {guild.features[x]}'
                    
        #Create an embedded message with guild information in it with the colour theme R:0, G:255, B:0:
        embed = discord.Embed(color=0x00ff00) #R:0, G:255, B:0
        embed.set_author(info[name], icon_url=guild.icon_url) #The name of the Guild and the Guild's icon
        embed.set_footer(text=f"Guild ID: {guild.id} | Guild Owner: {guild.owner} | Guild Owner ID: {guild.owner_id} | Shard ID: {guild.shard_id} | Chunked: {guild.chunked}", icon_url=f"{ctx.author.avatar_url}")

        #Syntax: Embed.add_field(name[str], value[str], inline[bool])
        embed.add_field("Region", info['region']) #1: name, value
        embed.add_field(f"Emoji [Limit: {guild.emoji_limit}]", len(guild.emojis)) #2: name, value
        embed.add_field(name=f"Channels [{len(guild.channels)}]", value=f"Text: {len(guild.text_channels)}, Voice: {len(guild.voice_channels)}")
#4
        embed.add_field(name=f"Members [{len(guild.members)}]", value=f"Human: number, Bot: number")
#5
        embed.add_field(name=f"Tier [Boosters: {len(guild.premium_subscribers)}]", value=f"{guild.premium_tier}")
#6
        embed.add_field(name="File Upload Limit", value=f"{guild.filesize_limit/1000000}MB")
#7
        embed.add_field(name="Bitrate Limit", value=f"{guild.bitrate_limit/1000} kbps")
#8
        embed.add_field(name=f"AFK Channel [AFK: {guild.afk_timeout/60}m]", value=f"{guild.afk_channel}")
#9
        embed.add_field(name="2FA Level", value=f"{guild.mfa_level}")
#10
        embed.add_field(name="Default Notifications", value=f"{str(guild.default_notifications[0]).title()}")
#11
        embed.add_field(name="Verification Level", value=f"{str(guild.verification_level).title()}")
#12
        embed.add_field(name="Explicit Content Filter", value=f"{str(guild.explicit_content_filter).title()}")
#13
        embed.add_field(name="Guild Invite Splash", value=f"{guild.splash}")
#14
        embed.add_field(name="Extra Info",
        value=f"System Channel: {guild.system_channel.mention}, Large Guild: {guild.large}, Unavailable: {guild.unavailable}",
        inline=False)
#before preantepenultimate 21
        embed.add_field(name="Guild Limits",
        value=f"Presences Limit: {guild.max_presences}, Member Limit: {guild.max_members}",
        inline=False)
#preantepenultimate 22
        embed.add_field(name="Premium Guild Features",
        value=f"{features.title()}",
        inline=False)
#antepenultimate 23
        embed.add_field(name="Server created",
        value=f"{dotw[guild.created_at.weekday()-1]}, {guild.created_at.day} {moty[guild.created_at.month-1]} {guild.created_at.year} at {guild.created_at.hour}:{guild.created_at.minute}",
        inline=False)
#penultimate 24
        embed.add_field(name=f"Roles [{len(guild.roles)}]",
        value=f"{roles}",
        inline=False)
#ultimate 25
        embed.add_field(name=f"Categories [{len(guild.categories)}]",
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
        if who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if nickname == 'None':
                nickname = None
            await who.edit(nick=nickname)
        else:
            await ctx.send(f"{ctx.author.mention}, you cannot perform action `{ctx.command}` on a user with an equal or higher top role.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='kick',
        description='Kicks a user',
        aliases=[]
    )

    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, who: discord.Member, *, reason=None):
        if who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            await ctx.guild.kick(user=who, reason=reason)
            await ctx.send(f'{who} was kicked for {reason}.\nID: `{who.id}`')

        elif who.id == self.bot.user.id:
            await ctx.send(f'I cannot kick myself! If you want me to leave, you can use `{self.bot.get_prefix(ctx.message)}leave`.')

        elif who.id != ctx.author.id:
            await ctx.send(f'{ctx.author.mention}, you are unable to kick someone with an equal or higher rank to you.')

        else:
            await ctx.send(f'{ctx.author.mention}, you cannot kick yourself!')

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
    async def _ban(self, ctx, who, delete_message_days: int=1, *, reason=None):

        content = ''
        s = False
        preban = False

        if delete_message_days > 7:
            delete_message_days = 7
            #await ctx.send("Deleting 7 days of messages (this is the maximum)")

        try: #Attempts to convert 'who' into a Guild.Member object for a standard ban
            who = await self.m_converter.convert(ctx, who)

            await ctx.send(f"Member to be banned: `{who}` [Type `y` to confirm]")
            def check(msg):
                return msg.author == ctx.author

            msg = await self.bot.wait_for('message', check=check)

            if msg.content != 'y':
                raise commands.CommandError("`Operation cancelled.`")

        except: #If fail, attempts to convert 'who' into a Guild.User object for a pre-emptive ban
            who = await self.u_converter.convert(ctx, who)
            preban = True

                #except TypeError:
                #    raise commands.CommandError("`Invalid User or ID entered.`")

        #print(str([BanEntry.user.id for BanEntry in self.ban_entries]))
        if who not in [BanEntry.user for BanEntry in self.ban_entries]:

            if who in ctx.guild.members:
                who = ctx.guild.get_member(who.id)

                if who.id == self.bot.user.id:
                    raise commands.CommandError('Don\'t make me do that!')

                elif who.id == ctx.author.id:
                    raise commands.CommandError(f'{ctx.author.mention}, you cannot ban yourself!')

                elif who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
                    await ctx.guild.ban(user=who, reason=reason, delete_message_days=delete_message_days)
                    s = True

                elif who.id != ctx.author.id:
                    raise commands.CommandError(f'{ctx.author.mention}, you are unable to ban someone with an equal or higher rank to you.')

            else:
                await ctx.guild.ban(user=who, reason=reason, delete_message_days=delete_message_days)
                s = True
            if s == True:
                content = f'`{str(who)}` was banned.'
                if reason is not None:
                    content = content[:len(content)-1] + f' for `{reason}`.'
                if preban == True:
                    content += '[`Pre-ban`]'
                content += f'\nThe past `{delete_message_days} days` of messages for this user were deleted.'
                content += f'\nUser ID: `{str(who.id)}`'
                await ctx.send(content)

        else:
            raise commands.CommandError(f'{ctx.author.mention}, this user is already banned.')

    #---------------------------------------------------------------------------------

    @commands.command(
        name='multiban',
        help='Bans multiple users at once (use with caution)'
    )

    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True) #We don't want the bot being able to ban everyone with just ban_members
    async def _mban(self, ctx, who: commands.Greedy[discord.Member], delete_message_days=1, *, reason=None):
        failed_bans = ''
        successful_bans = []

        for x in range(0,len(who)):
            if who[x] not in [BanEntry.user for BanEntry in self.ban_entries]:
                if who[x] in ctx.guild.members:
                    if who[x].id == self.bot.user.id:
                        failed_bans += f'\n`{who[x]}: Don\'t make me ban myself!`'

                    elif who[x].id == ctx.author.id:
                        failed_bans += f'\n`{who[x]}: You cannot ban yourself!`'

                    elif who[x].id != ctx.author.id:
                        failed_bans += f'\n`{who[x]}: You are unable to ban someone with an equal or higher rank to you.`'

                    elif who[x].top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
                        successful_bans.append(who[x])

                else:
                    await ctx.guild.ban(user=who[x], reason=reason, delete_message_days=delete_message_days)
                    successful_bans.append(who[x])
            else:
                failed_bans += f'`{who[x]}: This user is already banned.`' #This should never happen; a User is not a Member if they are banned from the guild.
        if successful_bans != []:
            content = f'`Passed: {len(successful_bans)}`\n`{str(successful_bans)}` will be banned.'
            if reason is not None:
                content = content[:len(content)-1] + f' for `{reason}`.'
            content += f'\nThe past `{delete_message_days} days` of messages for these members will be deleted.'
            if str([discord.Member.id for discord.Member in successful_bans]) != []:
                content += f'\nUser IDs: `{str([discord.Member.id for discord.Member in successful_bans])}`'
        else:
            content = ''
        if failed_bans != '':
            content += f'\n`Failed: {len(who) - len(successful_bans)}`{failed_bans}\n*The above users will not be banned.*\n'
        else:
            content += 'All ban requests were successful.\n'
        content += f'**WARNING: This action is irreversible. Are you sure you want to ban these {len(successful_bans)} users? **[Type in "`the name of this server` ~ ban" to confirm]'
        await ctx.send(content)

        def check(msg):
            return msg.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)

        if msg.content != f'{ctx.guild.name} ~ ban':
            #This could be an else statement beneath the ban if statement, and is completely inefficient and pointless, but
            #just in case, this is placed above the if statement to ensure no accidental multibans occur.
            raise commands.CommandError("`Operation cancelled.`")

        if msg.content == f'{ctx.guild.name} ~ ban':
            for x in range(0,len(successful_bans)):
                await ctx.guild.ban(user=successful_bans[x], reason=reason, delete_message_days=delete_message_days)


    @commands.command(
        name='unban',
        help='Unbans a banned user'
    )

    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx, who, *, reason=None):
        who = await self.u_converter.convert(ctx, who)

        if who in [BanEntry.user for BanEntry in self.ban_entries]:
            await ctx.guild.unban(user=who, reason=reason)
            content = f'`{str(who)}` was unbanned.'
            if reason is not None:
                content = content[:len(content)-1] + f' for `{reason}`.'
            content += f'\nUser ID: `{str(who.id)}`'
            await ctx.send(content)

        else:
            raise commands.CommandError(f'{ctx.author.mention}, this user is not currently banned.')

    @_ban.before_invoke
    @_unban.before_invoke
    @_mban.before_invoke
    async def check_ban_entries(self, ctx):
        from discord.ext.commands import MemberConverter
        from discord.ext.commands import UserConverter
        self.ban_entries = await ctx.guild.bans()
        self.u_converter = UserConverter()
        self.m_converter = MemberConverter()
        print(self.ban_entries)

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
    #        return msg.author == ctx.author

    #    msg = await self.bot.wait_for('message', check=check)
    #    await ctx.send("Bye mom!")
    #    await ctx.guild.leave()

    #@_ban.before_invoke()

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='textchannel', help='Create, edit or delete a TextChannel.', aliases=['tc'])
    async def _textchannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_textchannel.command(name='create', help='Create a TextChannel.')
    @commands.has_permissions(manage_messages=True)
    async def _textcreate(self, ctx, name='text-channel', topic=None, category:discord.CategoryChannel=None, position:int=None, slowmode_delay:int=None, nsfw:bool=None, reason=None):
        #Check if the Text Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the length of the topic less than 1024 characters long?
        # - Is the slowmode delay valid and less than 6 hours?
                          
        if 1 < len(name) < 100:
            if topic is not None:
                if len(topic) > 1024:
                    raise commands.CommandError("Please choose a channel topic that is 1024 or less characters in length.")
                          
            if slowmode_delay is not None:
                if slowmode_delay < 0 or slowmode_delay > 21600:
                    raise commands.CommandError("Please choose a delay between 0 and 21600 seconds.")

            c = await ctx.guild.create_text_channel(name=name, position=position, slowmode_delay=slowmode_delay, nsfw=nsfw, topic=topic, category=category, reason=reason)
            await ctx.send(f"The text channel {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------
    
    @commands.group(name='voicechannel', help='Create, edit or delete a VoiceChannel.', aliases=['vc'])
    async def _voicechannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")
    
    @_voicechannel.command(name='create', help='Create a VoiceChannel.')
    @commands.has_permissions(manage_messages=True)
    async def _voicecreate(self, ctx, name="Voice Channel", category:discord.CategoryChannel=None, user_limit:int=None, position:int=None, bitrate
        #Check if the Voice Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the user limit valid? (TBA)
        # - Is the bitrate valid? (TBA)
                           
        if 1 < len(name) < 100:
            c = await ctx.guild.create_voice_channel(name=name, category=category, position=position, user_limit=user_limit, bitrate=bitrate, reason=reason)
            await ctx.send(f"The voice channel {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")
    
    #---------------------------------------------------------------------------------
                           
    @commands.group(name='categorychannel', help='Create, edit or delete a CategoryChannel.', aliases=['category','cc'])
    async def _categorychannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @commands.has_permissions(manage_channels=True)
    async def _categorycreate(self, ctx, name: str="Category", reason: str=None):
        if 1 < len(name) < 100:
            c = await ctx.guild.create_category(name=name, reason=reason)
            await ctx.send(f"The category {c.mention} has been created!")
        else:
            raise commands.CommandError("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------
                           
def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Setup(bot))
