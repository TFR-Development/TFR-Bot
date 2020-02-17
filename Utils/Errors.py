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
			colour=Colour.from_rgb(255, 70, 73),
			title="Missing Arguments",
			description=f"Missing `{arg_name.replace('`', '')}` from your command!"
		)
		
		
class InvalidArgs(ErrorBase):
	def __init__(self, arg, proper_type):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="Invalid Arguments",
			description=
			f"`{arg.replace('`', '')}` isn't a valid `{proper_type.replace('`', '')}`"
		)


class MissingPermissions(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="Missing Permissions",
			description="You do not have permission to run this command"
		)


class MissingFile(ErrorBase):
	def __init__(self, file_type):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="Missing File",
			description=(
				f"Expected {file_type} to be attached to the message"
			)
		)


class NoXP(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(0, 0, 0),
			title="No XP",
			description="This user hasn't collected any XP yet"
		)


class NoAPIConnection(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="No API Connection",
			description=
			"Unable to connect to the API, please contact a Bot Owner "
			"or Bot Admin"
		)


class APIError(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="API Error",
			description=
			"Error from API request, please contact a Bot Admin / "
			"Owner",
		)


class NoQOTD(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="No QOTD",
			description="No QOTD left in storage"
		)


class NoQOTDChannel(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="No QOTD Channel Set",
			description="No QOTD channel has been set for this server"
		)


class InvalidQOTDChannel(ErrorBase):
	def __init__(self):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="Invalid QOTD Channel",
			description="The QOTD channel which was set is now invalid"
		)


class UnchangedOutput(ErrorBase):
	def __init__(self, from_type, to_type):
		self.message = Embed(
			type="rich",
			colour=Colour.from_rgb(255, 70, 73),
			title="No Conversion Necessary",
			description=f"`{from_type}` and `{to_type}` are the same"
		)
