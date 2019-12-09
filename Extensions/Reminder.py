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
		
	async def run(self, cmd, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs(
				"time argument"
			).send(message.channel)
		
		time_parse = self.client.TimeParser(" ".join(args))
		time, msg = time_parse.parse()
		
		if not time:
			return await self.client.Errors.MissingArgs(
				"time argument"
			)

		self.client.DataBaseManager.get_table("reminders").insert({
			"user": str(message.author.id),
			"expiry": (epoch() * 1000) + time,
			"message": msg
		}).run(self.client.DataBaseManager.connection)
		
		await message.channel.send(
			f"Reminder set for {time_parse.parse_to_string()}"
		)
		

def setup(client):
	client.CommandHandler.add_commands(
		AddReminder(client)
	)
