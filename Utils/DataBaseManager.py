from rethinkdb import RethinkDB
from time import time as epoch


class DataBaseManager:
	def __init__(self, client):
		self.r = RethinkDB()
		self.connection = self.r.connect(
			port=28015,
			host="localhost"
		)
		# Initiate database connection
		
		self.client = client
		# Connection to discord
	
	def get_table(self, table):
		# Returns the request table as a Cursor object, creating if not
		# exists
		
		t_list = self.r.db("tfr").table_list().run(self.connection)
		# A list of all the table names
		
		if table in t_list:
			# Table exists, return that
			return self.r.db("tfr").table(table)
		
		# Create the table, it doesn't exist
		self.r.db("tfr").table_create(table).run(self.connection)
		
		# Return the newly created table
		return self.r.db("tfr").table(table)
	
	def get_prefix(self, guild):
		# Returns the prefix for the guild with given id
		if not isinstance(guild, str):
			# Ensure the guild (id) is a string
			guild = str(guild)
		
		guild_conf = list(
			self.get_table("guilds").filter(
				{
					"guild": guild
				}
			).run(self.connection)
		)
		# Return all objects in "guilds" table with matching guild id
		# Utilising __iter__ function to convert the result into a list
		
		if guild_conf:
			# An object matching the guild id was found
			guild_conf = guild_conf[0]
		# Select the first match
		
		if guild_conf and "prefix" in guild_conf.keys():
			# Object found and it contains a prefix, return that
			return guild_conf["prefix"]
		
		if not guild_conf:
			# Object not found, create an entry for this guild
			self.get_table("guilds").insert(
				{
					"guild": guild,
					"prefix": self.client.config.default_prefix
				}
			).run(self.connection)
		
		else:
			# Object found but doesn't contain a prefix, update it to
			# contain the default prefix
			self.get_table("guilds").get(guild).update(
				{
					"prefix": self.client.config.default_prefix
				}
			).run(self.connection)
		
		# Return default prefix
		return self.client.config.default_prefix
	
	def update_prefix(self, guild, new_prefix):
		# Updates prefix for guild with given id to new_prefix
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		(
			self.get_table("guilds")  # Connect to guilds table
			.filter(
				# Filter to return objects only matching guild (id)
				{
					"guild": guild
				}
			)
			.update(  # Update all matches to the new prefix
				{
					"prefix": new_prefix
				}
			)
			.run(self.connection)
		)
	
	def add_xp(self, guild, member, amount):
		# Adds {amount} xp to {member} in {guild}
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		if not isinstance(member, str):
			# Ensure member is a string
			member = str(member)
		
		table = self.get_table("xp")
		
		user_xp = list(
			table.filter(
				# Filter all entries in the "xp" table to return only
				# those with matching guild (id) and member (id) as
				# below
				{
					"guild": guild,
					"user": member
				}
			).run(self.connection)
		)
		# Utilise __iter__ function to convert the result into a list
		
		if user_xp:
			# Some match was found
			
			user_xp = user_xp[0]
			# Select first match only
			
			previous = user_xp["xp"]
			# The XP of the user before adding the new xp
			
			self.get_table("xp").get(user_xp["id"]).update(
				# Update user in the database, using the id of the
				# object returned to update only the correct user
				{
					"xp": previous + amount,  # Add XP
					"cooldown": (
						epoch() + self.client.config.xp_cooldown
					) * 1000  # Update cooldown
				}
			).run(self.connection)
			
			return previous + amount  # Return new XP total
		
		else:
			# No entry found in XP table matching user and guild,
			# create one
			table.insert(
				{
					"guild": guild,  # Add the guild id
					"user": member,  # Add the user id
					"xp": amount,  # Add the total xp
					"cooldown": (
						epoch() + self.client.config.xp_cooldown
					) * 1000  # Add the cooldown
				}
			).run(self.connection)
			
			return amount
	
	def xp_level(self, guild, member):
		# Returns the xp level (as an int) of the given member
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		if not isinstance(member, str):
			# Ensure member is a string
			member = str(member)
		
		level = 1
		# Start at level 1
		
		result = list(
			self.get_table("xp").filter(
				{
					"guild": guild,
					"user": member
				}
			).run(self.connection)
		)  # Attempt to find the users xp in the database
		
		if result:
			# If some user(s) were found, select the first only
			result = result[0]
		else:
			# If no database entry with their xp was found, return
			# the starting level (1)
			return level
		
		xp = result["xp"]
		
		# Logic adapted from Nadeko source levelling code for
		# consistency
		
		base_xp = 36
		total_xp = 0
		lvl = 1
		
		while True:
			required = (base_xp + base_xp / 4.0 * (lvl - 1))
			
			if required + total_xp > xp:
				break
			
			total_xp += required
			lvl += 1
		
		return lvl - 1
	
	def in_xp_cooldown(self, member, guild):
		# Returns whether or not the member is currently on cooldown
		# to earn more xp
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		if not isinstance(member, str):
			# Ensure member is a string
			member = str(member)
		
		# Attempt to find user in the database and then turn the
		# result into a python list
		result = list(
			self.get_table("xp").filter(
				{
					"guild": guild,
					"user": member
				}
			)
			.run(self.connection)
		)
		
		if not result:
			# User not found in db
			return False
		
		if "cooldown" not in result[0]:
			# Somehow not in their db entry, returning False will
			# cause them to gain xp, which will add a cooldown entry
			# if not one exists
			return False
		
		return result[0]["cooldown"] >= epoch() * 1000
	
	def get_xp(self, member, guild):
		# Returns the total xp for {member} in {guild} as an int
		
		xp_db = list(
			self.get_table("xp").filter(
				{
					# Filter all entries in the "xp" table to only
					# those which match the guild and member id
					"guild": guild,
					"member": member
				}
			).run(self.connection)
		)
		# Convert to a python list so its easy to select the first
		# result
		
		return {
			"xp": xp_db[0]["xp"] if xp_db else 0,
			# If a db entry exists, return the xp that contains,
			# if not, return 0
			"level": self.xp_level(
				xp_db[0]["xp"] if xp_db else 0, member
			)
			# Automatically generate the level using the same method
			# and return that also
		}
	
	def add_qotd(self, question, thought, fact, guild, author):
		# Adds the information for a QOTD to the database
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		if not isinstance(author, str):
			# Ensure author is a string
			author = str(author)
		
		(
			self.get_table("qotd")
			.insert(
				# Insert QOTD dictionary into "qotd" table
				{
					"question": question,
					"thought": thought,
					"fact": fact,
					"guild": guild,
					"author": author
				}
			).run(self.connection)
		)
	
	def get_qotd(self, guild):
		# Returns all qotd stored for the given guild
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		return list(
			self.get_table("qotd")
			.filter(
				{
					"guild": guild
				}
			)
			# Return all entries in "qotd" table matching the guild id
			.run(self.connection)
		)  # Convert to a list for ease of use
	
	def remove_qotd(self, qotd_id):
		# Removes the QOTD of given id from the database
		
		(
			self.get_table("qotd")
			.get(qotd_id)
			.delete()
			.run(self.connection)
		)
	
	def get_qotd_channel(self, guild):
		# Returns the id of the QOTD output channel for the given
		# guild, or None if not found
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
	
		config = list(
			self.get_table("guilds")
			.filter(
				{
					"guild": guild
				}
			)
			.run(self.connection)
		)
		
		if len(config) == 0:
			return None
		# Not really sure how this could happen,
		# A config entry should be created on the message event
		# before a command is ran if no prefix entry exists
		
		config = config[0]
		
		if "qotd_channel" in config.keys():
			return config["qotd_channel"]
		
		return None
	
	def set_qotd_channel(self, guild, channel):
		# Sets the QOTD output channel for the given guild
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
			
		if not isinstance(channel, str):
			# Ensure channel is a string
			channel = str(channel)
		
		(
			self.get_table("guilds")
			.filter(
				{
					"guild": str(guild)
				}
			)
			.update(
				{
					"qotd_channel": str(channel)
				}
			)
			.run(self.connection)
		)
	
	def set_qotd_role(self, guild, role):
		# Sets the role which will be mentioned when a QOTD is sent
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
			
		if not isinstance(role, str):
			# Ensure role is a string:
			role = str(role)
			
		(
			self.get_table("guilds")
			.filter(
				{
					"guild": str(guild)
				}
			)
			.update(
				{
					"qotd_role": str(role)
				}
			)
			.run(self.connection)
		)
	
	def get_qotd_role(self, guild):
		# Returns the role to be mentioned when a QOTD is sent,
		# should it exist else None
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
			
		config = list(
			self.get_table("guilds")
			.filter(
				{
					"guild": guild
				}
			)
			.run(self.connection)
		)
		
		if len(config) == 0:
			return None
		# Not really sure how this could happen,
		# A config entry should be created on the message event
		# before a command is ran if no prefix entry exists
		
		config = config[0]
		
		if "qotd_role" in config.keys():
			return config["qotd_role"]
		
		return None
	
	def get_all_qotd(self, guild):
		# Returns a list of all the QOTD for the guild in dictionary
		# form
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		return list(
			self.get_table("qotd")
			.filter(
				{
					"guild": guild
				}
			)
			.run(self.connection)
		)
	
	def qotd_exists(self, qotd, guild):
		# Checks a QOTD entry exists with the id {qotd} and it is
		# "owned" by the correct guild
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		res = (
			self.get_table("qotd")
			.get(qotd)
			.run(self.connection)
		)
		
		return res and res["guild"] == guild
	
	def get_filters(self, guild, channel=""):
		# Returns all filters for the given guild, and channel if
		# specified
		
		match = {
			"guild": str(guild),
			"type": "text"
		}
		
		if channel:
			match["channel"] = str(channel)
		
		return list(
			self.get_table("filters")
			.filter(
				match
			)
			.run(
				self.connection
			)
		)
	
	def insert_punishment(self, **options):
		# Creates a new punishment entry
		
		self.get_table("punishments").insert(
			options
		).run(self.connection)
	
	def get_img_filters(self, guild):
		# Returns all image filters stored for the given guild as a list
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		return list(
			self.get_table("filters").filter(
				{
					"guild": guild,
					"type": "image"
				}
			).run(
				self.connection
			)
		)
	
	def add_text_filter(self, punish, regex, channel, reason, guild):
		# Adds a text filter (Regular Expression) to the given guild
		# and channel
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		if not isinstance(channel, str):
			# Ensure channel is a string
			channel = str(channel)
		
		(
			self.get_table("filters")
			.insert(
				{
					"guild": guild,
					"action": punish,
					"filter": regex,
					"channel": channel,
					"reason": reason,
					"type": "text"
				}
			).run(self.connection)
		)
	
	def filter_exists(self, guild, f_id, f_type):
		# Returns True if the filter being searched for exists,
		# is of the correct type and for the correct guild else False
		
		return len(
			list(
				self.get_table("filters")
				.filter(
					{
						"guild": (
							guild if isinstance(guild, str) else
							str(guild)
						),
						"id": f_id,
						"type": f_type
					}
				)
				.run(self.connection)
			)
		) > 0
	
	def insert_img_filter(
			self, guild, img, ignore_colour, reason,
			name, punishment
		):
		# Inserts an image filter to the database (b64 encoded
		# representation of image)
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		(
			self.get_table("filters")
			.insert(
				{
					"guild": guild,
					"type": "image",
					"img": img,
					"ignore_colour": ignore_colour,
					"reason": reason,
					"name": name,
					"action": punishment
				}
			)
			.run(self.connection)
		)
	
	def img_filter_exists(self, guild, name):
		# Return True if there is one or more entry matching this
		# name and guild
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)
		
		return len(
			list(
				self.get_table("filters")
				.filter(
					{
						"guild": str(guild),
						"type": "image",
						"name": name
					}
				)
				.run(self.connection)
			)
		) > 0
	
	def get_img_filter(self, guild, f_id):
		# Returns the image filter matching guild and id
		
		if not isinstance(guild, str):
			# Ensure guild is a string
			guild = str(guild)

		return list(
			self.get_table("filters")
			.filter(
				{
					"guild": str(guild),
					"type": "image",
					"id": f_id
				}
			)
			.run(self.connection)
		)

	def add_custom_command(self, guild, name, description, body):
		if not isinstance(guild, str):
			guild = str(guild)
		
		(
			self.get_table("customs")
			.insert(
				{
					"guild": guild,
					"name": name.lower(),
					"description": description,
					"body": body
				}
			)
			.run(self.connection)
		)

	def get_customs(self, guild):
		if not isinstance(guild, str):
			guild = str(guild)
			
		return list(
			self.get_table("customs")
			.filter(
				{
					"guild": guild
				}
			)
			.run(self.connection)
		)
	
	def remove_custom(self, name, guild):
		if not isinstance(guild, str):
			guild = str(guild)
		
		(
			self.get_table("customs")
			.filter(
				{
					"name": name.lower(),
					"guild": guild
				}
			)
			.delete()
			.run(self.connection)
		)

	def custom_command_exists(self, name, guild):
		if not isinstance(guild, str):
			guild = str(guild)
		
		return len(
			list(
				self.get_table("customs")
				.filter(
					{
						"name": name.lower(),
						"guild": guild
					}
				)
				.run(self.connection)
			)
		) > 0

	@staticmethod
	def get(iterable, key):
		for i in iterable:
			if key(i):
				return i
		return None

	def get_guild_currency(self, guild):
		if not isinstance(guild, str):
			guild = str(guild)

		return list(
			self.get_table("currency")
			.filter(
				{
					"guild": guild
				}
			)
			.run(self.connection)
		)
	
	def get_currency(self, guild, member):
		if not isinstance(guild, str):
			guild = str(guild)
			
		if not isinstance(member, str):
			member = str(member)
			
		guild_cur = self.get_guild_currency(guild)
		
		member_cur = self.get(
			guild_cur,
			lambda m: m["member"] == member
		)
		
		if not guild_cur or not member_cur:
			blank = {
				"guild": guild,
				"member": member,
				"cur": 0,
				"gamblingSuspended": False
			}
			
			return (
				self.get_table("currency")
				.insert(
					blank,
					return_changes=True
				)
				.run(self.connection)
			)["changes"][0]["new_val"]
			
		return member_cur

	def update_member_cur(self, guild, member, new_amount):
		old_value = self.get_currency(guild, member)
		
		(
			self.get_table("currency")
			.get(old_value["id"])
			.update(
				{
					"cur": new_amount
				}
			)
			.run(self.connection)
		)
		
	def is_gambling_suspended(self, guild, member):
		return (
			self.get_currency(guild, member)
			.get("gamblingSuspended", False)
		)
