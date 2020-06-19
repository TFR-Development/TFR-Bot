from random import randint
from Utils.CustomCommand import CustomCommand
from re import match, escape


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
		
		# Defining prefixes here also ensures a guild object will
		# exist so the automod filters can run without error
		prefixes = [
			self.client.data_base_manager.get_prefix(
				str(message.guild.id)
			),
			f"<@{self.client.user.id}>",
			f"<@!{self.client.user.id}>",
		]
		
		if await self.client.auto_mod.auto_mod_filter(message):
			# AUTOMOD -> Check message content, if there was a match,
			# end here
			return
		
		if not self.client.data_base_manager.in_xp_cooldown(
				message.author.id, message.guild.id):
			
			# The user isn't in cooldown for xp, add xp
			
			self.client.data_base_manager.add_xp(
				guild=message.guild.id,
				member=message.author.id,
				amount=randint(1, 5)
			)
			
		prefix = self.find_prefix(
			prefixes,
			message.content
		)
		# Attempts to find the prefix used in this message, allowing
		# mentions as a prefix
		
		customs = self.client.data_base_manager.get_customs(
			str(message.guild.id)
		)
		
		custom = self.find_custom(message, customs)
		
		if not prefix:
			# No prefix match, check for custom commands and then end
			# here
			if custom:
				await custom.run(
					message,
					(
						message.content[len(custom.name):]
						.strip().split(" ")
					)
				)
			
			return
		
		# Remove the prefix from the message content and remove
		# leading / trailing whitespace then split into a list at spaces
		args = message.content[len(prefix):].strip().split(" ")
		
		if len(args) == 0:
			# The message was just a prefix, there's no message
			# remaining, check for a custom command then end here
			
			if custom:
				await custom.run(
					message,
					(
						message.content[len(custom.name):]
						.strip().split(" ")
					)
				)
			
			return
		
		cmd = args.pop(0)
		# The command name is the first argument (first word after the
		# prefix)
		
		command = self.client.command_handler.get_command(cmd)
		# Search for the command (case insensitive)

		if not command:
			# No command was found, check for custom command then return
			
			if custom:
				await custom.run(
					message,
					message.content[len(custom.name):].strip().split(" ")
				)
			
			return
		
		command.prefix = prefix
		
		command.author_perm_level = self.client.calculate_permissions(
			self.client,
			message.author,
			message.guild
		).calculate()
		
		if command.author_perm_level < command.perm_level:
			# The user doesn't have permission to use this command,
			# send an error message and return
			return await self.client.errors.MissingPermissions().send(
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
	
	@staticmethod
	def cc_regex(name):
		return fr"(?i)^{escape(name)}($|\s)"
	
	def find_custom(self, message, customs):
		for c in customs:
			if match(self.cc_regex(c["name"]), message.content):
				return CustomCommand.load(
					c["body"],
					self.client,
					c["name"],
					c["description"]
				)
		return None


def setup(client):
	MessageEvent(client)
