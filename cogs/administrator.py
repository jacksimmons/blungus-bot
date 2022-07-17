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

    #---------------------------------------------------------------------------------

    @commands.command(
        name='rename',
        help='Removes or changes a user\'s nickname',
        aliases=['nick']
    )

    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def _rename(self, ctx, member:discord.Member, *, nickname=None):
        #This command will by default remove a member's nickname, however if the 'nickname'
        #perameter is provided, the member will be given that nickname.

        if member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if member.id != ctx.guild.owner_id: #Nobody can rename the owner
                await member.edit(nick=nickname)
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

    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx, member:discord.Member, *, reason=None):

        ban_entries = await ctx.guild.bans()

        #This command will by default kick a member with no reason, however if the 'reason'
        #perameter is provided, then in the log for the member's kick this reason will be provided.

        #member = await self.m_converter.convert(ctx, member) #Converts the 'member' perameter into a Member object

        if member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if member.id != ctx.guild.owner_id: #Nobody can kick the owner, so this shouldn't be an option.
                #We don't want the author to be able to kick someone lower than themselves in the role hierarchy,
                #however if they are the owner of the server they are able to bypass this rule.
                await ctx.guild.kick(user=member, reason=reason)
                await ctx.send(f'{member} was kicked for {reason}.\nID: `{member.id}`')
            else:
                await ctx.send(f'{ctx.author.mention}, you don\'t have permissions to kick this member.')

        elif member.id == self.bot.user.id:
            #We don't want the bot to be able to kick itself as this may cause unwanted issues
            await ctx.send(f'I cannot kick myself! If you want me to leave, you can use `{self.bot.command_prefix}leave`.')

        elif member.id == ctx.author.id:
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

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx, member: discord.User, delete_message_days: int=1, *, reason=None):

        ban_entries = await ctx.guild.bans()

        content = ''
        s = False

        if delete_message_days > 7:
            delete_message_days = 7
            #await ctx.send("Deleting 7 days of messages (this is the maximum)")

        if member not in [BanEntry.user for BanEntry in ban_entries]:
            #https://wiki.python.org/moin/Generators
            #This checks whether the user/member is in the list of banned members. Since every BanEntry is a tuple within the
            #guild.bans list, we need to use a 'generator' to check whether the user is in [a list of users for every BanEntry
            #in the ban entries list].

            if member in ctx.guild.members:
                self.m = commands.MemberConverter
                member = self.m.convert(ctx, member)
                del self.m
                #If the user is a member of the guild, we need to ensure the author is a higher rank than the victim
                #to prevent abuse of the bot, however if the user is not a member of the guild, this is not an issue.

                if member.id == self.bot.user.id:
                    #We don't want the bot to be able to ban itself as this may cause issues
                    await ctx.send('Don\'t make me do that!')

                elif member.id == ctx.author.id:
                    #We don't want the author to be able to ban themselves as this may cause issues
                    await ctx.send(f'{ctx.author.mention}, you cannot ban yourself!')

                elif member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
                    if member.id != ctx.guild.owner_id: #Nobody can ban the owner, so this shouldn't be an option.
                        await ctx.guild.ban(user=member, reason=reason, delete_message_days=delete_message_days)
                        s = True
                    else:
                        await ctx.send(f'{ctx.author.mention}, you can\'t ban the owner!')

                else:
                    #The member cannot ban this member as they are lower in the hierarchy
                    await ctx.send(f'{ctx.author.mention}, you are unable to ban someone with an equal or higher rank to you.')

            else:
                await ctx.guild.ban(user=member, reason=reason, delete_message_days=delete_message_days)
                s = True

            if s == True:
                #The output for this command is more complex, so the variable 's' is used to determine when
                #the ban has been [s]uccessful and the output is then determined here.
                content = f'`{str(member)}` was banned.'
                if reason is not None:
                    content = content[:len(content)-1] + f' for `{reason}`.'
                content += f'\nThe past `{delete_message_days} days` of messages for this user were deleted.'
                content += f'\nUser ID: `{str(member.id)}`'
                await ctx.send(content)

        else:
            await ctx.send(f'{ctx.author.mention}, this user is already banned.')

    #---------------------------------------------------------------------------------

    @commands.command(
        name='multiban',
        help='Bans multiple users at once (use with caution)'
    )

    @commands.guild_only()
    @commands.has_permissions(administrator=True) #We don't want members able to ban multiple people with just ban_members
    async def _mban(self, ctx, users: commands.Greedy[discord.User], delete_message_days=1, *, reason=None):
        #This command uses commands.Greedy, which takes in arguments of a certain type until no more are given,
        #allowing multiple users to be passed into the command at once, so this command is able to ban multiple users at once.

        ban_entries = await ctx.guild.bans()

        failed_bans = ''
        successful_bans = []

        if delete_message_days < 0:
            delete_message_days = 0
            await ctx.send("`Delete message days` must be an integer between `0 and 7` inclusive, so it has been set to 0.")

        elif delete_message_days > 7:
            delete_message_days = 7
            await ctx.send("`Delete message days` must be an integer between `0 and 7` inclusive, so it has been set to 7.")
        for x in range(0,len(users)):

            if users[x] not in [BanEntry.user for BanEntry in ban_entries]: #Generator to check the user is not already banned

                if users[x] in ctx.guild.members:
                    users = await self.m_converter.convert(ctx, str(users[x]))

                    if users.id == self.bot.user.id: #We don't want the bot to be able to ban itself
                        failed_bans += f'\n`{users}: Don\'t make me ban myself!`'

                    elif users.id == ctx.author.id: #We don't want the author to be able to ban themself
                        failed_bans += f'\n`{users}: You cannot ban yourself!`'

                    elif users.id == ctx.guild.owner_id: #Nobody can ban the owner, so this prevents related errors from occurring
                        failed_bans += f'\n`{users}: You can\'t ban the owner of the guild!`'

                    elif users.top_role >= ctx.guild.get_member(self.bot.user.id).top_role:
                        failed_bans += f'\n`{users}: I cannot ban this user.`'

                    elif users.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id: #The ban was successful
                        successful_bans.append(users)

                    else: #The author does not have sufficient permissions to ban this user
                        failed_bans += f'\n`{users}: You are unable to ban someone with an equal or higher rank to you.`'

                else:
                    #If the user is not a member and exists, the user is able to be banned.
                    await ctx.guild.ban(user=users[x], reason=reason, delete_message_days=delete_message_days)
                    successful_bans.append(users[x])

            else: #Otherwise, the member has already been banned.
                failed_bans += f'`{users[x]}: This user is already banned.`'


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
            content += f'\n`Failed: {len(users) - len(successful_bans)}`{failed_bans}\n'

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

    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx, user: discord.User, *, reason=None):

        ban_entries = await ctx.guild.bans()

        if user in [BanEntry.user for BanEntry in ban_entries]:
            await ctx.guild.unban(user=user, reason=reason)
            content = f'`{str(user)}` was unbanned.'
            if reason is not None:
                content = content[:len(content)-1] + f' for `{reason}`.'
            content += f'\nUser ID: `{str(user.id)}`'
            await ctx.send(content)

        else:
            await ctx.send(f'{ctx.author.mention}, this user is not currently banned.')

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
    @commands.guild_only()
    async def _welcome(self, ctx):
        if ctx.invoked_subcommand is None:
            raise commands.BadArgument("Invalid subcommand passed.")

    @_welcome.command(name='set', help='Set the channel for which welcome messages will be displayed in.')
    async def setup_welcome_messages(self, ctx, channel:discord.TextChannel):
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
                data[str(id)]['channels']['welcome'] = channel.id #Same outcome whether 'welcome_channel' exists already or not

            else:
                data[str(id)] = {}
                data[str(id)]['channels'] = {}
                data[str(id)]['channels']['welcome'] = channel.id

            json.dump(data, file, indent=4)

            file.truncate() #Remove remaining part

        await ctx.send(f'Welcome channel **set** to {channel.mention}!')

    @_welcome.command(name='toggle', help='Toggles welcome messages in the current channel.')
    async def toggle_welcome_messages(self, ctx):

        output = ''
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

                if 'welcome' not in data[str(id)]['channels']: #Toggle ON
                    data[str(id)]['channels']['welcome'] = ctx.channel.id
                    output = f'Welcome messages have been toggled **ON** in {ctx.channel.mention}!'
                else: #Toggle OFF
                    data[str(id)]['channels'].pop('welcome') #Remove the welcome channel data from the dictionary
                    output = f'Welcome messages have been toggled **OFF.**'

            else: #Toggle ON
                data[str(id)] = {}
                data[str(id)]['channels'] = {}
                data[str(id)]['channels']['welcome'] = ctx.channel.id
                output = f'Welcome messages have been toggled **ON** in {ctx.channel.mention}!'

            json.dump(data, file, indent=4)

            file.truncate() #Remove remaining part

        await ctx.send(output)

    @_welcome.command(name='disable', help='Disables welcome messages.')
    async def disable_welcome_messages(self, ctx):

        with open('data/guilds.json', 'r+') as file:
            data = json.load(file)
            file.seek(0)

            data[str(ctx.guild.id)]['channels'].pop('welcome', None) #Removes nothing by default, so if there was no welcome data to begin with, nothing will be removed.

            json.dump(data, file, indent=4)

            file.truncate() #Removing remaining part

        await ctx.send('Welcome messages have been **disabled.**')

    #---------------------------------------------------------------------------------
    #A command group for creating and deleting tags, which work by the same principle
    #as dictionaries: they each have a key to identify them, and they each can store
    #a string value with which the bot will reply to the key identifier with.

    #Example scenario:

    #-> create tag, name = 'test', value = 'www.google.com'
    #-> use tag, name = 'test'
    #-> bot sends: 'www.google.com'

    #Note that the 'tag' command for using tags is in miscellaneous.py

    @commands.group(
        name='tags',
        help='List, create or delete tags in this guild.',
        invoke_without_command=True
    )

    @commands.guild_only()
    async def _tags(self, ctx):

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

    @_tags.command(name='create', aliases=['add','c'])
    async def _tagcreate(self, ctx, name, *, value):
        """Create a tag."""
        if len(name) <= 30:
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
                await ctx.send(f"Tag `{name}` created.")
            else:
                await ctx.send("Tag created.")

        else:
            raise commands.CommandError(f"{ctx.author.mention}, tag names can be a maximum of 30 characters long.")

    @_tags.command(name='delete', aliases=['remove','d'])
    async def _tagdelete(self, ctx, *, name):
        """Delete a tag."""

        with open('data/guilds.json', 'r+') as file:

            #Sources: [1] https://stackoverflow.com/questions/13265466/read-write-mode-python
            #         [2] https://stackoverflow.com/questions/21035762/python-read-json-file-and-modify
            #         [3] https://stackabuse.com/reading-and-writing-json-to-a-file-in-python/
            data = json.load(file)
            id = ctx.guild.id

            file.seek(0) # Reset file position to the beginning

            if str(id) in data:
                if 'tags' in data[str(id)]:
                    if name in data[str(id)]['tags']:
                        data[str(id)]['tags'].pop(name)
                    else:
                        raise commands.CommandError(f"Invalid tag name: Tag `{name}` doesn\'t exist.")
                else:
                    raise commands.CommandError("Invalid tag name: No tags have been created yet for this guild.")
            else:
                raise commands.CommandError("Invalid tag name: No data is currently being stored for this guild.")

            #Source: https://stackoverflow.com/questions/11277432/how-to-remove-a-key-from-a-python-dictionary

            json.dump(data, file, indent=4)
            file.truncate() #Remove remaining part

        await ctx.send(f"Tag `{name}` has been deleted.")

    #---------------------------------------------------------------------------------
    #Command group for creating, getting information about, editing and deleting 'Roles'
    #---Roles are named tags which can be added to Members to give them specific permissions,
    #---allow them to see private channels, change the colour of their Usernames, etc.

    @commands.group(name='role', help='Interact with or create new roles.', aliases=['r'])
    @commands.guild_only()
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

    @_role.command(name='info', help='Display some information about an existing Role.', aliases=['i'])
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
        embed.add_field(name='Members', value=str(len(role.members)))
        embed.add_field(name='Created at', value=f'{dotw[role.created_at.weekday()-1]}, {role.created_at.day} {moty[role.created_at.month-1]} {role.created_at.year}')

        embed.add_field(name='Hoisted', value=role.hoist)
        embed.add_field(name='Mentionable', value=role.mentionable)
        embed.add_field(name='Managed Externally', value=role.managed)

        embed.add_field(name='Position', value=role.position)
        embed.add_field(name='Colour [Hex]', value=role.colour)
        embed.add_field(name='Colour [RGB]', value=role.colour.to_rgb())

        embed.add_field(name='Permissions', value=formatted_perms)

        await ctx.send(embed=embed)

    @_role.command(name='colour', help='Sets the colour for a Role.', aliases=['color','col'])
    @commands.has_permissions(manage_roles=True)
    async def _rolecolour(self, ctx, role:discord.Role, colour:discord.Colour, *, reason=None):
        await role.edit(colour=colour)
        await ctx.send(f"✅ Role colour changed to {str(colour)}.")

    @_role.command(name='hoist', help='Hoists an existing Role.', aliases=['h'])
    @commands.has_permissions(manage_roles=True)
    async def _rolehoist(self, ctx, role:discord.Role, *, reason=None):
        if role.hoist:
            await role.edit(hoist=False)
            await ctx.send("✅ Role is now **no longer hoisted.**")
        else:
            await role.edit(hoist=True)
            await ctx.send("✅ Role is now **hoisted.**")

    @_role.command(name='mentionable', help='Toggles mentionable for a Role.', aliases=['m'])
    @commands.has_permissions(manage_roles=True)
    async def _rolementionable(self, ctx, role:discord.Role, *, reason=None):
        if role.mentionable:
            await role.edit(mentionable=False)
            await ctx.send("✅ Role is now **no longer mentionable.**")
        else:
            await role.edit(mentionable=True)
            await ctx.send("✅ Role is now **mentionable.**")

    @_role.command(
        name='move',
        help='''Changes the position of a Role in relation to other roles.
        Example: move "New Role" +1
        -> Moves role 1 position up in the role hierarchy, bringing it closer to the highest role
        Example 2: move "New Role" -2 Stupid Role
        -> Moves role 2 positions down in the role hierarchy, bringing it closer to the @ everyone role
        -> Displays "Stupid Role" in the Audit Log
        Example 3: move "New Role" 10
        -> Changes role\'s position to 10 in the hierarchy. This may move it higher or lower than its original position.''',
        usage='<role> <movement ({+/-integer [Movement]} or {integer [Edit Position]})> [reason]'
    )

    @commands.has_permissions(manage_roles=True)
    async def _rolemove(self, ctx, role:discord.Role, movement, *, reason=None):

        add = False
        subtract = False

        if role.position < ctx.author.top_role.position or ctx.author == ctx.guild.owner:
            if movement[0] == '+':
                add = True
                movement = movement[1:]
            elif movement[0] == '-':
                subtract = True
                movement = movement[1:]

            try:
                movement = int(movement)
                if add:
                    if role.position + movement < ctx.author.top_role.position or ctx.author == ctx.guild.owner:
                        await role.edit(position=role.position + movement)
                        await ctx.send(f"Role moved up `{movement}` positions in the role hierarchy.")
                    else:
                        raise commands.CommandError(ctx.author.mention + ", you cannot move a role to a position higher than your own top role.")

                elif subtract:
                    await role.edit(position=role.position - movement)
                    await ctx.send(f"Role moved down `{movement}` positions in the role hierarchy.")

                else:
                    if movement < ctx.author.top_role.position or ctx.author == ctx.guild.owner:
                        await role.edit(position=movement)
                        await ctx.send(f"Role's role hierachy position updated to `{role.position}`.")
                    else:
                        raise commands.CommandError(ctx.author.mention + ", you cannot change a role\'s position to higher than your own top role.")

            except ValueError:
                raise commands.CommandError(ctx.author.mention + ", `movement` syntax must be one of the following: '+[integer]', '-[integer]' or '[integer]'.")
        else:
            raise commands.CommandError(ctx.author.mention + ", you do not have sufficient permissions to edit this role.")

    @_role.command(name='rename', help='Rename an existing Role.', aliases=['r'])
    @commands.has_permissions(manage_roles=True)
    async def _rolerename(self, ctx, role:discord.Role, new_name, *, reason=None):
        await role.edit(name=new_name)
        if len(new_name) < 100:
            await ctx.send(f'✅ {new_name} has been renamed.')
        else:
            await ctx.send('✅ Role has been renamed.')

    @_role.command(name='edit', help='Edit an existing Role.', aliases=['e'])
    @commands.has_permissions(manage_roles=True)
    async def _roleedit(self, ctx, role:discord.Role, colour:discord.Colour=discord.Colour.default(), hoist:bool=False, mentionable:bool=False, position:int=None, *, reason=None):
        await role.edit(colour=colour, hoist=hoist, mentionable=mentionable, position=position, reason=reason)
        if len(role.name) < 100:
            await ctx.send(f'✅ {role.name} has been updated.')
        else:
            await ctx.send('✅ Role has been updated.')

    @_role.command(name='delete', help='Delete an existing Role.', aliases=['remove','del'])
    @commands.has_permissions(manage_roles=True)
    async def _roledel(self, ctx, role:discord.Role, *, reason=None):
        await role.delete(reason=reason)
        await ctx.send('✅ Role has been deleted.')

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

        embed.set_author(name=f'Text Channel Info', icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

        embed.add_field(name='Channel', value=target.mention, inline=False)

        embed.add_field(name='ID', value=target.id)
        embed.add_field(name='Category', value=target.category)
        embed.add_field(name='Category ID', value=target.category_id)

        embed.add_field(name='Topic', value=target.topic)
        embed.add_field(name='News Channel', value=target.is_news())
        embed.add_field(name='NSFW Channel', value=target.is_nsfw())

        embed.add_field(name='Created at', value=f'{dotw[target.created_at.weekday()-1]}, {target.created_at.day} {moty[target.created_at.month-1]} {target.created_at.year}')
        embed.add_field(name='Slowmode delay', value=target.slowmode_delay)
        embed.add_field(name='Position', value=target.position)

        #embed.add_field(name='Permissions synced', value=target.permissions_synced)

        changed_roles = await Base.convert_long_list(target.changed_roles, 50, 900)
        #Make the max total length slightly below the maximum embed value length which is 1024.

        if changed_roles == '':
            num_changed = 0
            changed_roles = None
        else:
            num_changed = target.changed_roles

        embed.add_field(name=f'Changed roles [{str(num_changed)}]', value=changed_roles, inline=False)

        last_message = target.last_message.content[:300]
        if len(target.last_message.content) >= 300:
            last_message += '[...]'

        embed.add_field(name='Last Message', value=last_message, inline=False)

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
        #embed.add_field(name='Permissions synced', value=target.permissions_synced)

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
        cloned_channel = await category_to_clone.clone(name=name, reason=reason)
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
            len_channels = 0

            widget = await self.bot.fetch_widget(ctx.guild.id)

            embed = discord.Embed() #Create an Embed
            embed.set_author(name='Widget')
            embed.set_footer(text=f'Requested by {str(ctx.author)}', icon_url=ctx.author.avatar_url)

            channels = await Base.convert_long_list(widget.channels, 70, 1000)
            num_channels = len(channels)

            if channels == '':
                channels = None
            else:
                len_channels = len(widget.channels)

            #members = await Base.convert_long_list(widget.members, 40, 1000)

            embed.add_field(name='Guild ID', value=str(widget.id))
            embed.add_field(name='Guild Name', value=widget.name)
            embed.add_field(name='Created at', value=f'{dotw[widget.created_at.weekday()-1]}, {widget.created_at.day} {moty[widget.created_at.month-1]} {widget.created_at.year}')

            embed.add_field(name=f'Accessible Voice Channels [{str(num_channels)}]', value=channels, inline=False)

            embed.add_field(name='Widget JSON URL', value=widget.json_url, inline=False)

            embed.add_field(name='Guild Invite URL', value=widget.invite_url, inline=False)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            raise commands.CommandError(f'{ctx.author.mention}: The widget for this guild is disabled.')

    @_widget.command(name='members', help='Displays the online members in the server.')
    async def _widgetmembers(self, ctx):
        try:
            len_members = 0

            widget = await self.bot.fetch_widget(ctx.guild.id)

            embed = discord.Embed() #Create an Embed
            embed.set_author(name='Widget: Online Members')

            members = await Base.convert_long_list(widget.members, 40, 1000)

            if members == '':
                members = None
            else:
                num_members = len(widget.members)

            embed.add_field(name=f'Members [{str(num_members)}]', value=members)

            await ctx.send(embed=embed)

        except discord.Forbidden:
            raise commands.CommandError(f'{ctx.author.mention}: The widget for this guild is disabled.')


def setup(bot):
    bot.add_cog(Admin(bot))
    bot.add_cog(Setup(bot))
