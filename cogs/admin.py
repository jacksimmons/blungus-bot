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

async def setup(bot):
    await bot.add_cog(Admin(bot))
