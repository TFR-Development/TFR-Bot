from Utils.CurrencyCommand import (
	CurrencyCommand, gambling_suspended, command_cooldown
)
from discord import Embed, Colour


class TimelyCommand(CurrencyCommand):
	
	def __init__(self, client):
		super().__init__(client)
		self.name = "timely"
		self.aliases = [
			"daily",
			"dailies"
		]
		self.category = "Currency"
		self.description = "Gives you your timely currency for the day"
		self.cooldown = 12 * 60 * 60  # 12 hours (43200 seconds)
		self.perm_level = 0
		self.timely_amount = self.client.config.timely_amount or 20
		
	@gambling_suspended
	@command_cooldown(name="timely")
	async def currency_run(self, _, message, *__):
		message.author.cur += self.timely_amount
		
		await message.channel.send(
			embed=Embed(
				title="Claimed timely",
				description=self.gen_description(message),
				colour=Colour.from_rgb(180, 111, 255)
			)
		)
		
	def gen_description(self, msg):
		return (
			"You've claimed your {} {}'s, you can claim again in {}"
			.format(
				self.timely_amount,
				self.client.config.currency_name,
				self.time_formatter(
					self.client.cooldown_manager.get_cooldown(
						"timely",
						(msg.author.id, msg.guild.id,)
					)
				)
			)
		)


def setup(client):
	client.command_handler.add_command(
		TimelyCommand(client)
	)
