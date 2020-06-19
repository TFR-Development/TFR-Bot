from Utils.CurrencyUtils import CurrencyGuild, CurrencyMessage
from discord import Guild as DGuild
from time import time as epoch


class CurrencyCommand:
	
	conversion = {
		"y": 31449600,  # year to second multiplier,
		# defined as 52 weeks
		"w": 604800,  # week to second multiplier
		"d": 86400,  # day to second multiplier
		"h": 3600,  # hour to second multiplier
		"m": 60,  # minute to second multiplier
		"s": 1
	}
	
	def __init__(self, client):
		self.client = client
		
	def new_guild(self, guild):
		if isinstance(guild, DGuild):
			return CurrencyGuild(self.client, guild)
		
		g = self.client.get_guild(guild)
	
		if g:
			return CurrencyGuild(self.client, g)
	
	async def run(self, cmd, message, *args):
		message = CurrencyMessage(self.client, message)

		await self.currency_run(cmd, message, *args)
	
	async def currency_run(self, *args):
		pass
	
	def time_formatter(self, time):
		if isinstance(time, float):
			time = time.__round__()
		
		times = ["year", "week", "day", "hour", "minute", "second"]
		time_string = ""
		for t in times:
			multiplier = self.conversion[t[0]]
			current_time = time // multiplier
			time = time % multiplier
			
			if current_time > 0:
				plural = "s " if current_time > 1 else " "
				time_string += str(current_time) + " "
				time_string += t + plural
		
		return time_string.strip()


def gambling_suspended(f):
	async def arg_handler(self, cmd, message, *args):
		if message.author.is_gambling_suspended:
			await self.client.errors.GamblingSuspended().send(
				message.channel
			)
			return
		return await f(self, cmd, message, *args)
	return arg_handler


def command_cooldown(name):
	def decorator(f):
		async def arg_handler(self, cmd, message, *args):
			in_cooldown = (
				self.client
				.cooldown_manager
				.in_cooldown(
					name,
					(message.author.id, message.guild.id,)
				)
			)
			
			if in_cooldown:
				return await self.client.errors.InCooldown(
					self.time_formatter(
						self.client.cooldown_manager.get_cooldown(
							name,
							(message.author.id, message.guild.id,),
						)
					)
				).send(message.channel)
			
			self.client.cooldown_manager.add(
				name,
				(message.author.id, message.guild.id,),
				getattr(self, "cooldown", 0) + epoch()
			)
			
			return await f(self, cmd, message, *args)
		return arg_handler
	return decorator
