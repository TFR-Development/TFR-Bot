from discord import Embed, Colour


class PermissionBase:
	def __init__(self, client):
		self.client = client
		self.perms = [
			"partner manager",
			"helper",
			"moderator",
			"administrator",
			"owner"
		]
		self.perm_level = 5
		self.category = "Administration"
		
	async def handle(self, message, mode, embed_msg, *args):
		# Make a request to the API to parse quote wrapped arguments
		parsed = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if parsed == -1:
			# API request failed, send an error
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		if "Error" in parsed.keys():
			# The API returned an error
			return await self.client.Errors.APIError().send(
				message.channel
			)
		
		args = parsed.get("Message", [])
		
		if len(args) < 1:
			# No arguments supplied, send an error for missing args
			return await self.client.Errors.MissingArgs("role").send(
				message.channel
			)
		
		role_resolvable = args[0]
		
		role = self.get_role(role_resolvable, message.guild)
		
		if not role:
			# Role not found
			return await self.client.Errors.InvalidArgs(
				role_resolvable,
				"role"
			).send(
				message.channel
			)
		
		if len(args) < 2:
			# No permission level supplied
			return await self.client.Errors.MissingArgs(
				"perm level"
			).send(message.channel)
		
		perm = args[1].lower()
		# Convert to lowercase (input sensitisation)
		
		if perm not in self.perms:
			# Invalid permission level
			return await self.client.Errors.InvalidArgs(
				perm,
				"permission"
			).send(message.channel)
		
		old_conf = list(
			self.client.DataBaseManager.get_table("guilds")
			.filter(
				{
					"guild": str(message.guild.id)
				}
			).run(self.client.DataBaseManager.connection)
		)
		# Retrieve the old config for permissions
		
		if old_conf:
			# Old config found, use the first match
			old_conf = old_conf[0]
			
			perm = perm.replace(" ", "_")
			
			# partner manager -> partner_manager
			
			if perm in old_conf:
				# The old config had the key for this permission already
				old_conf = old_conf[perm]
			else:
				# This key doesn't exist yet, initialise as empty list
				old_conf = []
		else:
			# No match found, use an empty list
			old_conf = []
		
		if role.id not in old_conf and mode == "remove":
			return await message.channel.send(
				embed=Embed(
					type="rich",
					title="Permission not attached to role",
					colour=Colour.from_rgb(255, 70, 73),
					description=(
						f"The `{role.name}` role didn't have "
						f"{perm.title()} permissions"
					)
				)
			)
		
		if mode == "remove":
			# Remove all duplicates and all instances of role.id
			old_conf = list(
				set(
					(n for n in old_conf if n != role.id)
				)
			)
			
		elif mode == "append":
			# Add role to the config
			old_conf.append(role.id)
			
			# Remove all duplicates
			old_conf = list(
				set(
					old_conf
				)
			)
		
		(
			self.client.DataBaseManager.get_table("guilds")
			.filter(
				{
					"guild": str(message.guild.id)
				}  # Select guild entries with matching guild id
			).update(
				{
					perm: old_conf  # Update the value of the perm key
					# to old_conf
				}
			).run(self.client.DataBaseManager.connection)
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="Success!",
				description=f"`{role.name}` is {embed_msg} a"
				f"{'n' if perm[0].upper() in 'AEIOU' else ''} "
				f"`{perm.title()}`"
			)
		)
		
	@staticmethod
	def get_role(role, guild):
		if role.isdigit() and 17 <= len(role) <= 19:
			# Matches an ID
			r = guild.get_role(int(role))
			if r:
				# If there's a role matching by ID, return that
				return r
		
		for role_iter in guild.roles:
			# Last resort: iter over every role and compare role name
			if role_iter.name.lower() == role.lower():
				# Match: Return role
				return role_iter
		
		return None


class SetPerm(PermissionBase):
	def __init__(self, client):
		self.client = client
		
		self.name = "permrole"
		self.aliases = ["ap", "attachperm"]
		self.description = \
			"Sets the permission level of a specific role"
		self.usage = \
			"permrole \"<role>\" \"<partner manager/helper/moderator/" \
			"administrator/owner>\""

		super().__init__(client)
	
	async def run(self, _, message, *args):
		await self.handle(message, "append", "now", *args)


class RemovePerm(PermissionBase):
	def __init__(self, client):
		self.client = client
		
		self.name = "unpermrole"
		self.aliases = ["dp", "detachperm"]
		self.description = \
			"Removes the permission level of a specific role"
		self.usage = \
			"unpermrole \"<role>\" \"<partner " \
			"manager/helper/moderator/" \
			"administrator/owner>\""
		
		super().__init__(client)
	
	async def run(self, _, message, *args):
		await self.handle(message, "remove", "no longer", *args)
		
		
def setup(client):
	client.CommandHandler.add_commands(
		RemovePerm(client),
		SetPerm(client)
	)
