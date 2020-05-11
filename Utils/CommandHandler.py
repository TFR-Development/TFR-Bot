class CommandHandler:
	def __init__(self):
		self.commands = []
		
	def get_command(self, cmd):
		for command in self.commands:
			# Iter over all commands (linear search for valid command)
			command_names = [
				*[c.lower() for c in command.aliases],
				command.name.lower()
			]
			# Combine all aliases and command name to lowercase,
			# then into single array
			if cmd.lower() in command_names:
				# Command name match found, return command object
				return command
			
	def add_command(self, command):
		self.commands.append(command)
		# Extend self.commands list with command
		
	def add_commands(self, *commands):
		self.commands = [*self.commands, *commands]
		# Extends self.commands with multiple commands (commands
		# contains a tuple of command objects)
