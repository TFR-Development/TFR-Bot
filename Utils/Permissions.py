class Permissions:
	def __init__(self, client=None, user=None, guild=None):
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
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds")
			.filter({
				"guild": str(guild.id)		
			}).run(self.client.DataBaseManager.connection)
		)[0]
		
		if "partner_manager" in guild_conf:
			pm_roles = guild_conf["partner_manager"]
			for role in pm_roles:
				if self.has_role(user.roles, role):
					return True
		return False
	
	def level_2(self, user, guild=None):
		# helper
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": str(guild.id)
			})
			.run(self.client.DataBaseManager.connection)
		)[0]
		
		if "helper" in guild_conf:
			helper_roles = guild_conf["helper"]
			for role in helper_roles:
				if self.has_role(user.roles, role):
					return True
		return False
	
	def level_3(self, user, guild=None):
		# moderator
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": str(guild.id)
			})
			.run(self.client.DataBaseManager.connection)
		)[0]
		
		if "moderator" in guild_conf:
			mod_roles = guild_conf["moderator"]
			for role in mod_roles:
				if self.has_role(user.roles, role):
					return True
		return False
	
	def level_4(self, user, guild=None):
		# admins
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": str(guild.id)
			})
			.run(self.client.DataBaseManager.connection)
		)[0]
		
		if "administrator" in guild_conf:
			admin_roles = guild_conf["administrator"]
			for role in admin_roles:
				if self.has_role(user.roles, role):
					return True
		return False
	
	def level_5(self, user, guild=None):
		# server owners
		if not hasattr(user, "roles"):
			return False
		
		if user.id == guild.owner.id:
			return True
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter({
				"guild": str(guild.id)
			})
			.run(self.client.DataBaseManager.connection)
		)[0]
		
		if "owner" in guild_conf:
			owners_roles = guild_conf["owner"]
			for role in owners_roles:
				if self.has_role(user.roles, role):
					return True
		return False
	
	def level_9(self, user, _):
		# bot admins
		return user.id in self.client.config.bot_admins
	
	def level_10(self, user, _):
		# bot owner
		return user.id == int(self.client.config.owner_id)
	
	def as_string(self, level):
		for perm in self.perms:
			if perm["level"] == level:
				return perm["name"]
		raise ValueError("Invalid Permission level provided")
	
	@staticmethod
	def has_role(roles, rid):
		rid = str(rid)
		for r in roles:
			if str(r.id) == rid:
				return True
		return False
