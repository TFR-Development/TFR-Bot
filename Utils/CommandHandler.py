class CommandHandler:
	def __init__(self):
		self.commands = []
		
	def get_command(self, cmd):
		for command in self.commands:
			command_names = [
				*[c.lower() for c in command.aliases],
				command.name.lower()
			]
			if cmd.lower() in command_names:
				return command
			
	def add_command(self, command):
		self.commands.append(command)
		
	def add_commands(self, *commands):
		self.commands = [*self.commands, *commands]