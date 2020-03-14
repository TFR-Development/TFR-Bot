from rethinkdb import RethinkDB
from time import time as epoch


class DataBaseManager:
	def __init__(self, client):
		self.r = RethinkDB()
		self.connection = self.r.connect(
			port=28015,
			host="localhost"
		)
		self.client = client
		
	def get_db(self):
		return self.r.db("tfr")
	
	def get_table(self, table):
		t_list = self.get_db().table_list().run(self.connection)
		
		if table in t_list:
			return self.get_db().table(table)
		
		self.get_db().table_create(table).run(self.connection)
		
		return self.get_db().table(table)

	def get_prefix(self, guild):
		guild = str(guild)
		guild_conf = list(
			self.get_table("guilds").filter(
				{
					"guild": guild
				}
			).run(self.connection)
		)
		
		if guild_conf:
			guild_conf = guild_conf[0]
			
		if guild_conf and "prefix" in guild_conf.keys():
			return guild_conf["prefix"]
		
		if not guild_conf:
			self.get_table("guilds").insert({
				"guild": guild,
				"prefix": self.client.config.default_prefix
			}).run(self.connection)
			
		else:
			self.get_table("guilds").get(guild).update({
				"prefix": self.client.config.default_prefix
			}).run(self.connection)
			
		return self.client.config.default_prefix

	def update_prefix(self, guild, new_prefix):
		guild = str(guild)
		(
				self.get_table("guilds")
				.filter(
					{
						"guild": guild
					}
				)
				.update(
					{
						"prefix": new_prefix
					}
				)
				.run(self.connection)
		)
		
	def add_xp(self, guild, member, amount):
		guild, member = str(guild), str(member)
		table = self.get_table("xp")
		
		user_xp = list(
			table.filter({
				"guild": guild,
				"user": member
			}).run(self.connection)
		)
		
		if user_xp:
			user_xp = user_xp[0]
			previous = user_xp["xp"]
			self.get_table("xp").get(user_xp["id"]).update({
				"xp": previous + amount,
				"cooldown": (
					epoch() + self.client.config.xp_cooldown
				) * 1000
			}).run(self.connection)
			return previous + amount
		
		else:
			table.insert({
				"guild": guild,
				"user": member,
				"xp": amount,
				"cooldown": (
					epoch() + self.client.config.xp_cooldown
				) * 1000
			}).run(self.connection)
			return amount

	def xp_level(self, guild, member):
		# Seems random for DataBaseManager but it interacts with
		# the database

		guild, member = str(guild), str(member)

		level = 1
		result = list(self.get_table("xp").filter({
			"guild": guild,
			"user": member
		}).run(self.connection))
		
		if result:
			result = result[0]
		else:
			return level
		
		xp = result["xp"]
		
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
	
		# Logic adapted from Nadeko source levelling code for
		# consistency
		
	def in_xp_cooldown(self, member, guild):
		
		member, guild = str(member), str(guild)
		
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
			return False
		
		if "cooldown" not in result[0]:
			return False
		
		return result[0]["cooldown"] >= epoch() * 1000

	def get_xp(self, member, guild):
		xp_db = list(
			self.get_table("xp").filter(
				{
					"guild": guild,
					"member": member
				}
			)
		)
		
		return {
			"xp": xp_db[0]["xp"] if xp_db else 0,
			"level": self.xp_level(
				xp_db[0]["xp"] if xp_db else 0, member
			)
		}
	
	def add_qotd(self, question, thought, fact, guild, author):
		guild = str(guild)
		author = str(author)
		
		(
			self.get_table("qotd")
			.insert(
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
	
	def remove_qotd(self, qotd_id):
		(
			self.get_table("qotd")
			.get(qotd_id)
			.delete()
			.run(self.connection)
		)
		
	def get_qotd_channel(self, guild):
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
		res = (
			self.get_table("qotd")
			.get(qotd)
			.run(self.connection)
		)
		
		return res and res["guild"] == str(guild)
	
	def get_filters(self, guild, channel=None):
		
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
		print(options)
		self.get_table("punishments").insert(
			options
		).run(self.connection)
		
	def get_img_filters(self, guild):
		return list(
			self.get_table("filters").filter(
				{
					"guild": str(guild),
					"type": "image"
				}
			).run(
				self.connection
			)
		)

	def add_text_filter(self, punish, regex, channel, reason, guild):
		(
			self.get_table("filters")
			.insert(
				{
					"guild": str(guild),
					"action": punish,
					"filter": regex,
					"channel": str(channel),
					"reason": reason,
					"type": "text"
				}
			).run(self.connection)
		)

	def filter_exists(self, guild, f_id, f_type):
		return len(
			list(
				self.get_table("filters")
				.filter(
					{
						"guild": str(guild),
						"id": f_id,
						"type": f_type
					}
				)
				.run(self.connection)
			)
		) != 0
