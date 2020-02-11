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
		parsed = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if parsed == -1:
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		if "Error" in parsed.keys():
			return await self.client.Errors.APIError().send(
				message.channel
			)
		
		args = parsed.get("Message", [])
		
		if len(args) < 1:
			return await self.client.Errors.MissingArgs("role").send(
				message.channel
			)
		
		role_resolvable = args[0]
		
		role = self.get_role(role_resolvable, message.guild)
		
		if not role:
			return await self.client.Errors.InvalidArgs(
				role_resolvable,
				"role"
			).send(
				message.channel
			)
		
		if len(args) < 2:
			return await self.client.Errors.MissingArgs(
				"perm level"
			).send(message.channel)
		
		perm = args[1].lower()
		
		if perm not in self.perms:
			return await self.client.Errors.InvalidArgs(
				perm,
				"permission"
			).send(message.channel)
		
		old_conf = list(
			self.client.DataBaseManager.get_table("guilds")
			.filter({
				"guild": str(message.guild.id)
			}).run(self.client.DataBaseManager.connection)
		)
		
		if old_conf:
			old_conf = old_conf[0]
			if perm.replace(" ", "_") in old_conf:
				old_conf = old_conf[perm.replace(" ", "_")]
			else:
				old_conf = []
		else:
			old_conf = []
		try:
			getattr(old_conf, mode)(str(role.id))
			
		except ValueError:
			return await message.channel.send(embed=Embed(
				type="rich",
				title="Permission not attached to role",
				colour=Colour.from_rgb(255, 70, 73),
				description=(
					f"The `{role.name}` role didn't have {perm.title()}"
					f" permissions"
				)
				
			))
		
		(
			self.client.DataBaseManager.get_table("guilds")
			.filter({
				"guild": str(message.guild.id)
			}).update({
				perm: old_conf
			}).run(self.client.DataBaseManager.connection)
		)
		
		await message.channel.send(embed=Embed(
			type="rich",
			colour=Colour.from_rgb(111, 255, 235),
			title="Success!",
			description=f"`{role.name}` is {embed_msg} a"
			f"{'n' if perm.title()[0] in 'AEIOU' else ''} "
			f"`{perm.title()}`"
		))
		
	@staticmethod
	def get_role(role, guild):
		if role.isdigit() and 17 <= len(role) <= 19:
			r = guild.get_role(int(role))
			if r:
				return r
		
		for role_iter in guild.roles:
			if role_iter.name.lower() == role.lower():
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
