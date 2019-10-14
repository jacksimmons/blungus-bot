from base import Base

class Guild(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
					 '
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
        g = ctx.guild
        
        #Variable definitions
        roles = ''
        categories = ''
        features = ''
        
        self.update_info(ctx)
        
        #Uses a function in the Base module to convert the list (g.roles) into a string
        roles = Base.convert_long_list(g.roles, 30, 250, g.default_role)
        
        #Uses a function in the Base module to convert the list (g.categories) into a string
        categories = Base.convert_long_list(g.categories, 30, 250, g.categories[len(g.categories)-1])

        #The (g.features) list is much shorter, so it can be converted to a string right here:
        if g.features == []:
            features = "None"
        else:
            for x in range(0, len(g.features)):
                if features == '':
                    features = g.features[x]
                else:
                    features += f', {g.features[x]}'
                    
        #Create an embedded message with guild information in it with the colour theme R:0, G:255, B:0:
        embed = discord.Embed(color=0x00ff00) #R:0, G:255, B:0
        embed.set_author(info[name], icon_url=g.icon_url) #The name of the Guild and the Guild's icon
        embed.set_footer(text=f"Guild ID: {g.id} | Guild Owner: {g.owner} | Guild Owner ID: {g.owner_id} | Shard ID: {g.shard_id} | Chunked: {g.chunked}", icon_url=f"{ctx.author.avatar_url}")

        #Syntax: Embed.add_field(name[str], value[str], inline[bool])
        embed.add_field("Region", g.region) #1: name, value
        embed.add_field(f"Emoji [Limit: {g.emoji_limit}]", len(g.emojis)) #2: name, value
        embed.add_field(name=f"Channels [{len(g.channels)}]", value=f"Text: {len(g.text_channels)}, Voice: {len(g.voice_channels)}")
#4
        embed.add_field(name=f"Members [{len(g.members)}]", value=f"Human: number, Bot: number")
#5
        embed.add_field(name=f"Tier [Boosters: {len(g.premium_subscribers)}]", value=f"{g.premium_tier}")
#6
        embed.add_field(name="File Upload Limit", value=f"{g.filesize_limit/1000000}MB")
#7
        embed.add_field(name="Bitrate Limit", value=f"{g.bitrate_limit/1000} kbps")
#8
        embed.add_field(name=f"AFK Channel [AFK: {g.afk_timeout/60}m]", value=f"{g.afk_channel}")
#9
        embed.add_field(name="2FA Level", value=f"{g.mfa_level}")
#10
        embed.add_field(name="Default Notifications", value=f"{str(g.default_notifications[0]).title()}")
#11
        embed.add_field(name="Verification Level", value=f"{str(g.verification_level).title()}")
#12
        embed.add_field(name="Explicit Content Filter", value=f"{str(g.explicit_content_filter).title()}")
#13
        embed.add_field(name="Extra Info",
        value=f"System Channel: {g.system_channel.mention}, Large Guild: {g.large}, Unavailable: {g.unavailable}",
        inline=False)
#before preantepenultimate 21
        embed.add_field(name="Guild Limits",
        value=f"Presences Limit: {g.max_presences}, Member Limit: {g.max_members}",
        inline=False)
#preantepenultimate 22
        embed.add_field(name="Premium Guild Features",
        value=f"{features.title()}",
        inline=False)
#antepenultimate 23
        embed.add_field(name="Server created",
        value=f"{dotw[g.created_at.weekday()-1]}, {g.created_at.day} {moty[g.created_at.month-1]} {g.created_at.year} at {g.created_at.hour}:{g.created_at.minute}",
        inline=False)
#penultimate 24
        embed.add_field(name=f"Roles [{len(g.roles)}]",
        value=f"{roles}",
        inline=False)
#ultimate 25
        embed.add_field(name=f"Categories [{len(g.categories)}]",
        value=f"{categories}",
        inline=False)

        await ctx.send(embed=embed)
def setup(bot):
	bot.add_cog(Guild(bot))
