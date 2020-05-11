from re import compile as re_compile, error as re_error, match, escape
from discord import Embed, Colour
from asyncio import TimeoutError as AsyncioTimeoutError


class AddChannelFilter:
	
	# All accepted punishments
	punishments = [
		"ban",
		"softban",
		"kick",
		"strike",
		"delete"
	]

	def __init__(self, client):
		self.client = client
		
		self.name = "addchannelfilter"
		self.aliases = ["acf"]
		self.perm_level = 4
		self.description = "Adds a channel filter (Regular Expression)"
		self.description += "\nPunishments:" + ", ".join(
			[f"`{i}`" for i in self.punishments]
		)
		self.category = "Administration"
		self.usage = (
			"addchannelfilter \"<punishment>\" \"<filter>\" "
			"\"<channel>\" \"[reason]\""
		)
	
	@staticmethod
	def get_channel(guild, channel_resolvable):
		if match(r"^<#\d{17,19}>", channel_resolvable):
			# If the resolvable matches a channel mention, trim the
			# lead / tail non digit characters
			channel_resolvable = channel_resolvable[2:-1]
			
		if channel_resolvable.isdigit():
			# The channel_resolvable now contains only [0-9]
			
			# Cast to an int and see if any channel id matches
			ch = guild.get_channel(int(channel_resolvable))
			
			if ch:
				# If there was a match, return that
				return ch
		
		# Last resort: iter over every channel and check for name
		for c in guild.channels:
			if c.name.lower() == channel_resolvable.lower():
				# Names match, so return this channel
				return c
			
		# Nothing matched, forced to say channel doesn't exist,
		# return None
		return None
	
	async def run(self, _, message, *args):
		# Attempt to make a request to the API to parse quote wrapped
		# arguments
		args = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if args == -1:
			# Connecting to API failed
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		args = args.get("Message", [])
		
		if len(args) < 1:
			# No Args
			return await self.client.Errors.MissingArgs(
				"punishment"
			).send(message.channel)
		
		punishment = args[0].lower()
		
		if punishment not in self.punishments:
			# Punishments not an accepted punishment, reject
			return await self.client.Errors.InvalidArgs(
				punishment, "punishment"
			).send(message.channel)
		
		if len(args) < 2:
			# No Regular Expression supplied as a filter
			return await self.client.Errors.MissingArgs(
				"RegEx filter"
			)
		
		try:
			_ = re_compile(args[1])
		except re_error as e:
			# The supplied Regular Expression was invalid, (compiling
			# failed), send the error to the channel
			return await self.client.Errors.InvalidRegEx(
				e
			).send(message.channel)
		
		if len(args) < 3:
			# No channel supplied
			return await self.client.Errors.MissingArgs(
				"channel"
			).send(message.channel)
		
		channel = self.get_channel(message.guild, args[2])
		
		if not channel:
			# Unable to find channel from channel resolvable (args[2])
			return await self.client.Errors.InvalidArgs(
				args[2], "channel"
			).send(message.channel)
		
		reason = "[AUTOMOD FILTER]" if len(args) == 3 else args[3]
		# Reason, defaulting to "[AUTOMOD FILTER]" if no other reason
		# provided
		
		self.client.DataBaseManager.add_text_filter(
			punishment, args[1], channel.id, reason,
			str(message.guild.id)
		)
		# Insert the filter config into the db

		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Success!",
				colour=Colour.from_rgb(111, 255, 235)
			).add_field(
				name="Punishment",
				value=punishment,
				inline=True
			).add_field(
				name="RegEx Filter",
				value=escape(args[1]).replace(r"\ ", " "),
				inline=True
			).add_field(
				name="Channel",
				value=f"<#{channel.id}>",
				inline=True
			).add_field(
				name="Reason",
				value=reason,
				inline=True
			),
			delete_after=30.0
		)
		
		
