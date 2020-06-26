from discord import Embed, Colour


class ErrorBase:
	def __init__(self, e):
		self.message = e

	async def send(self, channel):
		return await channel.send(
			embed=self.message,
			delete_after=20.0
		)


class MissingArgs(ErrorBase):
	def __init__(self, arg_name):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing Argument",
				description=(
					f"Missing `{arg_name.replace('`', '')}` "
					f"from your command!"
				)
			)
		)
		
		
class InvalidArgs(ErrorBase):
	def __init__(self, arg, proper_type):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Invalid Arguments",
				description=(
					f"`{arg.replace('`', '')}` isn't a valid "
					f"`{proper_type.replace('`', '')}`"
				)
			)
		)


class MissingPermissions(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing Permissions",
				description=
				"You do not have permission to run this command"
			)
		)


class MissingFile(ErrorBase):
	def __init__(self, file_type):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing File",
				description=(
					f"Expected {file_type} to be attached to"
					f" the message"
				)

			)
		)


class NoXP(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(0, 0, 0),
				title="No XP",
				description="This user hasn't collected any XP yet"
			)
		)


class NoAPIConnection(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="No API Connection",
				description=(
					"Unable to connect to the API, please contact a Bot"
					" Owner or Bot Admin"
				)
			)
		)


class APIError(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="API Error",
				description=(
					"Error from API request, please contact a "
					"Bot Admin / Owner"
				)
			)
		)


class NoQOTD(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="No QOTD",
				description="No QOTD left in storage"
			)
		)


class NoQOTDChannel(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="No QOTD Channel Set",
				description=
				"No QOTD channel has been set for this server"
			)
		)


class InvalidQOTDChannel(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Invalid QOTD Channel",
				description=
				"The QOTD channel which was set is now invalid"
			)
		)


class UnchangedOutput(ErrorBase):
	def __init__(self, from_type, to_type):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="No Conversion Necessary",
				description=
				f"`{from_type}` and `{to_type}` are the same"
			)
		)


class PlaceNotFound(ErrorBase):
	def __init__(self, place_name):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Place Not Found",
				description=
				f"There is no place found with the name `{place_name}`"
			)
		)


class InvalidRegEx(ErrorBase):
	def __init__(self, err):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Invalid Regular Expression!",
				description=f"```py\n{err}```"
			)
		)


class MissingImages(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing files",
				description=
				"You didn't attach any images to your command"
			)
		)


class InvalidFile(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Invalid image",
				description="The image must be png format"
			)
		)


class FileReadError(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Error",
				description=(
					"There was an error when attempting to "
					"open the image"
				)
			)
		)


class MissingFilterName(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing filter name",
				description="You must supply a name for the filter"
			)
		)


class ExistingFilterName(ErrorBase):
	def __init__(self, name):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Already existing filter",
				description=(
					f"`{name}` is already an image filter here, please "
					f"choose another name"
				)
			)
		)
		
		
class FetchAvatarError(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Unable to fetch user avatar",
				description="Error while fetching the users avatar"
			)
		)


class CustomCommandError(ErrorBase):
	def __init__(self, err):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Error when creating command",
				description=err
			)
		)


class MissingCommand(ErrorBase):
	def __init__(self, err):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Command not found",
				description=f"No command found called {err}"
			)
		)


class InCooldown(ErrorBase):
	def __init__(self, cooldown):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="This command is on cooldown",
				description=f"You can run this command again "
				f"in {cooldown}",
			)
		)


class GamblingSuspended(ErrorBase):
	def __init__(self):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Gambling suspended",
				description="Your usage of gambling commands has been"
				" temporarily suspended"
			)
		)


class InvalidUser(ErrorBase):
	def __init__(self, u):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="User not found",
				description=f"Could not find user {u}"
			)
		)


class MissingCurrency(ErrorBase):
	def __init__(self, amount):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Missing currency",
				description=(
					f"You don't have enough currency for that, "
					f"you only have {amount}"
				)
			)
		)
		

class NoShopItems(ErrorBase):
	def __init__(self, guild):
		super().__init__(
			Embed(
				type="rich",
				colour=Colour.from_rgb(255, 70, 73),
				title="Shop not setup",
				description=f"{guild} has not items in the shop"
			)
		)
