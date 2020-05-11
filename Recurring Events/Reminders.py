from time import time as epoch
from discord.errors import HTTPException, Forbidden
from discord import Embed


class Reminders:
	def __init__(self, client):
		self.client = client
	
	async def run(self):
		current_time = epoch() * 1000
		# Retrieve all reminders where the time to send them is
		# either equal to or less than the current time
		reminders = list(
			self.client.DataBaseManager
			.get_table("reminders")
			.filter(lambda r: r["expiry"] <= current_time)
			.run(self.client.DataBaseManager.connection)
		)

		for reminder in reminders:
			# For each reminder, fetch the user
			user = self.client.get_user(int(reminder["user"]))
			
			if not user:
				# If somehow the user doesn't exist, delete the
				# reminder then continue to the next reminder
				(
					self.client.DataBaseManager
					.get_table("reminders")
					.get(reminder["id"])
					.delete()
					.run(self.client.DataBaseManager.connection)
				)
				continue
			
			try:
				await user.send(
					embed=Embed(
						description=reminder["message"],
						type="rich",
						title="Reminder"
					)
				)
				
			except (HTTPException, Forbidden):
				pass
				# Assume user blocked the bot
			
			# Delete the reminder from the db
			(
				self.client.DataBaseManager
				.get_table("reminders")
				.get(reminder["id"])
				.delete()
				.run(self.client.DataBaseManager.connection)
			)


def setup(setup_event, client):
	# Setup the event to run once evey 2 seconds
	setup_event(
		Reminders(client),
		2
	)