class ListFilters:
	
	# For creating a menu to navigate the filters
	accepted_reactions = {
		"◀": {
			"check": lambda page, _: page != 0
		},
		"▶": {
			"check": lambda page, length: page < length - 1
		},
		"❌": {
			"check": lambda *_: True
		}
	}
	
	def __init__(self, client):
		self.client = client
		self.name = "listchannelfilters"
		self.aliases = ["lcf"]
		self.perm_level = 4
		self.description = "Lists all channel filters"
		self.category = "Administration"
		self.usage = "listchannelfilters [#channel]"

		self.left_arrow, self.right_arrow, self.cross = (
			self.accepted_reactions.keys()
		)
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			channel = ""
			
		else:
			# Use get_channel static method from the AddChannelFilter
			# class defined above, returns a channel from a channel
			# resolvable
			channel = AddChannelFilter.get_channel(
				message.guild,
				"-".join(args)
			)
			
			if not channel:
				# No channel found from the given resolvable, send an
				# error to the channel
				return await self.client.Errors.InvalidArgs(
					"-".join(args),
					"channel"
				)
			
			channel = channel.id
		
		# Retrieve all filters for the current guild and channel (if
		# specified)
		filters = self.client.DataBaseManager.get_filters(
			message.guild.id,
			channel
		)
		
		if not filters:
			# No filters found for the current guild / channel
			affected = f"<#{channel}>" if channel else \
				message.guild.name
			
			return await message.channel.send(
				embed=Embed(
					type="rich",
					title="No Filters",
					description=f"No filters are set in {affected}",
					colour=Colour.from_rgb(255, 70, 73)
				)
			)
	
		# Send the message which will hold the menu
		msg = await message.channel.send(
			embed=Embed(
				type="rich",
				description="Loading!",
				colour=Colour.from_rgb(111, 255, 235)
			)
		)
	
		# Init the page and length variables for use in the menu
		page, length = 0, len(filters)
		
		# Start the menu at page 0
		await msg.edit(
			embed=self.gen_embed(filters[page])
		)
		
		while True:
			# Start menu loop
			try:
				for reaction in self.accepted_reactions:
					# Iter over all reactions for the menu
					check = self.accepted_reactions[reaction]["check"]
					
					valid = check(page, length)
					
					reacted = self.get(
						msg.reactions,
						reaction,
						lambda re: str(re.emoji)
					)
					
					if reacted and reacted.me and valid:
						# The reaction exists, the bot's reaction is
						# included and the reaction should exist,
						# continue to next reaction
						continue
						
					if not (reacted and reacted.me) and valid:
						# The reaction should exist but either no-one
						# reacted with it or the bot hasn't
						await msg.add_reaction(reaction)
						# Add the reaction then continue to next
						# reaction
						continue
						
					if not valid and (reacted and reacted.me):
						# Reaction shouldn't exist but does, remove it
						await msg.remove_reaction(
							reaction, msg.guild.me
						)
				
				# Update message from cache
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				
				# Wait for the next reaction_add event on this message
				r, u = await self.client.wait_for(
					"reaction_add",
					check=lambda react, user: (
							str(react.emoji) in self.accepted_reactions
							and react.me and
							user.id == message.author.id and
							react.message.id == msg.id
						# The reaction is on the correct message,
						# the reacting user is the person who ran the
						# original command, the reaction is valid and
						# the bot also has that reaction (the
						# reaction should be on the menu at this point)
					)
				)
				
				if not (r and u) or (r and str(r.emoji) == self.cross):
					# Either r or u are None OR the reaction was
					# cross (to exit)
					return await msg.delete()
					# Delete the message
				
				# Remove the users reaction
				await msg.remove_reaction(r, u)
				
				# Increment the page if the reaction was a right arrow
				if str(r.emoji) == self.right_arrow:
					page += 1
				
				# Decrement the page if the reaction was a left arrow
				elif str(r.emoji) == self.left_arrow:
					page -= 1
				
				# If the page is somehow now less than 0, set it back
				# to 0
				if page < 0:
					page = 0
					
				# Page is outside of menu limits (greater than)
				# decrement
				while page >= length:
					page -= 1
				
				# Update menu with new info
				await msg.edit(
					embed=self.gen_embed(filters[page])
				)
				
			except AsyncioTimeoutError:
				# Waiting for the reaction timed out, delete the message
				return await msg.delete()
	
	@staticmethod
	def get(iterable, key, func=lambda n: n):
		for i in iterable:
			if func(i) == key:
				return i
		return None
	
	@staticmethod
	def gen_embed(f):
		# Returns an embed page for the menu, given the filter as f
		embed = Embed(
			type="rich",
			title=f["id"],
			colour=Colour.from_rgb(111, 255, 235)
		).add_field(
			name="Punishment",
			value=f["action"].title(),
			inline=True
		).add_field(
			name="Reason",
			value=f["reason"],
			inline=True
		).add_field(
			name="RegEx Filter",
			value=escape(f["filter"]).replace(
				r"\ ", " "
			),  # re.escape attempts to escape spaces, unescape so
			# the RegEx is presented correctly
			inline=True
		)
		
		if "channel" in f.keys():
			# Support for guild wide filters where the channel key
			# won't exist
			embed.add_field(
				name="Channel",
				value=f"<#{f['channel']}>"
			)

		return embed


class RemoveChannelFilter:
	def __init__(self, client):
		self.client = client
		self.name = "removechannelfilter"
		self.aliases = ["rmcf"]
		self.perm_level = 4
		self.description = "Removes a given channel filter"
		self.category = "Administration"
		self.usage = "removechannelfilter <id>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args provided to the command
			return await self.client.Errors.MissingArgs("id").send(
				message.channel
			)
		
		# Check the filter exists and belongs to the current guild
		valid = self.client.DataBaseManager.filter_exists(
			message.guild.id,
			args[0],
			"text"
		)
		
		if not valid:
			# Send an error message if the filter id isn't valid for
			# this guild
			return await self.client.Errors.InvalidArgs(
				args[0], "id"
			).send(
				message.channel
			)
		
		(
			self.client.DataBaseManager.get_table("filters")
			.get(args[0])
			.delete()
			.run(self.client.DataBaseManager.connection)
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Success!",
				description="Filter removed successfully.",
				colour=Colour.from_rgb(111, 255, 235)
			),
			delete_after=20.0
		)


def setup(client):
	client.CommandHandler.add_commands(
		AddChannelFilter(client),
		ListFilters(client),
		RemoveChannelFilter(client)
	)
