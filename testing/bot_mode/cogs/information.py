import discord
from discord.ext import commands
from base import Base

dotw = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] #Days of the week
moty = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] #Months of the year

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
	async def member_info(self, ctx, member: discord.Member):
		roles = None
		perms = None
		additional_info = None
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

		if ctx.guild.owner_id == member.id:
			additional_info = 'Guild Owner'

		formatted_perms = perms.title().replace("_", " ")

		embed = discord.Embed(color=0x00ff00)
		embed.set_author(name=member, icon_url=member.avatar_url)
		embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
		embed.set_thumbnail(url=member.avatar_url)

		embed.add_field(name="Name", value=member.name, inline=True)
		embed.add_field(name="ID", value=member.id, inline=True)

		embed.add_field(name="Account created", value=f"{dotw[member.created_at.weekday()]}, {member.created_at.day} {moty[member.created_at.month-1]} {member.created_at.year}", inline=True)
		embed.add_field(name="Joined guild", value=f"{dotw[member.joined_at.weekday()]}, {member.joined_at.day} {moty[member.joined_at.month-1]} {member.joined_at.year}", inline=True)

		embed.add_field(name="Bot", value=member.bot, inline=True)

		embed.add_field(name=f"Roles [{len(member.roles)-1}]", value=roles, inline=False)

		embed.add_field(name="Permissions", value=formatted_perms, inline=False)

		if additional_info is not None:
			embed.add_field(name="Additional Info", value=additional_info, inline=False)

		await ctx.send(embed=embed)

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
		embed.add_field(name="Owner", value=guild.owner)
#2
		embed.add_field(name="Region", value=guild.region)
#3
		embed.add_field(name="Categories", value=str(len(guild.categories)))
#4
		embed.add_field(name="Members", value=str(len(guild.members)))
#5
		embed.add_field(name="Channels", value=str(len(guild.channels)))
#6
		embed.add_field(name="Text Channels", value=str(len(guild.text_channels)))
#7
		embed.add_field(name="Voice Channels", value=str(len((guild.voice_channels)))
#8
		embed.add_field(name="File Upload Limit", value=f"{guild.filesize_limit/1000000}MB")
#9
		embed.add_field(name="Emoji Limit", value=str(guild.emoji_limit}) + " Emoji")
#10
		embed.add_field(name="Bitrate Limit", value=f"{guild.bitrate_limit/1000} kbps")
#11
		embed.add_field(name="Roles", value=str(len(guild.roles)))
#12
		embed.add_field(name="Nitro Boosters", value=str(guild.premium_subscription_count))
#13
		embed.add_field(name="Guild Premium Tier", value=str(guild.premium_tier))
#antepenultimate
		embed.add_field(
		name="Server created",
		value=f"{dotw[guild.created_at.weekday()]}, {guild.created_at.day} {moty[guild.created_at.month-1]} {guild.created_at.year} at {guild.created_at.hour}:{guild.created_at.minute}",
		inline=False)
#penultimate
		embed.add_field(name="Roles List", value=roles, inline=False)
#ultimate
		embed.add_field(name="Categories List", value=categories, inline=False)
#send the embed
		await ctx.send(embed=embed)

	@commands.command(
		name='advancedguildinfo',
		help='''Gives you a large amount of available information about this guild.
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
		embed.set_author(name=info[name], icon_url=g.icon_url) #The name of the Guild and the Guild's icon
		embed.set_footer(text=f"Guild ID: {g.id} | Guild Owner: {g.owner} | Guild Owner ID: {g.owner_id} | Shard ID: {g.shard_id} | Chunked: {g.chunked}", icon_url=f"{ctx.author.avatar_url}")

#Syntax: Embed.add_field(name[str], value[str], inline[bool])
		embed.add_field("Region", g.region)
		embed.add_field(f"Emoji [Limit: {g.emoji_limit}]", len(g.emojis))
		embed.add_field(name=f"Channels [{len(g.channels)}]", value=f"Text: {len(g.text_channels)}, Voice: {len(g.voice_channels)}")
		embed.add_field(name=f"Members [{len(g.members)}]", value=f"Human: number, Bot: number")
		embed.add_field(name=f"Tier [Boosters: {len(g.premium_subscribers)}]", value=f"{g.premium_tier}")
		embed.add_field(name="File Upload Limit", value=f"{g.filesize_limit/1000000}MB")
		embed.add_field(name="Bitrate Limit", value=f"{g.bitrate_limit/1000} kbps")
		embed.add_field(name=f"AFK Channel [AFK: {g.afk_timeout/60}m]", value=f"{g.afk_channel}")
		embed.add_field(name="2FA Level", value=str(g.mfa_level)")
		embed.add_field(name="Default Notifications", value=f"{str(g.default_notifications[0]).title()}")
		embed.add_field(name="Verification Level", value=f"{str(g.verification_level).title()}")
		embed.add_field(name="Explicit Content Filter", value=f"{str(g.explicit_content_filter).title()}")
		embed.add_field(name="Extra Info",
		value=f"System Channel: {g.system_channel.mention}, Large Guild: {g.large}, Unavailable: {g.unavailable}",
		inline=False)
#before preantepenultimate 21
		embed.add_field(name="Guild Limits",
		value=f"Presences Limit: {g.max_presences}, Member Limit: {g.max_members}",
		inline=False)
#preantepenultimate 22
		embed.add_field(name="Premium Guild Features",
		value=features.title(),
		inline=False)
#antepenultimate 23
		embed.add_field(name="Server created",
		value=f"{dotw[g.created_at.weekday()]}, {g.created_at.day} {moty[g.created_at.month-1]} {g.created_at.year} at {g.created_at.hour}:{g.created_at.minute}",
		inline=False)
#penultimate 24
		embed.add_field(name=f"Roles [{len(g.roles)}]",
		value=roles, inline=False)
#ultimate 25
		embed.add_field(name=f"Categories [{len(g.categories)}]",
		value=categories, inline=False)
#send the embed
		await ctx.send(embed=embed)

def setup(bot):
	bot.add_cog(Info(bot))
