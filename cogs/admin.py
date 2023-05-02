import discord
import json

from discord.ext import commands

from base import Base

#https://stackoverflow.com/questions/9847213/how-do-i-get-the-day-of-week-given-a-date-in-python
#Get the day of the week from a date

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="rename")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def _rename(self, ctx: commands.Context, member: discord.Member, *, nickname: str=None):
        """Removes or changes a user\'s nickname"""
        #This command will by default remove a member's nickname, however if the 'nickname'
        #perameter is provided, the member will be given that nickname.
        if member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if member.id != ctx.guild.owner_id: #Nobody can rename the owner
                await member.edit(nick=nickname)
            else:
                await ctx.send(f'{ctx.author.mention}, you can\'t rename the owner.')
        else:
            await ctx.send(f"{ctx.author.mention}, you cannot rename a user with an equal or higher top rank to you.")

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="kick")
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx: commands.Context, member: discord.Member, *, reason=None):
        """Kicks a user from the server. They can join back with an invite."""
        #This command will by default kick a member with no reason, however if the 'reason'
        #parameter is provided, then in the log for the member's kick this reason will be provided.

        if member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id:
            if member.id != ctx.guild.owner_id: #Nobody can kick the owner, so this shouldn't be an option.
                #We don't want the author to be able to kick someone lower than themselves in the role hierarchy,
                #however if they are the owner of the server they are able to bypass this rule.
                await ctx.guild.kick(user=member, reason=reason)
                await ctx.send(f'{member} was kicked for {reason}.\nID: `{member.id}`')
            else:
                await ctx.send(f'{ctx.author.mention}, you don\'t have permissions to kick this member.')

        elif member.id == ctx.author.id or member.id == self.bot.user.id:
            #We don't want members to be able to kick themselves as this may cause issues
            await ctx.send(f'{ctx.author.mention}, I can\'t bring myself to do that.')

        else:
            #If the author is not trying to kick themself and they do not have sufficient permissions to kick the member
            await ctx.send(f'{ctx.author.mention}, you are unable to kick someone with an equal or higher top rank to you.')

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="ban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _ban(self, ctx: commands.Context, user: discord.User, delete_message_days: int=1, *, reason=None):
        """Bans a user. They cannot join back until you unban them."""
        content = ''
        success = False

        if delete_message_days > 7:
            delete_message_days = 7
            #await ctx.send("Deleting 7 days of messages (this is the maximum)")

        if user not in [ban_entry.user async for ban_entry in ctx.guild.bans()]:
            #https://wiki.python.org/moin/Generators
            #This checks whether the user/member is in the list of banned members. Since every BanEntry is a tuple within the
            #guild.bans list, we need to use a 'generator' to check whether the user is in [a list of users for every BanEntry
            #in the ban entries list].

            if user in ctx.guild.members:
                member: discord.Member = ctx.guild.get_member(user.id)
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
                        await ctx.guild.ban(user=user, reason=reason, delete_message_days=delete_message_days)
                        success = True
                    else:
                        await ctx.send(f'{ctx.author.mention}, you can\'t ban the owner!')

                else:
                    #The member cannot ban this member as they are lower in the hierarchy
                    await ctx.send(f'{ctx.author.mention}, you are unable to ban someone with an equal or higher rank to you.')

            else:
                # Preban
                await ctx.guild.ban(user=user, reason=reason, delete_message_days=delete_message_days)
                success = True

            if success == True:
                content = f'`{user.name}` was banned.'
                if reason is not None:
                    content = content[:len(content)-1] + f' for `{reason}`.'
                content += f'\nThe past `{delete_message_days} days` of messages for this user were deleted.'
                content += f'\nUser ID: `{str(user.id)}`'
                await ctx.send(content)

        else:
            await ctx.send(f'{ctx.author.mention}, this user is already banned.')

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="multiban")
    @commands.guild_only()
    @commands.has_permissions(administrator=True) #We don't want members able to ban multiple people with just ban_members
    async def _mban(self, ctx: commands.Context, users: commands.Greedy[discord.User], delete_message_days=1, *, reason=None):
        """Bans multiple users at once (use with caution)."""
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

        for x in range(0, len(users)):
            if users[x] not in [ban_entry.user async for ban_entry in ctx.guild.bans()]: #Generator to check the user is not already banned
                if users[x] in ctx.guild.members:
                    member: discord.Member = ctx.guild.get_member(users[x].id)
                    if member.id == self.bot.user.id: #We don't want the bot to be able to ban itself
                        failed_bans += f'\n`{users[x]}: Don\'t make me ban myself!`'

                    elif member.id == ctx.author.id: #We don't want the author to be able to ban themself
                        failed_bans += f'\n`{users[x]}: You cannot ban yourself!`'

                    elif member.id == ctx.guild.owner_id: #Nobody can ban the owner, so this prevents related errors from occurring
                        failed_bans += f'\n`{users[x]}: You can\'t ban the owner of the guild!`'

                    elif member.top_role >= ctx.guild.get_member(self.bot.user.id).top_role:
                        failed_bans += f'\n`{users[x]}: I cannot ban this user.`'

                    elif member.top_role < ctx.author.top_role or ctx.author.id == ctx.guild.owner_id: #The ban was successful
                        successful_bans.append(users[x])

                    else: #The author does not have sufficient permissions to ban this user
                        failed_bans += f'\n`{users[x]}: You are unable to ban someone with an equal or higher rank to you.`'

                else:
                    #If the user is not a member and exists, the user is able to be banned.
                    await ctx.guild.ban(user=users[x], reason=reason, delete_message_days=delete_message_days)
                    successful_bans.append(users[x])

            else: #Otherwise, the member has already been banned.
                failed_bans += f'`{users[x]}: This user is already banned.`'


        if successful_bans != []: #If bans have already been successful, the 'content' variable needs to be set (for output).
            successful_ban_list = [member.name for member in successful_bans]
            content = f'`Passed: {len(successful_bans)}`\n`{str(successful_ban_list)}` will be banned.'

            if reason is not None: #Add the reason on to the end of the string if there is one
                content = content[:len(content)-1] + f' for `{reason}`.'

            content += f'\nThe past `{delete_message_days} days` of messages for these members will be deleted.'

            if str([member.id for member in successful_bans]) != []: #Generator to check if the User ID list is empty
                content += f'\nUser IDs: `{str([member.id for member in successful_bans])}`'

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
        else:
            for x in range(0,len(successful_bans)):
                await ctx.guild.ban(user=successful_bans[x], reason=reason, delete_message_days=delete_message_days)
            await ctx.send(str(len(successful_bans)) + ' users were successfully banned.')

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="unban")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _unban(self, ctx: commands.Context, user: discord.User, *, reason=None):
        """Unbans a user, allowing them to rejoin the server."""
        if user in [ban_entry.user async for ban_entry in ctx.guild.bans()]:
            await ctx.guild.unban(user=user, reason=reason)
            content = f'`{str(user)}` was unbanned.'
            if reason is not None:
                content = content[:len(content)-1] + f' for `{reason}`.'
            content += f'\nUser ID: `{str(user.id)}`'
            await ctx.send(content)

        else:
            await ctx.send(f'{ctx.author.mention}, this user is not currently banned.')

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="unbanall")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def _unban_all(self, ctx: commands.Context, *, reason=None):
        """Unbans every banned user (use with caution)."""
        banned_users = [ban_entry.user async for ban_entry in ctx.guild.bans()]

        await ctx.send(f"Banned users: `{str([banned_user.name for banned_user in banned_users])}`")

        def check(msg):
            #Returns a boolean as to whether the author is the same or not
            return msg.author == ctx.author

        if banned_users != []:
            content = f'**WARNING: This action is irreversible. Are you sure you want to unban these {len(banned_users)} users? **[Type in "`{ctx.guild.name}` yes" to confirm]'
            await ctx.send(content) #Sends the output
        else:
            await ctx.send("No users to unban!")
            return

        msg = await self.bot.wait_for('message', check=check)

        if msg.content != f'{ctx.guild.name} yes':
            #This could be an else statement beneath the ban if statement, and is completely inefficient and pointless, but
            #just in case, this is placed above the if statement to ensure no accidental multibans occur.
            await ctx.send("`Operation cancelled.`")
        else:
            for user in banned_users:
                await ctx.guild.unban(user=user, reason=reason)
            content = f"`{str([user.name for user in banned_users])}` were unbanned."
            if reason is not None:
                content = content[:len(content)-1] + f' for `{reason}`.'
            if len(banned_users) < 20:
                content += f'\nUser IDs: `{str([user.id for user in banned_users])}`'
            await ctx.send(content)

    #---------------------------------------------------------------------------------

    @commands.hybrid_command(name="bye")
    @commands.has_permissions(administrator=True)
    async def _bye(self, ctx):
        """Makes the bot leave the server (:()"""
        await ctx.send("Are you sure you want me to leave? [y/n]")

        def check(msg):
            return msg.author == ctx.author

        msg = await self.bot.wait_for('message', check=check)
        if (msg.content.lower() in ["yes", "y"]):
            await ctx.send("Bye mom!")
            await ctx.guild.leave()
        else:
            await ctx.send("`Operation cancelled.`")


async def setup(bot):
    await bot.add_cog(Admin(bot))
