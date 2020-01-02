from time import time as epoch
from discord.errors import HTTPException, Forbidden
from discord import Embed


class Reminders:
	def __init__(self, client):
		self.client = client
	
	async def run(self):
		current_time = epoch() * 1000
		reminders = list(
			self.client.DataBaseManager
			.get_table("reminders")
			.filter(lambda r: r["expiry"] <= current_time)
			.run(self.client.DataBaseManager.connection)
		)

		for reminder in reminders:
			user = self.client.get_user(int(reminder["user"]))
			if not user:
				continue
			try:
				await user.send(embed=Embed(
						description=reminder["message"],
						type="rich",
						title="Reminder"
					)
				)
			except (HTTPException, Forbidden):
				pass
				# Assume user blocked the bot
			(
				self.client.DataBaseManager
				.get_table("reminders")
				.get(reminder["id"])
				.delete()
				.run(self.client.DataBaseManager.connection)
			)


def setup(setup_event, client):
	setup_event(
		Reminders(client),
		2
	)
