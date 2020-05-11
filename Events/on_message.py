from random import randint


class MessageEvent:

	def __init__(self, client):
		self.client = client
		
		client.event(self.on_message)

	async def on_message(self, message):
		if message.author.bot:
			# Ignore bot messages
			return
		
		if not message.guild:
			# Ignore DM's
			return
		
		if await self.client.AutoMod.auto_mod_filter(message):
			# AUTOMOD -> Check message content, if there was a match,
			# end here
			return
		
		if not self.client.DataBaseManager.in_xp_cooldown(
				message.author.id, message.guild.id):
			
			# The user isn't in cooldown for xp, add xp
			
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
		# Attempts to find the prefix used in this message, allowing
		# mentions as a prefix
		
		if not prefix:
			# No prefix match, end here
			return
		
		# Remove the prefix from the message content and remove
		# leading / trailing whitespace then split into a list at spaces
		args = message.content[len(prefix):].strip().split(" ")
		
		if len(args) == 0:
			# The message was just a prefix, there's no message
			# remaining, end here
			return
		
		cmd = args.pop(0)
		# The command name is the first argument (first word after the
		# prefix)
		
		command = self.client.CommandHandler.get_command(cmd)
		# Search for the command (case insensitive)

		if not command:
			# No command was found, end here
			return
		
		command.prefix = prefix
		
		command.author_perm_level = self.client.CalculatePermissions(
			self.client,
			message.author,
			message.guild
		).calculate()
		
		if command.author_perm_level < command.perm_level:
			# The user doesn't have permission to use this command,
			# send an error message and return
			return await self.client.Errors.MissingPermissions().send(
				message.channel
			)
		
		# Support for typing option (for slow commands)
		if getattr(command, "typing", False):
			async with message.channel.typing():
				# Run the command within an asynchronous context
				# manager for typing in the current channel
				await command.run(command, message, *args)
		else:
			# Run the command without typing
			await command.run(command, message, *args)
		
	@staticmethod
	def find_prefix(prefixes, msg):
		# Basic linear search to find the first element of prefixes
		# which matches the start of msg
		for prefix in prefixes:
			if msg.startswith(prefix):
				return prefix
	

def setup(client):
	MessageEvent(client)
