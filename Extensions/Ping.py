class Ping:
	
	def __init__(self, client):
		self.client = client
		
		self.name = "ping"
		self.aliases = []
		self.perm_level = 0
		self.description = "Pings and pongs, gives some latency info"
		self.category = "Miscellaneous"
		
	async def run(self, cmd, message, *args):
		await message.channel.send(
			f"""Pong!:ping_pong:\nLatency {round(
				self.client.latency * 1000,
				3)
			}ms"""
		)
		

def setup(client):
	client.CommandHandler.add_command(Ping(client))
