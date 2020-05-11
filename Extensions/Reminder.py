from time import time as epoch


class AddReminder:
	def __init__(self, client):
		self.client = client
		
		self.name = "remindme"
		self.aliases = [
			"remind",
			"reminder"
		]
		self.perm_level = 0
		self.description = "Sets a reminder"
		self.category = "Miscellaneous"
		self.usage = "remindme <time> [message]"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args supplied
			return await self.client.Errors.MissingArgs(
				"time argument"
			).send(message.channel)
		
		time_parse = self.client.TimeParser(" ".join(args))
		# Form a TimeParser object to parse the time from the message
		time, msg = time_parse.parse()
		
		if not time:
			# Time not found in message
			return await self.client.Errors.MissingArgs(
				"time argument"
			).send(message.channel)

		# Insert reminder into reminders table
		self.client.DataBaseManager.get_table("reminders").insert(
			{
				"user": str(message.author.id),
				"expiry": (epoch() * 1000) + time,
				"message": msg,
				"type": "dm"
			}
		).run(self.client.DataBaseManager.connection)
		
		# parse_to_string returns the date in human readable form
		await message.channel.send(
			f"Reminder set for {time_parse.parse_to_string()}"
		)
		

def setup(client):
	client.CommandHandler.add_commands(
		AddReminder(client)
	)
