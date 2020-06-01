from re import compile
from discord import Embed, Colour
from Utils.CurrencyCommand import CurrencyCommand, gambling_suspended


class CurCommand(CurrencyCommand):
	
	user_resolvable = compile(r"(<@!?)?(\d{17,19})(>)?")
	
	def __init__(self, client):
		self.client = client
		super().__init__(client)
		
		self.name = "cur"
		
		self.aliases = [
			"bal",
			"£",
			"$"
		]
		self.category = "Currency"
		self.description = "Tells you how much currency a person has"
		self.perm_level = 0
		self.usage = "cur [user]"

	@gambling_suspended
	async def currency_run(self, _, message, *args):
		user = message.author
		
		if not args:
			return await self.send_user(message, user)
		
		match = self.user_resolvable.match(args[0])
		
		if match:
			user = message.guild.get_member(match.group(2))
		else:
			return await self.client.errors.InvalidUser(
				args[0]
			).send(
				message.channel
			)
			
		if user:
			return await self.send_user(message, user)
		
		if not args[0].isdigit():
			return await self.client.errors.InvalidUser(
				args[0]
			).send(
				message.channel
			)
		
		target = args[0]
	
		bank = {}
	
		for cur in message.guild.all_currency:
			if cur["member"] == target:
				bank = cur
				break
				
		if not bank:
			return await self.client.errors.InvalidUser(
				args[0]
			).send(
				message.channel
			)
		
		fetched_user = await self.client.fetch_user(
			# Since the data is already in the db it can be assumed
			# the id is valid
			int(target)
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				description="{} has {} {}".format(
					f"{fetched_user.name}#{fetched_user.discriminator}",
					bank["cur"],
					self.client.config.currency_name
				)
			)
		)
			
	async def send_user(self, message, user):
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				description="{} has {} {}".format(
					f"{user.name}#{user.discriminator}",
					user.cur,
					self.client.config.currency_name
				)
			)
		)


def setup(client):
	client.command_handler.add_command(
		CurCommand(client)
	)
