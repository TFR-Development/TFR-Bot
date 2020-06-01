from traceback import format_exc


class ErrorHandler:
	def __init__(self, client):
		self.client = client
		self.client.event(self.on_error)
		
	async def on_error(self, event, *_, **__):
		await self.client.webhook_manager.send(
			f"Exception in `{event}`\n```py\n{format_exc()}```"
		)

		
def setup(client):
	ErrorHandler(client)
