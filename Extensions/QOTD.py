from discord import Embed, Colour
from random import choice
from asyncio import TimeoutError as AsyncioTimeout
from datetime import datetime


def format_qotd(question, thought, fact):
	return f"**__Question__**\n{question}\n\n**__Thought__**\n" \
			f"{thought}\n\n**__Fact__**\n{fact}"


class QOTDAdd:
	def __init__(self, client):
		self.client = client
		
		self.name = "addqotd"
		self.aliases = [
			"qotdadd",
			"qadd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Adds a QOTD to storage"
		self.usage = "qotdadd \"<question>\" \"<thought>\" \"<fact>\""
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs(
				"question"
			).send(message.channel)
		
		# Make a request to the API to parse quote wrapped args
		res = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if res == -1:
			# -1 indicates error connecting to API
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		args = res.get("Message", [])
		
		if len(args) < 1:
			# No question arg provided
			return await self.client.Errors.MissingArgs(
				"question"
			).send(
				message.channel
			)
		
		if len(args) < 2:
			# No thought arg provided
			return await self.client.Errors.MissingArgs(
				"thought"
			).send(
				message.channel
			)
		
		if len(args) < 3:
			# No fact arg provided
			return await self.client.Errors.MissingArgs(
				"fact"
			).send(
				message.channel
			)
		
		question, thought, fact, *_ = args
		
		# Unpack args into question, thought and fact, any extra args
		# being ignored

		# Insert into the db
		self.client.DataBaseManager.add_qotd(
			question,
			thought,
			fact,
			str(message.guild.id),
			str(message.author.id)
		)

		await message.channel.send(
			embed=Embed(
				type="rich",
				title="QOTD Added Successfully",
				description=(
					f"Preview:\n\n"
					f"{format_qotd(question, thought, fact)}"
				),
				colour=Colour.from_rgb(111, 255, 141)
			),
			delete_after=40.0
		)
	

class SendQOTD:
	def __init__(self, client):
		self.client = client
		
		self.name = "sendqotd"
		self.aliases = [
			"qotdsend",
			"qsend"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Sends a QOTD from storage"
		self.usage = "sendqotd"
		
	async def run(self, _, message, *__):
		# Retrieve all QOTD in the db for this guild
		all_qotd = self.client.DataBaseManager.get_qotd(
			str(message.guild.id)
		)
		
		if len(all_qotd) == 0:
			# This server didn't have any stored
			return await self.client.Errors.NoQOTD().send(
				message.channel
			)
		
		# Pick a (pseudo)random one
		qotd = choice(all_qotd)
		
		# Fetch the output channel from the db
		channel = self.client.DataBaseManager.get_qotd_channel(
			str(message.guild.id)
		)
		
		if not channel:
			# No channel found
			return await self.client.Errors.NoQOTDChannel().send(
				message.channel
			)
		
		# Resolve ID to a channel
		guild_channel = message.guild.get_channel(int(channel))
		
		if not guild_channel:
			# No channel found with that ID
			return await self.client.Errors.InvalidQOTDChannel().send(
				message.channel
			)
		
		# Attempt to fetch the role to mention from the db
		role_mention = self.client.DataBaseManager.get_qotd_role(
			message.guild.id
		)
		
		msg_text, r, mentionable = None, None, None
		
		if role_mention:
			# There was an entry in the db for which role to mention
			
			r = message.guild.get_role(int(role_mention))
			# Attempt to resolve that entry to a role
			
			if r:
				# The role was found
				
				# Store whether the role was mentionable before editing
				mentionable = r.mentionable
				
				await r.edit(
					mentionable=True
				)
				msg_text = f"<@&{r.id}>"
		
		# Attempt to fetch QOTD author using their ID
		user = await self.client.fetch_user(int(qotd["author"]))
		
		await guild_channel.send(
			content=msg_text,
			embed=Embed(
				type="rich",
				title="QOTD",
				description=format_qotd(
					qotd["question"],
					qotd["thought"],
					qotd["fact"]
				),
				colour=Colour.from_rgb(180, 111, 255)
			).set_footer(
				text=str(user),
				icon_url=str(user.avatar_url)
			)
			
		)
		
		if msg_text:
			# Restore the role to its previous mentionable state
			await r.edit(
				mentionable=mentionable
			)

		# Send success receipt to the message channel
		await message.channel.send(
			embed=Embed(
				type="rich",
				title="QOTD Sent Successfully",
				description="Channel: <#{}>".format(str(channel)),
				colour=Colour.from_rgb(111, 255, 141)
			).set_footer(
				text=str(user),
				icon_url=str(user.avatar_url)
			),
			delete_after=40.0
		)

		# Now it has been sent, delete it from the db
		self.client.DataBaseManager.remove_qotd(qotd["id"])

		# Get a channel to send the date to
		response_channel = self.get_response_channel(message.guild)
		
		if not response_channel:
			# Channel not found
			return
		
		await response_channel.send(f"```{self.format_date()}```")
		
	@staticmethod
	def get_response_channel(guild):
		# Returns a channel called qotd-response if it exists
		for c in guild.channels:
			if c.name == "qotd-response":
				return c
		
	@staticmethod
	def format_date():
		# Returns the current date as a formatted string
		date = datetime.now()
		
		start = date.strftime("%A, %B ")
		
		day = date.strftime("%d")
		# Zero padded two digit date
		
		year = date.strftime(" %Y")
		
		exceptions = {
			"01": "st",
			"02": "nd",
			"03": "rd",
			"21": "st",
			"22": "nd",
			"23": "rd",
			"31": "st"
		}
		
		if day in exceptions.keys():
			return start + day + exceptions[day] + year
		
		return start + day + "th" + year


class SetQOTDChannel:
	def __init__(self, client):
		self.client = client
		
		self.name = "setqotdchannel"
		self.aliases = [
			"qotdch",
			"setqotdch"
		]
		
		self.category = "QOTD"
		self.perm_level = 4
		self.description = \
			"Sets the channel the QOTD message will be sent to"
		self.usage = "setqotdchannel <channel>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args provided
			return await self.client.Errors.MissingArgs("channel").send(
				message.channel
			)
		
		channel_resolvable = "-".join(args)
		
		# Search for channel using the channel resolvable
		channel = self.get_channel(message.guild, channel_resolvable)
	
		if not channel:
			# Channel not found
			return await self.client.Errors.InvalidArgs(
				channel_resolvable,
				"channel"
			).send(message.channel)
		
		# Update in db
		self.client.DataBaseManager.set_qotd_channel(
			str(message.guild.id),
			str(channel.id)
		)
		
		# Send success receipt
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="Channel Updated!",
				description=f"QOTD will now be sent to <#{channel.id}>"
			)
		)
		
	@staticmethod
	def strip_channel(channel):
		# Return a channel id from a channel mention
		
		channel = channel.strip()
		if channel.startswith("<#"):
			channel = channel[2:]
		if channel.endswith(">"):
			channel = channel[:-1]
			
		return channel

	def get_channel(self, guild, channel_resolvable):
		# Attempts to resolve channel_resolvable to one of {guild}s
		# channels
		
		channel_id = self.strip_channel(channel_resolvable)
		
		for channel in guild.channels:
			if channel_resolvable == channel.name:
				return channel
			if str(channel.id) == channel_id:
				return channel
		return None


