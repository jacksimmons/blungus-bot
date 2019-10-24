import discord
import json
from discord.ext import commands

from base import Base

#https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date-in-python
#Get the day of the week from a date

dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Days of the week in string format
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Months of the year in string format


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ban_entries = []
        self.m_converter = None
        self.u_converter = None

    #---------------------------------------------------------------------------------

    @commands.group(
        name='tags',
        help='List, create or delete tags in this guild.',
        invoke_without_command=True
    )

    async def _tags(self, ctx):

        import os
        os.chdir('../bot_mode')

        with open('data/guilds.json', 'r') as file:
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0)

            if str(id) in data:
                if 'tags' in data[str(id)]:

                    content = ''

                    for tag in data[str(id)]['tags']:
                        if content == '':
                            content = tag
                        else:
                            content += f', {tag}'

                    if len(content) >= 1024:
                        content = content[:1000] + ' ...'

                    embed = discord.Embed(colour=0x100000)
                    embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
                    embed.add_field(name="Tags", value=content, inline=False)

                    await ctx.send(embed=embed)

                else:
                    raise commands.CommandError(ctx.author.mention + ', no tags have been created yet for this guild.')
            else:
                raise commands.CommandError(ctx.author.mention + ', no data is being stored for this guild (this includes tags).')

    #---------------------------------------------------------------------------------

    @_tags.command(name='create')
    async def _tagcreate(self, ctx, name, *, value):
        """Create a tag."""

        if len(name) <= 30:

            import os
            os.chdir('../bot_mode')

            with open('data/guilds.json', 'r+') as file:

                #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
                #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
                #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
                data = json.load(file)
                id = ctx.guild.id

                file.seek(0) # Reset file position to the beginning

                if str(id) not in data:
                    data[str(id)] = {}
                if 'tags' not in data[str(id)]:
                    data[str(id)]['tags'] = {}
                if name not in data[str(id)]['tags']:
                    data[str(id)]['tags'][name] = value
                    json.dump(data, file, indent=4)
                    file.truncate() #Remove remaining part
                else:
                    raise commands.CommandError(f"Tag `{name}` already exists.")

            if len(value) < 500:
                await ctx.send(f"Tag `{name}` has been created.")
            else:
                await ctx.send("That tag has been created.")

        else:
            raise commands.CommandError(f"{ctx.author.mention}, tag names can be a maximum of 30 characters long.")

    @_tags.command(name='delete')
    async def _tagdelete(self, ctx, *, name):
        """Delete a tag."""

        with open('data/guilds.json', 'r+') as file:

            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) not in data:
                data[str(id)] = {}
            if 'tags' not in data[str(id)]:
                data[str(id)]['tags'] = {}
            if name in data[str(id)]['tags']:
                data[str(id)]['tags'].pop(name, None)
                #This removes the need to check if this variable exists;
                #If there is a {tag name}, it will get removed.
                #If not, it will remove None, which removes nothing.
                #Source: https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary
                json.dump(data, file, indent=4)
                file.truncate() #Remove remaining part
            else:
                raise commands.CommandError(f"Invalid tag name: Tag `{name}` does not exist.")

        await ctx.send(f"Tag `{name}` has been deleted.")

    #---------------------------------------------------------------------------------

    @commands.command(
        name='tag',
        help='Displays one of the guild\'s tags.',
    )

    async def _tag(self, ctx, *, name):

        import os
        os.chdir('../bot_mode')

        with open('data/guilds.json', 'r') as file:
            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) not in data:
                data[str(id)] = {}
                raise commands.CommandError(ctx.author.name + ": No tags have been created yet. Use the `tags` command group to add one.")
            else:
                if 'tags' not in data[str(id)]:
                    raise commands.CommandError(ctx.author.name + ": No tags have been created yet. Use the `tags` command group to add one.")
                else:
                    if name in data[str(id)]['tags']:
                        await ctx.send(data[str(id)]['tags'][name])

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
            #https://wiki.python.org/moin/Generators
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

    @commands.has_permissions(administrator=True) #We don't want members able to ban multiple people with just ban_members
    @commands.bot_has_permissions(ban_members=True)
    async def _mban(self, ctx, who: commands.Greedy[discord.User], delete_message_days=1, *, reason=None):
        #This command uses commands.Greedy, which takes in arguments of a certain type until no more are given,
        #allowing multiple users to be passed into the command at once, so this command is able to ban multiple users at once.

        failed_bans = ''
        successful_bans = []

        if delete_message_days < 0:
            delete_message_days = 0
            await ctx.send("`Delete message days` must be an integer between `0 and 7` inclusive, so it has been set to 0.")

        elif delete_message_days > 7:
            delete_message_days = 7
            await ctx.send("`Delete message days` must be an integer between `0 and 7` inclusive, so it has been set to 7.")
        for x in range(0,len(who)):

            if who[x] not in [BanEntry.user for BanEntry in self.ban_entries]: #Generator to check the user is not already banned

                if who[x] in ctx.guild.members:
                    member = await self.m_converter.convert(ctx, str(who[x]))

                    if member.id == self.bot.user.id: #We don't want the bot to be able to ban itself
                        failed_bans += f'\n`{member}: Don\'t make me ban myself!`'

                    elif member.id == ctx.author.id: #We don't want the author to be able to ban themself
                        failed_bans += f'\n`{member}: You cannot ban yourself!`'

                    elif member.id == ctx.guild.owner_id: #Nobody can ban the owner, so this prevents related errors from occurring
                        failed_bans += f'\n`{member}: You can\'t ban the owner of the guild!`'

                    elif member.top_role >= ctx.guild.get_member(self.bot.user.id).top_role:
                        failed_bans += f'\n`{member}: I cannot ban this user.`'

                    elif member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id: #The ban was successful
                        successful_bans.append(member)

                    else: #The author does not have sufficient permissions to ban this user
                        failed_bans += f'\n`{member}: You are unable to ban someone with an equal or higher rank to you.`'

                else:
                    #If the user is not a member and exists, the user is able to be banned.
                    await ctx.guild.ban(user=who[x], reason=reason, delete_message_days=delete_message_days)
                    successful_bans.append(who[x])

            else: #Otherwise, the member has already been banned.
                failed_bans += f'`{who[x]}: This user is already banned.`'


        if successful_bans != []: #If bans have already been successful, the 'content' variable needs to be set (for output).
            successful_ban_list = [discord.Member.name for discord.Member in successful_bans]
            content = f'`Passed: {len(successful_bans)}`\n`{str(successful_ban_list)}` will be banned.'

            if reason is not None: #Add the reason on to the end of the string if there is one
                content = content[:len(content)-1] + f' for `{reason}`.'

            content += f'\nThe past `{delete_message_days} days` of messages for these members will be deleted.'

            if str([discord.Member.id for discord.Member in successful_bans]) != []: #Generator to check if the User ID list is empty
                content += f'\nUser IDs: `{str([discord.Member.id for discord.Member in successful_bans])}`'

        else: #Otherwise, set the content to empty
            content = ''

        if failed_bans != '': #If some bans have failed, add them to the content
            content += f'\n`Failed: {len(who) - len(successful_bans)}`{failed_bans}\n'

        else: #Otherwise, mention that everything was a success
            content += '\nAll ban requests were successful.\n'

        #Confirmation that the author wants to ban these users, as this is a very powerful (and potentially dangerous) command.
        #They will need to type in the server name and '~ ban' to confirm this action.

        if successful_bans != []:
            content += f'**WARNING: This action is irreversible. Are you sure you want to ban these {len(successful_bans)} users? **[Type in "`{ctx.guild.name}` yes" to confirm]'
            await ctx.send(content) #Sends the output

        else:
            raise commands.CommandError('Cancelling - every ban request failed.')

        def check(msg):
            #Returns a boolean as to whether the author is the same or not
            return msg.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)

        if msg.content != f'{ctx.guild.name} yes':
            #This could be an else statement beneath the ban if statement, and is completely inefficient and pointless, but
            #just in case, this is placed above the if statement to ensure no accidental multibans occur.
            await ctx.send("`Operation cancelled.`")

        if msg.content == f'{ctx.guild.name} yes':
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

    #A class which allows Members to create, modify or delete new Guild-related objects.
    #It is ordered by the order of the object in question in relation to the 'Discord
    #Models' section of the official documentation from top to bottom:

    #Message > Reaction > Guild > Member > Emoji > Role > [Text > Voice > Category]Channel > Invite > Widget
    
    
    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

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
                data[str(id)]['channels']['welcome'] = target.i

            json.dump(data, file, indent=4)

            file.truncate() #Remove remaining part

        await ctx.send(f'Welcome channel has been set to {target.mention}!')

    #---------------------------------------------------------------------------------
    #Command group for creating, getting information about, editing and deleting 'Roles'
    #---Roles are named tags which can be added to Members to give them specific permissions,
    #---allow them to see private channels, change the colour of their Usernames, etc.

    @commands.group(name='role', help='Interact with or create new roles.')
    async def _role(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_role.command(name='create', help='Create a new Role.')
    @commands.has_permissions(manage_roles=True)
    async def _rolecreate(self, ctx, name=None, colour:discord.Colour=None, hoist:bool=False, mentionable:bool=False, *, reason=None):
        await ctx.guild.create_role(name=name, colour=colour, hoist=hoist, mentionable=mentionable, reason=reason)
        if len(name) < 100:
            await ctx.send(f'{role.mention} has been created!')
        else:
            await ctx.send('Role has been created!')

    @_role.command(name='info', help='Display some information about an existing Role.')
    @commands.has_permissions(manage_roles=True)
    async def _roleinfo(self, ctx, *, role:discord.Role):

        perms = None

        embed = discord.Embed(colour=role.colour) #Create an embed
        embed.set_author(name=f'Role Info', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        if len(role.name) <= 1024:
            name = role.name
        else:
            name = role.name[:1020] + ' ...'

        perm_dict = iter(role.permissions)

        while True:
            try:
                perm = next(perm_dict)
                if perm[1] == True:
                    if perms is not None:
                        perms += f', {perm[0]}'
                    else:
                        perms = perm[0]

            except StopIteration:
                break

        formatted_perms = perms.title().replace("_", " ")

        embed.add_field(name='Name', value=name, inline=False)

        embed.add_field(name='ID', value=role.id)
        embed.add_field(name='Hoisted', value=role.hoist)
        embed.add_field(name='Mentionable', value=role.mentionable)

        embed.add_field(name='Created at', value=f'{dotw[role.created_at.weekday()-1]}, {role.created_at.day} {moty[role.created_at.month-1]} {role.created_at.year}')
        embed.add_field(name='Position', value=role.position)
        embed.add_field(name='Managed', value=role.managed)

        embed.add_field(name='Colour [Hex]', value=str(role.colour))
        embed.add_field(name='Colour [Raw]', value=hash(role.colour))
        embed.add_field(name='Colour [RGB]', value=role.colour.to_rgb())

        embed.add_field(name='Permissions', value=formatted_perms)

        await ctx.send(embed=embed)

    @_role.command(name='edit', help='Edit an existing Role.')
    @commands.has_permissions(manage_roles=True)
    async def _roleedit(self, ctx, role:discord.Role, name=None, colour:discord.Colour=None, hoist:bool=False, mentionable:bool=False, position:int=None, *, reason=None):
        await role.edit(name=name, colour=colour, hoist=hoist, mentionable=mentionable, position=position, reason=reason)
        if len(name) < 100:
            await ctx.send(f'{role.mention} has been updated.')
        else:
            await ctx.send('Role has been updated.')

    @_role.command(name='delete', help='Delete an existing Role.')
    @commands.has_permissions(manage_roles=True)
    async def _roledel(self, ctx, role:discord.Role, reason=None):
        await role.delete(reason=reason)
        await ctx.send('Role has been deleted.')

    #---------------------------------------------------------------------------------
    #---A command group to allow Members to create, clone, view information about, see
    #---invites for, see pinned messages for, see webhooks for, edit and delete
    #---TextChannels.

    @commands.group(name='textchannel', help='Interact with or create Text Channels.', aliases=['tc'])
    async def _textchannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_textchannel.command(name='create', help='Create a Text Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _textcreate(self, ctx, name='text-channel', topic=None, category:discord.CategoryChannel=None, slowmode_delay:int=None, position:int=None, nsfw:bool=None, *, reason=None):
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
            await ctx.send(f"Text Channel {c.mention} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    @_textchannel.command(name='clone', help='Clones a Text Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _textclone(self, ctx, channel_to_clone:discord.TextChannel, name=None, *, reason=None):
        cloned_channel = await channel_to_clone.clone(name=name, reason=reason)
        await ctx.send(f'Text Channel {channel_to_clone.mention} has been cloned to create {cloned_channel.mention}!')

    @_textchannel.command(name='info', help='Display some information about an existing Text Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _textinfo(self, ctx, *, target:discord.TextChannel):

        embed = discord.Embed() #Create an embed
        embed.set_author(name=f'{target.mention}', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='ID', value=target.id)
        embed.add_field(name='Category', value=target.category)
        embed.add_field(name='Category ID', value=target.category_id)

        embed.add_field(name='Topic', value=target.topic)
        embed.add_field(name='News Channel', value=target.is_news())
        embed.add_field(name='NSFW Channel', value=target.is_nsfw())

        embed.add_field(name='Created at', value=f'{dotw[target.created_at.weekday()-1]}, {target.created_at.day} {moty[target.created_at.month-1]} {target.created_at.year}')
        embed.add_field(name='Slowmode delay', value=target.slowmode_delay)
        embed.add_field(name='Position', value=target.position)

        embed.add_field(name='Permissions synced', value=target.permissions_synced)

        changed_roles = await Base.convert_long_list(target.changed_roles, 50, 900)
        #Make the max total length slightly below the maximum embed value length which is 1024.

        embed.add_field(name='Changed roles', value=changed_roles, inline=False)

        last_message = target.last_message[:300]
        if len(target.last_message) >= 300:
            last_message += '[...]'

        embed.add_field(name='last_message', value=last_message, inline=False)

        await ctx.send(embed=embed)

    @_textchannel.command(name='invites', help='Displays all invites currently leading to this Text Channel.')
    @commands.has_permissions(manage_guild=True)
    async def _textinvites(self, ctx, *, channel:discord.TextChannel):

        invites = await Base.convert_long_list(channel.invites(), 100, 1000)

        embed = discord.Embed()
        embed.set_author(name=channel.mention, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='Invites', value=invites)

    @_textchannel.command(name='pins', help='Displays all pinned messages in this Text Channel.')
    async def _textpins(self, ctx, *, channel:discord.TextChannel):

        pins = [message.id for message in (await channel.pins())]

        embed = discord.Embed()
        embed.set_author(name=f'📌Pins', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        if len(pins) == 0:
            pins = 'There are no pinned messages in this channel.'
        embed.add_field(name='Channel', value=channel.mention, inline=False)
        embed.add_field(name='Pins', value=str(pins), inline=False)

        await ctx.send(embed=embed)

    @_textchannel.command(name='webhooks', help='Displays all webhooks associated with this Text Channel.')
    @commands.has_permissions(manage_webhooks=True)
    async def _textwebhooks(self, ctx, *, channel:discord.TextChannel):

        webhooks = [webhook.name for webhook in (await channel.webhooks())]

        embed = discord.Embed()
        embed.set_author(name=f'Webhooks', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        if len(webhooks) == 0:
            webhooks = 'There are no webhooks associated with this channel.'
        embed.add_field(name='Channel', value=channel.mention, inline=False)
        embed.add_field(name='Webhooks', value=str(webhooks), inline=False)

        await ctx.send(embed=embed)

    @_textchannel.command(name='edit', help='Edit an existing Text Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _textedit(self, ctx, channel:discord.TextChannel, name, topic=None, category:discord.CategoryChannel=None, slowmode_delay:int=None, position:int=None, nsfw:bool=None, sync_perms:bool=None, *, reason=None):
        await channel.edit(name=name, topic=topic, position=position, nsfw=nsfw, sync_permissions=sync_perms, category=category, slowmode_delay=slowmode_delay, reason=None)
        await ctx.send(f'Text Channel {channel.mention} has been updated.')

    @_textchannel.command(name='delete', help='Deletes an existing Text Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _textdel(self, ctx, channel:discord.TextChannel, *, reason=None):
        await channel.delete(reason=reason)
        await ctx.send(f'Text Channel {channel.mention} has been deleted.')

    #---------------------------------------------------------------------------------
    #---A command group to allow Members to create, clone, view information about,
    #---see invites for, edit and delete VoiceChannels.

    @commands.group(name='voicechannel', help='Interact with or create new Voice Channels.', aliases=['vc'])
    async def _voicechannel(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_voicechannel.command(name='create', help='Create a VoiceChannel.')
    @commands.has_permissions(manage_messages=True)
    async def _voicecreate(self, ctx, name="Voice Channel", category:discord.CategoryChannel=None, user_limit:int=None, bitrate:int=None, position:int=None, *, reason=None):
        #Check if the Voice Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the user limit valid? (TBA)
        # - Is the bitrate valid? (TBA)

        if 1 < len(name) < 100:
            c = await ctx.guild.create_voice_channel(name=name, category=category, position=position, user_limit=user_limit, bitrate=bitrate, reason=reason)
            await ctx.send(f"The voice channel {c.name} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    @_voicechannel.command(name='clone', help='Clones a Voice Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _voiceclone(self, ctx, channel_to_clone:discord.VoiceChannel, name=None, reason=None):
        cloned_channel = await channel_to_clone.clone(name=name, reason=reason)
        await ctx.send(f'Voice Channel {channel_to_clone.name} has been cloned to create {cloned_channel.name}!')

    @_voicechannel.command(name='info', help='Display some information about an existing Voice Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _voiceinfo(self, ctx, target:discord.VoiceChannel):

        embed = discord.Embed() #Create an embed
        embed.set_author(name=f'{target.mention}', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='ID', value=target.id)
        embed.add_field(name='Category', value=target.category)
        embed.add_field(name='Category ID', value=target.category_id)

        embed.add_field(name='Bitrate', value=target.bitrate)
        embed.add_field(name='User Limit', value=target.user_limit)
        embed.add_field(name='Created at', value=f'{dotw[target.created_at.weekday()-1]}, {target.created_at.day} {moty[target.created_at.month-1]} {target.created_at.year}')

        embed.add_field(name='Position', value=target.position)
        embed.add_field(name='Permissions synced', value=target.permissions_synced)

        changed_roles = await Base.convert_long_list(target.changed_roles, 50, 900)
        #Make the max total length slightly below the maximum embed value length which is 1024.

        embed.add_field(name='Changed roles', value=changed_roles, inline=False)

        await ctx.send(embed=embed)

    @_voicechannel.command(name='invites', help='Displays all invites currently leading to this Voice Channel.')
    @commands.has_permissions(manage_guild=True)
    async def _voiceinvites(self, ctx, channel:discord.VoiceChannel):

        invites = await Base.convert_long_list(channel.invites(), 100, 1000)

        embed = discord.Embed()
        embed.set_author(name=channel.mention, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='Invites', value=invites)

    @_voicechannel.command(name='edit', help='Edit an existing Voice Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _voiceedit(self, ctx, channel:discord.VoiceChannel, name, user_limit:int=None, bitrate:int=None, category:discord.CategoryChannel=None, position:int=None, sync_perms:bool=None, *, reason=None):
        await channel.edit(name=name, bitrate=bitrate, user_limit=user_limit, position=position, sync_permissions=sync_perms, category=category, reason=None)
        await ctx.send(f'Voice Channel {channel.name} has been updated.')

    @_voicechannel.command(name='delete', help='Deletes an existing Voice Channel.')
    @commands.has_permissions(manage_channels=True)
    async def _voicedel(self, ctx, channel:discord.VoiceChannel, reason=None):
        await channel.delete(reason=reason)
        await ctx.send(f'Voice Channel {channel.name} has been deleted.')

    #---------------------------------------------------------------------------------
    #---A command group to allow Members to create, clone, view information about, edit
    #---and delete CategoryChannels.

    @commands.group(name='categorychannel', help='Interact with or create new Categories.', aliases=['category','cc'])
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
            await ctx.send(f"The category {c.name} has been created!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    @_categorychannel.command(name='clone', help='Clones a Category.')
    @commands.has_permissions(manage_channels=True)
    async def _categoryclone(self, ctx, category_to_clone:discord.CategoryChannel, name=None, reason=None):
        cloned_channel = await channel_to_clone.clone(name=name, reason=reason)
        await ctx.send(f'Category {category_to_clone.name} has been cloned to create {cloned_channel.name}!')

    @_categorychannel.command(name='info', help='Display some information about an existing Category.')
    @commands.has_permissions(manage_channels=True)
    async def _categoryinfo(self, ctx, target:discord.CategoryChannel):

        embed = discord.Embed() #Create an embed
        embed.set_author(name=f'{target.name}', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='ID', value=target.id)
        embed.add_field(name='NSFW Category', value=target.is_nsfw())
        embed.add_field(name='Created at', value=f'{dotw[target.created_at.weekday()-1]}, {target.created_at.day} {moty[target.created_at.month-1]} {target.created_at.year}')

        embed.add_field(name='Position', value=target.position)

        changed_roles = await Base.convert_long_list(target.changed_roles, 50, 900)
        #Make the max total length slightly below the maximum embed value length which is 1024.

        embed.add_field(name='Changed roles', value=changed_roles, inline=False)

        await ctx.send(embed=embed)

    @_categorychannel.command(name='edit', help='Edit an existing Category.')
    @commands.has_permissions(manage_channels=True)
    async def _categoryedit(self, ctx, category:discord.CategoryChannel, name, position:int=None, nsfw:bool=None, reason=None):
        await category.edit(name=name, position=position, nsfw=nsfw, reason=reason)
        await ctx.send(f'Category {category.name} has been updated.')

    @_categorychannel.command(name='delete', help='Deletes an existing Category.')
    @commands.has_permissions(manage_channels=True)
    async def _categorydel(self, ctx, category:discord.CategoryChannel, reason=None):
        await category.delete(reason=reason)
        await ctx.send(f'Category {category.name} has been deleted.')

    #-----------------------------------------
    #--A command group within a command group to
    #--let users decide what type of channel
    #--to add to the category.

    @_categorychannel.group(name='createchannel', help='Creates a Text or Voice Channel in a Category.', aliases=['createnew','add'])
    async def _categoryadd(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_categoryadd.command(name='textchannel', help='Creates a Text Channel in a Category.', aliases=['text','tc'])
    async def _categoryaddtext(self, ctx, category:discord.CategoryChannel, name='text-channel', topic=None, slowmode_delay=None, position:int=None, nsfw:bool=None, *, reason=None):
        #Check if the Text Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the length of the topic less than 1024 characters long?
        # - Is the slowmode delay valid and less than 6 hours?

        if 1 < len(name) < 100: #This is the maximum limit for Text Channel names.
            if topic is not None:
                if len(topic) > 1024: #This is the maximum limit for Text Channel topics.
                    await ctx.send("Please choose a channel topic that is 1024 or less characters in length.")

            if slowmode_delay is not None:
                if slowmode_delay < 0 or slowmode_delay > 21600: #This is the range that 'slowmode_delay' must be in.
                    await ctx.send("Please choose a delay between 0 and 21600 seconds.")

            c = await category.create_text_channel(name=name, position=position, slowmode_delay=slowmode_delay, nsfw=nsfw, topic=topic, reason=reason)
            await ctx.send(f"Text Channel {c.mention} has been created in Category `{category.name}`!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    @_categoryadd.command(name='voicechannel', help='Creates a Voice Channel in a Category.', aliases=['voice','vc'])
    async def _categoryaddvoice(self, ctx, category:discord.CategoryChannel, name='Voice Channel', user_limit:int=None, bitrate:int=None, *, reason=None):
        #Check if the Voice Channel requested is valid and can be created;
        # - Is there a name more than 1 and less than 100 characters long?
        # - Is the user limit valid? (TBA)
        # - Is the bitrate valid? (TBA)

        if 1 < len(name) < 100:
            c = await ctx.guild.create_voice_channel(name=name, position=position, user_limit=user_limit, bitrate=bitrate, reason=reason)
            await ctx.send(f"The voice channel {c.name} has been created in Category `{category.name}`!")
        else:
            await ctx.send("Please choose a name between 1 and 100 characters in length.")

    #-----------------------------------------
    #---------------------------------------------------------------------------------
    #---A command group to create, get information about and delete Invites.
    #---'Invite' refers to a 'discord.gg/x' link where x is a hash that refers
    #---to a specific guild and channel that can be defined.
            
    @commands.group(name='invite', help='Interact with or create new instant invites.')
    async def _invite(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_invite.command(name='create', help='Create an instant invite.')
    @commands.has_permissions(create_instant_invite=True)
    async def _invitecreate(self, ctx, channel, max_age:int=0, max_uses:int=0, temporary_membership:bool=False, unique_invite:bool=True, *, reason=None):
        try:
            t_converter = commands.TextChannelConverter()
            final = await t_converter.convert(ctx, channel)
            type = 't'
        except:
            try:
                v_converter = commands.VoiceChannelConverter()
                final = await v_converter.convert(ctx, channel)
                type = 'v'
            except:
                raise commands.CommandError("Invalid Channel entered.")

        invite = await final.create_invite(max_age=max_age, max_uses=max_uses, temporary=temporary_membership, unique=unique_invite, reason=reason)
        if type == 't':
            await ctx.send(f"Your invite to {final.mention} has been generated: {str(invite)}")
        else:
            await ctx.send(f"Your invite to the Voice Channel {final.name} has been generated: {str(invite)}")

    @_invite.command(name='info', help='Displays information about an Invite.')
    async def _inviteinfo(self, ctx, invite):
        invite = await self.bot.fetch_invite(invite)

        embed = discord.Embed() #Create an Embed
        embed.set_author(name='Invite Info')
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='Code (ID)', value=invite.id)
        embed.add_field(name='Channel', value=invite.channel.mention)
        embed.add_field(name='Inviter', value=invite.inviter.mention)

        #embed.add_field(name='Created at', value=f'{dotw[invite.created_at.weekday()-1]}, {invite.created_at.day} {moty[invite.created_at.month-1]} {invite.created_at.year}')

        embed.add_field(name='Uses', value=str(invite.uses))
        embed.add_field(name='Maximum Uses', value=str(invite.max_uses))
        embed.add_field(name='Temporary', value=invite.temporary)

        embed.add_field(name='Revoked', value=invite.revoked)

        if invite.max_age == 0:
            max_age = 'Never expires'
        else:
            max_age = str(invite.max_age)

        embed.add_field(name='Maximum Age', value=max_age)

        embed.add_field(name='URL', value=invite.url, inline=False)
        embed.add_field(name='Approximate Member Count', value=invite.approximate_member_count, inline=False)
        embed.add_field(name='Approximate Online Count', value=invite.approximate_presence_count, inline=False)

        await ctx.send(embed=embed)

    @_invite.command(name='delete', help='Deletes an Invite.')
    @commands.has_permissions(manage_channels=True)
    async def _invitedel(self, ctx, invite, *, reason=None):
        invite = await self.bot.fetch_invite(invite)
        await invite.delete(reason=reason)
        await ctx.send("Invite deleted.")

    #---------------------------------------------------------------------------------
    #---A command group to create, get information about and delete Widgets.
    #---'Widget' refers to a Guild widget.

    @commands.group(name='widget', help='Interact with your Guild\'s Widget.')
    async def _widget(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_widget.command(name='info', help='Gets information about the Guild from a Widget.')
    async def _widgetinfo(self, ctx):
        try:
            widget = self.bot.fetch_widget(ctx.guild.id)

            embed = discord.Embed() #Create an Embed
            embed.set_author(name='Widget')
            embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

            channels = await Base.convert_long_list(widget.channels, 70, 1000)
            #members = await Base.convert_long_list(widget.members, 40, 1000)

            embed.add_field(name='Guild ID', value=str(widget.id))
            embed.add_field(name='Guild Name', value=widget.name)
            embed.add_field(name='Accessible Voice Channels', value=channels)

            embed.add_field(name='Widget JSON URL', value=widget.json_url)
            embed.add_field(name='Guild Invite URL', value=widget.invite_url)
            embed.add_field(name='Created at', value=f'{dotw[widget.created_at.weekday()-1]}, {widget.created_at.day} {moty[widget.created_at.month-1]} {widget.created_at.year}')

            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            raise commands.CommandError(f'{ctx.author.mention}: The widget for this guild is disabled.')

    @_widget.command(name='members', help='Displays the online members in the server.')
        try:
            widget = self.bot.fetch_widget(ctx.guild.id)

            embed = discord.Embed() #Create an Embed
            embed.set_author(name='Widget: Online Members')

            members = await Base.convert_long_list(widget.members, 40, 1000)
            embed.add_field(name='Members', value=members)

            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            raise commands.CommandError(f'{ctx.author.mention}: The widget for this guild is disabled.')
        
    
def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Setup(bot))
