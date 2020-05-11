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
			# Iter over levels starting from the highest level to find
			# the right level
			if getattr(self, "level_{}".format(perm["level"]))(
					self.user,
					self.guild
			):
				return perm["level"]
	
	@staticmethod
	def level_0(*_):
		# User permission, @everyone level
		return True
	
	def level_1(self, user, guild):
		# Partner manager role
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds")
			.filter(
				{
					"guild": str(guild.id)
				}
			).run(self.client.DataBaseManager.connection)
		)[0]
		# Find guild entry in the guilds table
		
		if "partner_manager" in guild_conf:
			# The entry has a partner_manager key
			pm_roles = guild_conf["partner_manager"]
			for role in pm_roles:
				if self.has_role(user.roles, role):
					# The user has this role, they're a partner manager
					return True
				
		# The user doesn't have any of the partner manager roles
		return False
	
	def level_2(self, user, guild):
		# Helper
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter(
				{
					"guild": str(guild.id)
				}
			)
			.run(self.client.DataBaseManager.connection)
		)[0]
		# Retrieve the guild entry from the guilds table
		
		if "helper" in guild_conf:
			# If the entry has a "helper" key
			helper_roles = guild_conf["helper"]
			for role in helper_roles:
				if self.has_role(user.roles, role):
					# This role is a helper role and one of the users
					# roles
					return True
				
		# The user isn't a helper, they don't have any of the helper
		# roles
		return False
	
	def level_3(self, user, guild):
		# Moderator
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter(
				{
					"guild": str(guild.id)
				}
			)
			.run(self.client.DataBaseManager.connection)
		)[0]
		# Retrieve the entry from the guilds table
		
		if "moderator" in guild_conf:
			# The entry has a "moderator" key
			mod_roles = guild_conf["moderator"]
			for role in mod_roles:
				if self.has_role(user.roles, role):
					# This is a mod role and the user has it
					return True
				
		# The user doesn't have any mod roles
		return False
	
	def level_4(self, user, guild):
		# Admins
		if not hasattr(user, "roles"):
			return False
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter(
				{
					"guild": str(guild.id)
				}
			)
			.run(self.client.DataBaseManager.connection)
		)[0]
		# Retrieve the entry from the guilds table
		
		if "administrator" in guild_conf:
			# If the entry has an "administrator" key
			admin_roles = guild_conf["administrator"]
			
			for role in admin_roles:
				if self.has_role(user.roles, role):
					# This is an admin role and the user has it
					return True
				
		# The user is not an admin, they don't have an admin role
		return False
	
	def level_5(self, user, guild):
		# server owners
		if not hasattr(user, "roles"):
			return False
		
		if user.id == guild.owner.id:
			# The user is the actual guild owner
			return True
		
		guild_conf = list(
			self.client.DataBaseManager.get_table("guilds").filter(
				{
					"guild": str(guild.id)
				}
			)
			.run(self.client.DataBaseManager.connection)
		)[0]
		# Retrieve the entry from the guilds table
		
		if "owner" in guild_conf:
			# The entry has an "owner" key
			owners_roles = guild_conf["owner"]
			for role in owners_roles:
				if self.has_role(user.roles, role):
					# The user has an "owner" role
					return True
		
		# The user isn't an owner
		return False
	
	def level_9(self, user, _):
		# Bot admins -> Simple ID comparison
		return user.id in self.client.config.bot_admins
	
	def level_10(self, user, _):
		# Bot owner -> Simple ID comparison
		return user.id == self.client.config.owner_id
	
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
