class Permissions:
	def __init__(self, client, user, guild):
		self.client = client
		self.user = user
		self.guild = guild
		
		self.perms = [
			{
				"name": "Everyone",
				"level": 0
			},
			{
				"name": "Partner Manager",
				"level": 1
			},
			{
				"name": "Helper",
				"level": 2
			},
			{
				"name": "Moderator",
				"level": 3
			},
			{
				"name": "Administrator",
				"level": 4
			},
			{
				"name": "Server Owners",
				"level": 5
			},
			{
				"name": "Bot Admins",
				"level": 9
			},
			{
				"name": "Bot Owner",
				"level": 10
			}
		]
		
	def calculate(self):
		for perm in list(reversed(self.perms)):
			if getattr(self, "level_{}".format(perm["level"]))(
					self.user,
					self.guild
			):
				return perm["level"]
	
	@staticmethod
	def level_0(*_):
		# User permission, @everyone level
		return True
	
	def level_1(self, user, guild=None):
		# partner manager role
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = (
			self.client.DataBaseManager.get_table("guilds")
			.filter({
				"guild": guild.id		
			})
		)
		
		if "partner_manager" in guild_conf.keys():
			pm_roles = guild_conf["partner_manager"]
			for role in pm_roles:
				if role in user.roles:
					return True
		return False
	
	def level_2(self, user, guild=None):
		# helper
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = (
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": guild.id
			})
		)
		
		if "helper" in guild_conf.keys():
			helper_roles = guild_conf["helper"]
			for role in helper_roles:
				if role in user.roles:
					return True
		return False
	
	def level_3(self, user, guild=None):
		# moderator
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = (
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": guild.id
			})
		)
		
		if "moderation" in guild_conf.keys():
			mod_roles = guild_conf["moderation"]
			for role in mod_roles:
				if role in user.roles:
					return True
		return False
	
	def level_4(self, user, guild=None):
		# admins
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = (
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": guild.id
			})
		)
		
		if "admin" in guild_conf.keys():
			admin_roles = guild_conf["admin"]
			for role in admin_roles:
				if role in user.roles:
					return True
		return False
	
	def level_5(self, user, guild=None):
		# server owners
		if not hasattr(user, "roles"):
			return False
		
		if user.id == guild.owner.id:
			return True
		
		guild_conf = (
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": guild.id
			})
		)
		
		if "owners" in guild_conf.keys():
			owners_roles = guild_conf["owners"]
			for role in owners_roles:
				if role in user.roles:
					return True
		return False
	
	def level_9(self, user, _):
		# bot admins
		return user.id in self.client.config["bot admins"]
	
	def level_10(self, user, _):
		# bot owner
		return user.id == int(self.client.config["owner id"])