from discord import Embed


class Prefix:
	def __init__(self, client):
		self.client = client
		
		self.name = "setprefix"
		self.aliases = [
			"prefix",
		]
		self.perm_level = 4
		self.description = "Sets the prefix on this server"
		self.category = "Administration"
		self.usage = "setprefix <prefix>"
	
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs("prefix").send(
				message.channel
			)
		
		new_prefix = " ".join(args)
		self.client.DataBaseManager.update_prefix(
			message.guild.id,
			new_prefix
		)
		
		await message.channel.send(
			f"Success! The prefix for {message.guild.name} has been "
			f"updated to `{new_prefix}`"
		)


def setup(client):
	client.CommandHandler.add_commands(
		Prefix(client)
	)
