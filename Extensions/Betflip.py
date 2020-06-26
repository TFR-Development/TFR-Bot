from Utils.CurrencyCommand import (
	CurrencyCommand, gambling_suspended, command_cooldown
)
from re import compile
from random import randint, seed
from os import urandom
from math import ceil
from discord import Embed, Colour


class Betflip(CurrencyCommand):
	
	outcome = compile(
		r"(?i)^([ht])(ead|ail)?s?$"
	)
	
	multiplier = 1.95

	cooldown = 2
	
	def __init__(self, client):
		super().__init__(client)
		self.client = client
		
		self.name = "betflip"
		self.description = "Bet on the outcome of a flipped coin"
		self.perm_level = 0
		self.category = "Currency"
		self.aliases = [
			"bf"
		]
		
		self.usage = "betflip <amount> <outcome>"

	@gambling_suspended
	@command_cooldown(name="betflip")
	async def currency_run(self, _, message, *args):
		if len(args) < 1:
			return await self.client.errors.MissingArgs("amount").send(
				message.channel
			)
		
		if len(args) < 2:
			return await self.client.errors.MissingArgs("outcome").send(
				message.channel
			)
			
		if not args[0].isdigit() and args[1].isdigit():
			amount = int(args[1])
			outcome = args[0]
		elif args[0].isdigit() and not args[1].isdigit():
			amount = int(args[0])
			outcome = args[1]
		else:
			if args[0].isdigit():
				return await self.client.errors.InvalidArgs(
					args[1],
					"outcome"
				).send(message.channel)
			
			return await self.client.errors.InvalidArgs(
				args[0],
				"amount"
			).send(message.channel)
			
		if not self.outcome.match(outcome):
			return await self.client.errors.InvalidArgs(
				outcome,
				"outcome"
			).send(message.channel)
		
		outcome = self.outcome.match(outcome).group(1).lower()
		
		if not message.author.can_gamble(amount):
			return await self.client.errors.MissingCurrency(
				message.author.cur
			).send(message.channel)
		
		seed(urandom(64))
		
		true_outcome = "h" if randint(1, 100) >= 50 else "t"
		
		if outcome == true_outcome:
			win_total = ceil(amount * self.multiplier)
			
			message.author.cur += win_total
			
			return await message.channel.send(
				embed=Embed(
					description=f"Congrats! You won {win_total}",
					type="rich",
					colour=Colour.from_rgb(180, 111, 255)
				)
			)
	
		message.author.cur -= amount
		
		await message.channel.send(
			embed=Embed(
				description="Better luck next time!",
				type="rich",
				colour=Colour.from_rgb(180, 111, 255)
			)
		)


def setup(client):
	client.command_handler.add_command(
		Betflip(client)
	)
