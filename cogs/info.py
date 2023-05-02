import discord
from discord.ext import commands
from discord.ext.commands import MemberConverter

from base import Base

class Info(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #---------------------------------------------------------------------------------

    @commands.command(
        name='memberinfo',
        description='Returns some basic information about a member in this guild.',
        aliases=['userinfo','whois']
    )

    # Member mention: <@id>
    # Role mention: <@&id>
    # Channel mention: <#id>
    async def member_info(self, ctx: commands.Context, target):
        roles = None
        perms = None
        user_flags = None
        additional_info = None

        member: discord.Member = await Base.m_converter.convert(ctx: commands.Context, target)

        for x in range(0, len(member.roles)):
            if roles is None or len(roles) < 500:
                current_role = member.roles[len(member.roles)-(x+1)]
                if current_role != ctx.guild.default_role:
                    if len(current_role.name) >= 30:
                        if roles is not None:
                            roles += f', {current_role.name[:30]}...'
                        else:
                            roles = f'{current_role.name[:30]}...'
                    else:
                        if roles is not None:
                            roles += f', {current_role.mention}'
                        else:
                            roles = current_role.mention
            elif len(roles) >= 500:
                print(roles)
                roles += ' ...'
                break

        perm_dict = iter(member.guild_permissions)
        while True:
            try:
                perm = next(perm_dict)
                if perm[0] == 'administrator' and perm[1] == True:
                    perms = 'administrator [...]'
                    break
                elif perm[1] == True:
                    if perms is not None:
                        perms += f', {perm[0]}'
                    else:
                        perms = perm[0]

            except StopIteration:
                break

        user_flags_list = member.public_flags.all()
        for user_flag in user_flags_list:
            user_flag = str(user_flag)[10:] # Remove "Userflags."
            if (user_flags is None):
                user_flags = user_flag
            else:
                user_flags += f", {user_flag}"

        if ctx.guild.owner_id == member.id:
            additional_info = 'Guild Owner'

        formatted_perms = perms.title().replace("_", " ") if perms is not None else None
        formatted_public_user_flags = user_flags.title().replace("_", " ") if user_flags is not None else None

        embed: discord.Embed = discord.Embed(color=0x00ff00)
        embed.set_author(name=member.name, icon_url=member.default_avatar)
        embed.set_footer(text=f"Requested by {ctx.author.name}{ctx.author.discriminator}", icon_url=ctx.author.avatar)
        embed.set_thumbnail(url=member.avatar)

        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Account created", value=f"{Base.dotw[member.created_at.weekday()]}, {member.created_at.day} {Base.moty[member.created_at.month-1]} {member.created_at.year}", inline=True)
        embed.add_field(name="Bot", value=member.bot, inline=True)
        
        if member == member.guild.me:
            embed.add_field(name="Absolute Unit", value="Yes", inline=False)
        
        embed.add_field(name="Joined guild", value=f"{Base.dotw[member.joined_at.weekday()]}, {member.joined_at.day} {Base.moty[member.joined_at.month-1]} {member.joined_at.year}", inline=True)
        embed.add_field(name=f"Roles [{len(member.roles)-1}]", value=roles, inline=False)
        embed.add_field(name="Permissions", value=formatted_perms, inline=False)

        embed.add_field(name="Public User Flags", value=formatted_public_user_flags, inline=False)

        if additional_info is not None:
            embed.add_field(name="Additional Info", value=additional_info, inline=False)
        
        await ctx.send(embed=embed)

    #---------------------------------------------------------------------------------

    @commands.command(
        name='guildinfo',
        description='Returns some basic info about this guild.',
        aliases=['serverinfo']
    )

    async def guildinfo_command(self, ctx):
        guild: discord.Guild = ctx.guild

        embed = discord.Embed(color=0x00ff00)
        embed.set_author(name=guild.name, icon_url=guild.icon)
        embed.set_footer(text=f"Requested by {ctx.author.name}{ctx.author.discriminator}", icon_url=ctx.author.avatar)
        embed.description = "This command only shows the channels I can see."
        thumb = guild.banner if guild.banner is not None else guild.icon
        embed.set_thumbnail(url=thumb)

        embed.add_field(name="Owner", value=guild.owner)
        embed.add_field(name="Members", value=str(len(guild.members)))
        embed.add_field(name="Created at", value=f"{Base.dotw[guild.created_at.weekday()]}, {guild.created_at.day} {Base.moty[guild.created_at.month-1]} {guild.created_at.year}", inline=True)

        embed.add_field(name="Categories", value=str(len(guild.categories)))
        embed.add_field(name="Text Channels", value=str(len(guild.text_channels)))
        embed.add_field(name="Voice Channels", value=str(len((guild.voice_channels))))

        embed.add_field(name="Threads", value=str(len(guild.threads)))
        embed.add_field(name="Nitro Boosters", value=str(guild.premium_subscription_count))
        embed.add_field(name="Premium Tier", value=str(guild.premium_tier))
        await ctx.send(embed=embed)

    @commands.command(
        name='advancedguildinfo',
        help='''Gives you a large amount of available information about this guild.
        Note: it is recommended to use this in a private channel to prevent any unwanted information being seen by normal users.''',
        aliases=['agi','asi']
    )

    async def advanced_guild_info(self, ctx):

        #This variable (ctx.guild) is used a lot, so this helps simplify the code below
        g: discord.Guild = ctx.guild

        #Variable definitions
        roles = ''
        categories = ''
        features = ''
        forums = ''

        premium_subscriber_role = "None"\
        if g.premium_subscriber_role is None\
        else g.premium_subscriber_role.mention

        rules_channel = "None"\
        if g.rules_channel is None\
        else g.rules_channel.mention

        public_updates_channel = "None"\
        if g.public_updates_channel is None\
        else g.public_updates_channel.mention

        system_channel = "None"\
        if g.system_channel is None\
        else g.system_channel.mention

        roles = Base.convert_long_list([role.mention for role in g.roles], 30, 250, g.default_role)
        categories = Base.convert_long_list([category.name for category in g.categories], 30, 250)
        emojis = Base.convert_long_list([f"<:{emoji.name}:{emoji.id}>" for emoji in g.emojis], 10000, 250)
        features = Base.convert_long_list([feature.name for feature in g.features], 30, 250)
        forums = Base.convert_long_list([forum.name for forum in g.forums], 30, 250)

#Create an embedded message with guild information in it with the colour theme R:0, G:255, B:0:
        embed = discord.Embed(color=0x00ff00) #R:0, G:255, B:0
        embed.set_author(name=ctx.author.name, icon_url=g.icon.url) #The author and the Guild's icon
        embed.set_footer(text=f"Guild ID: {g.id} | Guild Owner: {g.owner} | Guild Owner ID: {g.owner_id} | Shard ID: {g.shard_id} | Chunked: {g.chunked}", icon_url=f"{ctx.author.avatar}")

#Syntax: Embed.add_field(name[str], value[str], inline[bool])
        embed.add_field(name=f"Channels [{len(g.channels)}]", value=f"Text: {len(g.text_channels)}, Voice: {len(g.voice_channels)}")
        embed.add_field(name=f"Threads", value=str(len(g.threads)))
        embed.add_field(name=f"Members", value=f"{g.member_count}/{g.max_members}")

        embed.add_field(name=f"AFK timer: {g.afk_timeout/60}m", value=f"Channel: {g.afk_channel}")
        embed.add_field(name="Default Notifications", value=f"{str(g.default_notifications[0]).title()}")
        embed.add_field(name="Default Role", value=g.default_role.mention)
        
        embed.add_field(name="2FA Level", value=str(g.mfa_level))
        embed.add_field(name="Verification Level", value=f"{str(g.verification_level).title()}")
        embed.add_field(name="Explicit Content Filter", value=f"{str(g.explicit_content_filter).title()}")
        
        embed.add_field(name="Large (>250 members)", value=str(g.large))
        embed.add_field(name="Preferred Locale", value=str(g.preferred_locale))
        embed.add_field(name="Unavailable", value=str(g.unavailable))

        embed.add_field(name=f"Premium Tier [{str(g.premium_tier)}]", value=f"Booster Count: [{str(len(g.premium_subscribers))}]")
        embed.add_field(name="Premium Progress Bar Enabled", value=str(g.premium_progress_bar_enabled))
        embed.add_field(name="Premium Subscriber Role", value=premium_subscriber_role)

        embed.add_field(name="Stickers", value=f"{str(len(g.stickers))}/{str(g.sticker_limit)}")
        embed.add_field(name="Scheduled Events", value=str(len(g.scheduled_events)))
        embed.add_field(name="Vanity URL Code", value=g.vanity_url_code)

        embed.add_field(name="Stage Channels", value=str(len(g.stage_channels)))
        embed.add_field(name="Stage Instances", value=str(len(g.stage_instances)))
        embed.add_field(name="Widget Enabled", value=str(g.widget_enabled))

        embed.add_field(name="Rules Channel", value=rules_channel)
        embed.add_field(name="Public Updates Channel", value=public_updates_channel)
        embed.add_field(name="System Channel", value=system_channel)

        embed.add_field(name="Description", value=g.description, inline=False)
        embed.add_field(name=f"Roles [{len(g.roles)}]",
        value=roles, inline=False)
        embed.add_field(name=f"Categories [{len(g.categories)}]",
        value=categories, inline=False)
        embed.add_field(name=f"Emojis [{len(g.emojis)}/{g.emoji_limit}]",
        value=emojis, inline=False)
        embed.add_field(name=f"Features [{len(g.features)}]",
        value=features, inline=False)
        embed.add_field(name=f"Forums [{len(g.forums)}]",
        value=forums, inline=False)

        embed.add_field(name="Created at",
        value=f"{Base.dotw[g.created_at.weekday()]}, {g.created_at.day} {Base.moty[g.created_at.month-1]} {g.created_at.year} at {g.created_at.hour}:{g.created_at.minute}",
        inline=False)
        embed.add_field(name="Extra Info",
        value=f"System Channel: {g.system_channel.mention}, Large Guild: {g.large}, Unavailable: {g.unavailable}",
        inline=False)
        embed.add_field(name="Other Limits",
        value=f"\
        Presences Limit: {g.max_presences},\
        Files: {g.filesize_limit/1000000}MB,\
        Bitrate: {g.bitrate_limit/1000}kbps,\
        Video Channel Users: {str(g.max_video_channel_users)}",
        inline=False)
        embed.add_field(name="Premium Features",
        value=features.title(),
        inline=False)
#send the embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Info(bot))