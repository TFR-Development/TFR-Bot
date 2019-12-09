class CommandHandler:
	def __init__(self):
		self.commands = []
		
	def get_command(self, cmd):
		for command in self.commands:
			if cmd in [*command.aliases, command.name]:
				return command
			
	def add_command(self, command):
		self.commands.append(command)
		
	def add_commands(self, *commands):
		self.commands = [*self.commands, *commands]