from discord import Embed, Colour


class ErrorBase:
	async def send(self, channel):
		return await channel.send(
			embed=self.message,
			delete_after=20.0
		)


class MissingArgs(ErrorBase):
	def __init__(self, arg_name):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 0, 0),
			title="Missing Arguments",
			description=f"Missing {arg_name} from your command!"
		)
		
		
class InvalidArgs(ErrorBase):
	def __init__(self, arg, proper_type):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 0, 0),
			title="Invalid arguments",
			description=f"{arg} isn't a valid {proper_type}"
		)


class MissingPermissions(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 0, 0),
			title="Missing Permissions",
			description="You do not have permission to run this command"
		)
