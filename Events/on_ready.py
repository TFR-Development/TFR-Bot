from asyncio import sleep
from os import listdir
from importlib import import_module


class ReadyEvent:
	def __init__(self, client):
		self.client = client
		
		for event in listdir("Recurring Events"):
			# Load all recurring events
			if not event.endswith(".py"):
				continue
				
			# Import the file
			file = import_module(
				f"Recurring Events.{event.split('.')[0]}"
			)
			
			if not hasattr(file, "setup"):
				# No setup function, warn and continue
				print(
					f"Unable to load recurring event {event}, has no"
					" setup function"
				)
				continue
				
			file.setup(self.add_event, client)
		
		self._sent_load_success = False
		
		# Add on_ready event as ready listener
		client.event(self.on_ready)
		
	async def on_ready(self):
		
		# Log bot online
		print(f"{self.client.user} is ready")
		
		await self.client.webhook_manager.send(
			f"{self.client.user} is ready"
		)
		
		if not self._sent_load_success:
		
			commands = [
				f"`{cmd.name}`" for cmd in
				self.client.command_handler.commands
			]
			
			commands.sort(key=lambda c: c[1:-1])
			
			await self.client.webhook_manager.send(
				f"Loaded commands: {', '.join(commands)}"
			)
			
			self._sent_load_success = True
			for e in self.client.failed_events:
				await self.client.webhook_manager.send(
					f"Failed to load event {e[0]} for ```py\n{e[1]}```"
				)
				await sleep(2)
				
			for e in self.client.failed_commands:
				await self.client.webhook_manager.send(
					f"Failed to load command {e[0]} for "
					f"```py\n{e[1]}```"
				)
				await sleep(2)
				
	def add_event(self, func, timeout):
		self.client.loop.create_task(
			self.recurring_event_loop(func.run, timeout)
		)
		
	async def recurring_event_loop(self, func, timeout):
		while True:
			if not self.client.is_ready():
				await self.client.wait_until_ready()
			await func()
			await sleep(timeout)


def setup(client):
	ReadyEvent(client)
