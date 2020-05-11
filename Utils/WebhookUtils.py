from aiohttp import ClientSession
from discord import Webhook, AsyncWebhookAdapter
from discord.errors import (
	HTTPException, NotFound, Forbidden, InvalidArgument
)
from datetime import datetime


class WebhookManager:
	def __init__(self, client):
		self.client = client
		self._webhook_exceptions = (
			HTTPException,
			NotFound,
			Forbidden,
			InvalidArgument,
		)

	async def send(self, *args, **kwargs):
		try:
			async with ClientSession() as session:
				webhook = Webhook.from_url(
					self.client.config.webhook,
					adapter=AsyncWebhookAdapter(session)
				)
				
				if len(args) == 0 and kwargs.get("content") is None:
					kwargs["content"] = self.format_date()
				
				elif kwargs.get("content") is not None:
					kwargs["content"] = self.format_date() + kwargs[
						"content"
					]
				
				elif len(args) > 0:
					args = [self.format_date() + " ".join(args)]
				
				await webhook.send(*args, **kwargs)
				
		except self._webhook_exceptions as e:
			print("[WARN]", self.format_date(), e)
			pass

	@staticmethod
	def format_date():
		return datetime.now().strftime("`[LOG] %a %d %b %Y %H:%M:%S`: ")
