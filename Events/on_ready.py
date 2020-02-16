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
			if not event.endswith(".py"):
				continue
				
			file = import_module(
				f"Recurring Events.{event.split('.')[0]}"
			)
			
			if not hasattr(file, "setup"):
				print(
					f"Unable to load recurring event {event}, has no"
					" setup function"
				)
				continue
				
			file.setup(self.add_event, client)
		
		self.client = client
		client.event(self.on_ready)
		
	async def on_ready(self):
		current_interval = 0
		
		print(
			f"{self.client.user} is online!"
		)

		while True:
			await sleep(1)
			
			current_interval += 1
			for event in self.events_to_run(current_interval):
				await event.func.run()
				
			if current_interval >= self.max_timeout:
				current_interval = 0
				
	def add_event(self, func, timeout):
		if timeout > self.max_timeout:
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
		
		return list(filter(
			lambda event: (
				interval == event.timeout or
				interval % event.timeout == 0
			),
			self.recurring_events
		))
		

def setup(client):
	ReadyEvent(client)
