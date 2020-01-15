from random import randint


class MessageEvent:

	def __init__(self, client):
		self.client = client
		
		client.event(self.on_message)

	async def on_message(self, message):
		if message.author.bot:
			return
		
		if not message.guild:
			return
		
		if not self.client.DataBaseManager.in_xp_cooldown(
				message.author.id, message.guild.id):
				
			self.client.DataBaseManager.add_xp(
				guild=message.guild.id,
				member=message.author.id,
				amount=randint(1, 5)
			)
			
		prefix = self.find_prefix(
			[
				f"<@{self.client.user.id}>",
				f"<@!{self.client.user.id}>",
				self.client.DataBaseManager.get_prefix(message.guild.id)
			],
			message.content
		)
		
		if not prefix:
			return
		
		args = message.content[len(prefix):].strip().split(" ")
		
		cmd = args.pop(0)
		
		command = self.client.CommandHandler.get_command(cmd)

		if not command:
			return
		
		command.prefix = prefix
		
		command.author_perm_level = self.client.CalculatePermissions(
			self.client,
			message.author,
			message.guild
		).calculate()
		
		if command.author_perm_level < command.perm_level:
			return await self.client.Errors.MissingPermissions().send(
				message.channel
			)
		if getattr(command, "typing", False):
			async with message.channel.typing():
				await command.run(command, message, *args)
		else:
			await command.run(command, message, *args)
		
	@staticmethod
	def find_prefix(prefixes, msg):
		for prefix in prefixes:
			if msg.startswith(prefix):
				return prefix
	

def setup(client):
	MessageEvent(client)
