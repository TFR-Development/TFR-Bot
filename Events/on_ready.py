from asyncio import sleep
from os import listdir
from importlib import import_module


class RecurringEvent:
	def __init__(self, func, timeout):
		self.func = func
		self.timeout = timeout


class ReadyEvent:
	def __init__(self, client):
		
		self.recurring_events = []
		self.max_timeout = 1
		
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
		
		self.client = client
		
		self._sent_load_success = False
		
		# Add on_ready event as ready listener
		client.event(self.on_ready)
		
	async def on_ready(self):
		current_interval = 0
		
		# Log bot online
		
		print(f"{self.client.user} is ready")
		
		commands = [
			f"`{cmd.name}`" for cmd in
			self.client.CommandHandler.commands
		]

		commands.sort(key=lambda c : c[1:-1])

		await self.client.WebhookManager.send(
			f"{self.client.user} is ready\nLoaded commands: "
			f"{', '.join(commands)}"
		)
		
		if not self._sent_load_success:
			self._sent_load_success = True
			for e in self.client.failed_events:
				await self.client.WebhookManager.send(
					f"Failed to load event {e[0]} for ```py\n{e[1]}```"
				)
				await sleep(2)
				
			for e in self.client.failed_commands:
				await self.client.WebhookManager.send(
					f"Failed to load command {e[0]} for "
					f"```py\n{e[1]}```"
				)
				await sleep(2)
		
		while True:
			# Asynchronous delay of 1 second stops rest of the
			# program being blocked
			await sleep(1)
			
			current_interval += 1
			
			for event in self.events_to_run(current_interval):
				# Run each event at its interval
				await event.func.run()
				
			if current_interval >= self.max_timeout:
				# Reset current_interval
				current_interval = 0
				
	def add_event(self, func, timeout):
		if timeout > self.max_timeout:
			# Update self.max_timeout accordingly
			self.max_timeout = timeout
		
		self.recurring_events.append(
			RecurringEvent(
				func,
				timeout
			)
		)
		
	def events_to_run(self, interval):
		if interval == 0:
			return self.recurring_events
			# Initially run all
		
		return list(
			filter(
				lambda event: (
					interval == event.timeout or
					interval % event.timeout == 0
				),
				self.recurring_events
			)
		)
		

def setup(client):
	ReadyEvent(client)