class SetQOTDRole:
	def __init__(self, client):
		self.client = client
		
		self.name = "setqotdrole"
		self.aliases = [
			"qotdr",
			"setqotdr"
		]
		
		self.category = "QOTD"
		self.perm_level = 4
		self.description = \
			"Sets the role which will be @mentioned when a QOTD is sent"
		self.usage = "setqotdrole <role>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args provided
			return await self.client.Errors.MissingArgs("role").send(
				message.channel
			)
			
		role_resolvable = " ".join(args)
		
		# Attempt to resolve role_resolvable
		role = self.get_role(message.guild, role_resolvable)
		
		if not role:
			# No role found
			return await self.client.Errors.InvalidArgs(
				role_resolvable, "role"
			)
		
		# Update db entry
		self.client.DataBaseManager.set_qotd_role(
			str(message.guild.id),
			str(role.id)
		)
		
		# Send success receipt
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="Role Updated!",
				description=(
					f"<@&{role.id}> will now be mentioned when a "
					f"QOTD is sent"
				)
			)
		)
		
	@staticmethod
	def get_role(guild, role_resolvable):
		for r in guild.roles:
			if role_resolvable in [str(r.id), r.name]:
				return r
			
		return None
	
	
class QOTDList:
	def __init__(self, client):
		self.client = client
		
		self.name = "qotdlist"
		self.aliases = [
			"qotdl",
			"lqotd",
			"listqotd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Lists all QOTD currently stored"
		self.usage = "qotdlist"
		
		# All the reactions that are needed for the menu
		self.accepted_reactions = {
			"➡": {
				"check": lambda page, length: page < length - 1
			},
			"⬅": {
				"check": lambda page, _: page > 0
			},
			"❌": {
				"check": lambda *_: True
			}
		}

	async def run(self, _, message, *__):
		# Retrieve all the QOTD for this guild
		all_qotd = self.client.DataBaseManager.get_all_qotd(
			str(message.guild.id)
		)
		
		if len(all_qotd) == 0:
			# This guild doesn't have any QOTD in storage
			return await self.client.Errors.NoQOTD().send(
				message.channel
			)
		
		formatted_qotd = []
		
		user_cache = {}
		# Builds a cache of users, limiting the amount of requests
		# made to discord API, minimising ratelimits
		
		for qotd in all_qotd:
			qotd_iter_user = int(qotd["author"])
			if qotd_iter_user not in user_cache.keys():
				# User not in the local cache (dict)
				fetched = await self.client.fetch_user(qotd_iter_user)
				
				# Update dict with new user
				user_cache[qotd_iter_user] = {
					"avatar": str(fetched.avatar_url),
					"tag": str(fetched)
				}
				
			# Insert QOTD into menu pages
			formatted_qotd.append(
				{
					"msg": format_qotd(
						qotd["question"],
						qotd["thought"],
						qotd["fact"]
					),
					"user": qotd["author"],
					"id": qotd["id"],
					"avatar": user_cache[qotd_iter_user]["avatar"],
					"tag": user_cache[qotd_iter_user]["tag"]
				}
			)
			
		# Message to hold the menu
		msg = await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="QOTD",
				description="Loading"
			)
		)
		
		# Set page and length variables accordingly, used to navigate
		# the menu
		page = 0
		total_len = len(all_qotd)
		
		# Start the menu at page 0
		await msg.edit(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="QOTD",
				description=formatted_qotd[page]["msg"],
			).set_footer(
				text=(
					f"{formatted_qotd[page]['tag']} | Page "
					f"{page + 1} of {len(formatted_qotd)}"
				),
				icon_url=formatted_qotd[page]["avatar"]
			).set_author(
				name=formatted_qotd[page]['id']
			)
		)
		
		while True:
			# Start menu loop
			try:
				for r in self.accepted_reactions.keys():
					# Check reactions on message
					
					# A lambda function indicating whether or not the
					# reaction should currently exist (bool)
					keep = self.accepted_reactions[r]["check"](
						page,
						total_len
					)

					# Find reaction object from message.reactions
					reacted = self.get(
						msg.reactions,
						r,
						lambda react: react.emoji
					)
					
					if keep and reacted and reacted.me:
						# The reaction should exist and the bot has
						# reacted
						continue
					
					if keep:
						# The reaction should exist and bot hasn't
						# reacted
						await msg.add_reaction(r)
						continue
						
					if (not keep) and reacted and reacted.me:
						# The reaction shouldn't exist but the bot
						# has reacted
						await msg.remove_reaction(r, message.guild.me)
				
				# Update message from cache
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				
				# Wait for next reaction_add event on this message
				reaction, user = await self.client.wait_for(
					"reaction_add",
					timeout=300,
					check=lambda react_check, u: (
						# The bot has the same reaction and the user is
						# correct and the menu message is being
						# reacted to
						react_check.me and u.id == message.author.id
						and react_check.message.id == msg.id
					)
				)
				
				if not reaction:
					# Somehow reaction is None
					return await msg.delete()
				
				# Remove the users reaction
				await reaction.remove(user)
				
				if reaction.emoji == "❌":
					# User reacted with X, end menu
					return await msg.delete()
				
				if reaction.emoji == "➡":
					# Increment page by 1
					page += 1
					
				else:
					# Decrement page by 1
					page -= 1
					
				if page < 0:
					# Page is somehow a negative value, default back
					# to 0
					page = 0
				
				if page == len(formatted_qotd):
					page = len(formatted_qotd) - 1
				
				# Update the menu with the (new) current page
				await msg.edit(
					embed=Embed(
						type="rich",
						colour=Colour.from_rgb(111, 255, 235),
						title="QOTD",
						description=formatted_qotd[page]["msg"],
					).set_footer(
						text=(
							f"{formatted_qotd[page]['tag']} | Page "
							f"{page + 1} of {len(formatted_qotd)}"
						),
						icon_url=formatted_qotd[page]["avatar"]
						).set_author(
						name=formatted_qotd[page]['id']
					)
				)
			
			except AsyncioTimeout:
				# Timeout waiting for reaction, delete menu
				return await msg.delete()
	
	@staticmethod
	def get(reactions, key, func=lambda n: n):
		# Utility function to search for key in reactions
		for i in reactions:
			if func(i) == key:
				return i


class RemoveQOTD:
	def __init__(self, client):
		self.client = client
		
		self.name = "qotdremove"
		self.aliases = [
			"qotdrm",
			"rmqotd",
			"removeqotd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Removes a QOTD from storage"
		self.usage = "qotdremove <id>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args were provided
			return await self.client.Errors.MissingArgs("QOTD ID").send(
				message.channel
			)

		# Check a QOTD of the given ID both exists and was made by
		# the current guild
		valid = self.client.DataBaseManager.qotd_exists(
			args[0],
			message.guild.id
		)

		if not valid:
			# Either doesn't exist or doesn't belong to this guild
			return await self.client.Errors.InvalidArgs("QOTD ID").send(
				message.channel
			)
		
		# Remove this QOTD
		self.client.DataBaseManager.remove_qotd(args[0])
		
		# Send a success receipt to the current channel
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				title="Success!",
				description="QOTD deleted successfully"
			)
		)
		

def setup(client):
	client.CommandHandler.add_commands(
		QOTDAdd(client),
		SendQOTD(client),
		SetQOTDChannel(client),
		SetQOTDRole(client),
		QOTDList(client),
		RemoveQOTD(client),
	)
