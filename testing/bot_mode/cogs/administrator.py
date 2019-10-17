import discord
import json
from discord.ext import commands

from base import Base

dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Days of the week
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Months of the year

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ban_entries = []
        self.m_converter = None
        self.u_converter = None

    #---------------------------------------------------------------------------------

    @commands.command(
        name='rename',
        help='Removes or changes a user\'s nickname',
        aliases=['nick']
    )

    @commands.has_permissions(manage_nicknames=True)
    async def _rename(self, ctx, member, *, nickname=None):
        #This command will by default remove a member's nickname, however if the 'nickname'
        #perameter is provided, the member will be given that nickname.

        who = await self.m_converter.convert(ctx, member)

        if who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if who.id != ctx.guild.owner_id: #Nobody can rename the owner
                await who.edit(nick=nickname)
            else:
                await ctx.send(f'{ctx.author.mention}, you don\'t have permissions to rename this member.')
        else:
            await ctx.send(f"{ctx.author.mention}, you cannot rename a user with an equal or higher top rank to you.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='kick',
        description='Kicks a user',
        aliases=[]
    )

    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member, *, reason=None):

        #This command will by default kick a member with no reason, however if the 'reason'
        #perameter is provided, then in the log for the member's kick this reason will be provided.

        who = await self.m_converter.convert(ctx, member) #Converts the 'member' perameter into a Member object

        if who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if who.id != ctx.guild.owner_id: #Nobody can kick the owner, so this shouldn't be an option.
                #We don't want the author to be able to kick someone lower than themselves in the role hierarchy,
                #however if they are the owner of the server they are able to bypass this rule.
                await ctx.guild.kick(user=who, reason=reason)
                await ctx.send(f'{who} was kicked for {reason}.\nID: `{who.id}`')
            else:
                await ctx.send(f'{ctx.author.mention}, you don\'t have permissions to kick this member.')

        elif who.id == self.bot.user.id:
            #We don't want the bot to be able to kick itself as this may cause unwanted issues
            await ctx.send(f'I cannot kick myself! If you want me to leave, you can use `{self.bot.command_prefix}leave`.')

        elif who.id == ctx.author.id:
            #We don't want members to be able to kick themselves as this may cause issues
            await ctx.send(f'{ctx.author.mention}, you cannot kick yourself!')

        else:
			#If the author is not trying to kick themself and they do not have sufficient permissions to kick the member
            await ctx.send(f'{ctx.author.mention}, you are unable to kick someone with an equal or higher top rank to you.')

    #---------------------------------------------------------------------------------

    @commands.command(
        name='ban',
        description='Bans a user',
        aliases=[]
    )

    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, user, delete_message_days: int=1, *, reason=None):

        content = ''
        s = False
        preban = False

        if delete_message_days > 7:
            delete_message_days = 7
            #await ctx.send("Deleting 7 days of messages (this is the maximum)")

        try: #Attempts to convert 'user' into a Guild.Member object for a standard ban
            who = await self.m_converter.convert(ctx, user)

        except: #If that fails, attempts to convert 'who' into a User object for a pre-emptive ban
            try:
                who = await self.u_converter.convert(ctx, user)
                preban = True #This is used to show whether the user/member banned was in the server or not at the time
                #In this case, they are just a user and not a member of the guild, so the ban is pre-emptive

            except TypeError:
                await ctx.send("`Invalid User or ID entered.`")

        if who not in [BanEntry.user for BanEntry in self.ban_entries]:
            #(Source needed)
            #This checks whether the user/member is in the list of banned members. Since every BanEntry is a tuple within the
            #guild.bans list, we need to use a 'generator' to check whether the user is in [a list of users for every BanEntry
            #in the ban entries list].

            if who in ctx.guild.members:
                #If the user is a member of the guild, we need to ensure the author is a higher rank than the victim
                #to prevent abuse of the bot, however if the user is not a member of the guild, this is not an issue.

                if who.id == self.bot.user.id:
                    #We don't want the bot to be able to ban itself as this may cause issues
                    await ctx.send('Don\'t make me do that!')

                elif who.id == ctx.author.id:
                    #We don't want the author to be able to ban themselves as this may cause issues
                    await ctx.send(f'{ctx.author.mention}, you cannot ban yourself!')

                elif who.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
                    if who.id != ctx.guild.owner_id: #Nobody can ban the owner, so this shouldn't be an option.
                        await ctx.guild.ban(user=who, reason=reason, delete_message_days=delete_message_days)
                        s = True
                    else:
                        await ctx.send(f'{ctx.author.mention}, you can\'t ban the owner!')

                else:
                    #The member cannot ban this member as they are lower in the hierarchy
                    await ctx.send(f'{ctx.author.mention}, you are unable to ban someone with an equal or higher rank to you.')

            else:
                await ctx.guild.ban(user=who, reason=reason, delete_message_days=delete_message_days)
                s = True

            if s == True:
                #The output for this command is more complex, so the variable 's' is used to determine when
                #the ban has been [s]uccessful and the output is then determined here.
                content = f'`{str(who)}` was banned.'
                if reason is not None:
                    content = content[:len(content)-1] + f' for `{reason}`.'
                if preban == True:
                    content += '[`Pre-ban`]'
                content += f'\nThe past `{delete_message_days} days` of messages for this user were deleted.'
                content += f'\nUser ID: `{str(who.id)}`'
                await ctx.send(content)

        else:
            await ctx.send(f'{ctx.author.mention}, this user is already banned.')

    #---------------------------------------------------------------------------------

    @commands.command(
        name='multiban',
        help='Bans multiple users at once (use with caution)'
    )

    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(administrator=True) #We don't want the bot being able to ban multiple people with just ban_members
    async def _mban(self, ctx, who: commands.Greedy[discord.User], delete_message_days=1, *, reason=None):
		#This command uses commands.Greedy, which takes in arguments of a certain type until no more are given,
		#allowing multiple users to be passed into the command at once, so this command is able to ban multiple users at once.

        failed_bans = ''
        successful_bans = []


        for x in range(0,len(who)):

            if who[x] not in [BanEntry.user for BanEntry in self.ban_entries]: #Generator to check the user is not already banned

                if who[x] in ctx.guild.members:

                    if who[x].id == self.bot.user.id: #We don't want the bot to be able to ban itself
                        failed_bans += f'\n`{who[x]}: Don\'t make me ban myself!`'

                    elif who[x].id == ctx.author.id: #We don't want the author to be able to ban themself
                        failed_bans += f'\n`{who[x]}: You cannot ban yourself!`'

                    elif who[x].id == ctx.guild.owner_id: #Nobody can ban the owner, so this prevents related errors from occurring
                        failed_bans += f'\n`{who[x]}: You can\'t ban the owner of the guild!'

                    elif who[x].top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id: #The ban was successful
                        successful_bans.append(who[x])

                    else: #The author does not have sufficient permissions to ban this user
                        failed_bans += f'\n`{who[x]}: You are unable to ban someone with an equal or higher rank to you.`'

                else:
                    #If the user is not a member and exists, the user is able to be banned.
                    await ctx.guild.ban(user=who[x], reason=reason, delete_message_days=delete_message_days)
                    successful_bans.append(who[x])

            else: #Otherwise, the member has already been banned.
                failed_bans += f'`{who[x]}: This user is already banned.`'


        if successful_bans != []: #If bans have already been successful, the 'content' variable needs to be set (for output).
            content = f'`Passed: {len(successful_bans)}`\n`{str(successful_bans)}` will be banned.'

            if reason is not None: #Add the reason on to the end of the string if there is one
                content = content[:len(content)-1] + f' for `{reason}`.'

            content += f'\nThe past `{delete_message_days} days` of messages for these members will be deleted.'

            if str([discord.Member.id for discord.Member in successful_bans]) != []: #Generator to check if the User ID list is empty
                content += f'\nUser IDs: `{str([discord.Member.id for discord.Member in successful_bans])}`'

        else: #Otherwise, set the content to empty
            content = ''

        if failed_bans != '': #If some bans have failed, add them to the content
            content += f'\n`Failed: {len(who) - len(successful_bans)}`{failed_bans}\n*The above users will not be banned.*\n'

        else: #Otherwise, mention that everything was a success
            content += 'All ban requests were successful.\n'

        #Confirmation that the author wants to ban these users, as this is a very powerful (and potentially dangerous) command.
        #They will need to type in the server name and '~ ban' to confirm this action.

        content += f'**WARNING: This action is irreversible. Are you sure you want to ban these {len(successful_bans)} users? **[Type in "`the name of this server` ~ ban" to confirm]'
        await ctx.send(content) #Sends the output

        def check(msg):
            #Returns a boolean as to whether the author is the same or not
            return msg.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)

        if msg.content != f'{ctx.guild.name} ~ ban':
            #This could be an else statement beneath the ban if statement, and is completely inefficient and pointless, but
            #just in case, this is placed above the if statement to ensure no accidental multibans occur.
            await ctx.send("`Operation cancelled.`")

        if msg.content == f'{ctx.guild.name} ~ ban':
            for x in range(0,len(successful_bans)):
                await ctx.guild.ban(user=successful_bans[x], reason=reason, delete_message_days=delete_message_days)
            await ctx.send(str(len(successful_bans)) + ' users were successfully banned.')

    #---------------------------------------------------------------------------------

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
            await ctx.send(f'{ctx.author.mention}, this user is not currently banned.')

    #---------------------------------------------------------------------------------

    @_kick.before_invoke
    @_ban.before_invoke
    @_mban.before_invoke
    @_unban.before_invoke
    async def check_ban_entries(self, ctx):
        self.ban_entries = await ctx.guild.bans()

    @_rename.before_invoke
    @_kick.before_invoke
    @_ban.before_invoke
    @_mban.before_invoke
    @_unban.before_invoke
    async def get_converters(self, ctx):
        self.u_converter = commands.UserConverter()
        self.m_converter = commands.MemberConverter()

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

    @commands.group(name='welcome', help='Customise where and how the welcome messages feature operates.')
    async def _welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_welcome.command(name='setchannel', help='Enables welcome messages in the channel provided.')
    async def enable_welcome_messages(self, ctx, channel):
        tc_converter = commands.TextChannelConverter() #Creates a TextChannelConverter object that will convert strings to TextChannels
        target = await tc_converter.convert(ctx, channel)

        import os
        os.chdir('../bot_mode')

        with open('data/guilds.json', 'r+') as file:
            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) in data:
                if 'channels' not in data[str(id)]:
                    data[str(id)]['channels'] = {} #Create a 'welcome' dictionary if one doesn't already exist
                data[str(id)]['channels']['welcome'] = target.id #Same outcome whether 'welcome_channel' exists already or not

            else:
                data[str(id)] = {}
                data[str(id)]['channels'] = {}
                data[str(id)]['channels']['welcome'] = target.id

            json.dump(data, file, indent=4)

            file.truncate() #Remove remaining part

        await ctx.send(f'Welcome channel has been set to {target.mention}!')

    #---------------------------------------------------------------------------------

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
                    await ctx.send("Please choose a channel topic that is 1024 or less characters in length.")

            if slowmode_delay is not None:
                if slowmode_delay < 0 or slowmode_delay > 21600:
                    await ctx.send("Please choose a delay between 0 and 21600 seconds.")

            c = await ctx.guild.create_text_channel(name=name, position=position, slowmode_delay=slowmode_delay, nsfw=nsfw, topic=topic, category=category, reason=reason)
            await ctx.send(f"The text channel {c.mention} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------

    @commands.group(name='voicechannel', help='Create, edit or delete a VoiceChannel.', aliases=['vc'])
    async def _voicechannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_voicechannel.command(name='create', help='Create a VoiceChannel.')
    @commands.has_permissions(manage_messages=True)
    async def _voicecreate(self, ctx, name="Voice Channel", category:discord.CategoryChannel=None, user_limit:int=None, position:int=None, bitrate:int=None):
        #Check if the Voice Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the user limit valid? (TBA)
        # - Is the bitrate valid? (TBA)

        if 1 < len(name) < 100:
            c = await ctx.guild.create_voice_channel(name=name, category=category, position=position, user_limit=user_limit, bitrate=bitrate, reason=reason)
            await ctx.send(f"The voice channel {c.mention} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------

    @commands.group(name='categorychannel', help='Create, edit or delete a CategoryChannel.', aliases=['category','cc'])
    async def _categorychannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_categorychannel.command(name='create', help='Create a channel category.')
    @commands.has_permissions(manage_channels=True)
    async def _categorycreate(self, ctx, name: str="Category", reason: str=None):
        #Check if the Category requested is valid and can be created;
        # - Is the name in between 1 and 100 characters long?
        if 1 < len(name) < 100:
            c = await ctx.guild.create_category(name=name, reason=reason)
            await ctx.send(f"The category {c.mention} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    #---------------------------------------------------------------------------------


def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Setup(bot))
