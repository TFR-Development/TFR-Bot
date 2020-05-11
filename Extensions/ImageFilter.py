from discord import HTTPException, Forbidden, NotFound, File
from base64 import b64encode, b64decode
from discord import Embed, Colour
from io import BytesIO


class AddFilter:
	
	punishments = [
		"ban",
		"softban",
		"kick",
	]

	def __init__(self, client):
		self.client = client
		
		self.name = "addimagefilter"
		self.aliases = ["aif"]
		self.perm_level = 4
		self.description = (
			"Adds an image which will be filtered, tested when a new"
			" member joins"
		)
		self.category = "Administration"
		self.usage = (
			"addimagefilter <attach image> <filter name> <reason> "
			"<punishment> [ignore colours true|false]"
		)
		
	async def run(self, _, message, *args):
		# API request to parse quote wrapped args
		args = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if args == -1:
			# Error connecting to API
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		args = args.get("Message", [])
		
		if len(args) < 1:
			# No args provided
			return await self.client.Errors.MissingArgs(
				"filter name"
			).send(message.channel)

		filter_name = args[0]
		
		if len(filter_name) == 0:
			# Empty name
			return await self.client.Errors.MissingFilterName().send(
				message.channel
			)

		if self.client.DataBaseManager.img_filter_exists(
				message.guild.id, filter_name):
			# A filter with this name already exists, allowing
			# multiple filters with the same name would cause
			# complications
			return await self.client.Errors.ExistingFilterName(
				filter_name
			).send(message.channel)

		if len(args) < 2:
			# Missing a reason
			return await self.client.Errors.MissingArgs("reason").send(
				message.channel
			)

		reason = args[1]

		mode = False
		# Default compare colours (ignore = not mode)

		if len(args) < 3:
			# Missing a punishment argument
			return await self.client.Errors.MissingArgs(
				"punishment"
			).send(message.channel)

		if args[2].lower() not in self.punishments:
			# Invalid punishment supplied
			return await self.client.InvalidArgs(
				args[2], "punishment"
			).send(message.channel)

		if len(args) >= 4:
			# Mode is an optional arg
			
			mode = args[3].lower()

			if mode in ["true", "yes", "y", "t"]:
				# basic truthiness test
				mode = True
			else:
				mode = False			

		if len(message.attachments) == 0:
			# No image attached
			return await self.client.Errors.MissingImages().send(
				message.channel
			)

		file = message.attachments[0]

		if not file.filename.lower().endswith(".png"):
			# Currently only accepts *.png files
			return await self.client.Errors.InvalidFile().send(
				message.channel
			)

		try:
			# Attempt to read image attachment
			raw_img = await file.read()
		except (HTTPException, Forbidden, NotFound):
			return await self.client.Errors.FileReadError().send(
				message.channel
			)

		b64_encoded_img = b64encode(raw_img).decode()
		# Encode the raw image data into base64 and then decode from 
		# raw bytes to a string
		
		# Insert image filter into db
		self.client.DataBaseManager.insert_img_filter(
			str(message.guild.id),
			b64_encoded_img,
			mode,
			reason,
			filter_name,
			args[2]
		)

		# Success receipt
		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Success!",
				colour=Colour.from_rgb(111, 255, 235),
				description="Added image filter successfully"
			)
		)


class ListFilters:
	def __init__(self, client):
		self.client = client

		self.name = "listimagefilters"
		self.aliases = ["lif"]
		self.perm_level = 4
		self.description = "Lists image filters"
		self.category = "Administration"
		self.usage = "listimagefilters"

	async def run(self, _, message, *__):
		# Retrieve all image filters for the current guild
		filters = self.client.DataBaseManager.get_img_filters(
			str(message.guild.id)
		)

		if len(filters) == 0:
			# The guild has no image filters set
			return await message.channel.send(
				embed=Embed(
					type="rich",
					title="No image filters set",
					colour=Colour.from_rgb(111, 255, 235)
				),
				delete_after=30.0
			)

		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Image filters",
				colour=Colour.from_rgb(111, 255, 235),
				description="\n".join(
					(
						f"`{n['name']}` -> `{n['id']}` -> Ignore "
						f"Colours: {n['ignore_colour']}"
						for n in filters
					)
					# basic formatting which will result in this 
					# appearance "`name` -> `id` -> Ignore Colours: 
					# `ignore_colour`" with each filter on its own 
					# new line
				)
			)
		)


class GetFilter:
	def __init__(self, client):
		self.client = client

		self.name = "getimagefilter"
		self.aliases = ["gif"]
		self.perm_level = 4
		self.description = "Views a specific image filter"
		self.category = "Administration"
		self.usage = "getimagefilter <id>"

	async def run(self, _, message, *args):
		if len(args) == 0:
			# No args
			return self.client.Errors.MissingArgs("id").send(
				message.channel
			)

		f = self.client.DataBaseManager.get_img_filter(
			str(message.guild.id),
			args[0]
		)

		if not f:
			# No filter found matching ID and guild
			return await self.client.Errors.InvalidArgs(
				args[0],
				"ID"
			).send(message.channel)
		
		f = f[0]
		# f is a list, but should only contain a single element, 
		# select that

		# Create a BytesIO Buffer object to hold the image
		buffer = BytesIO()

		buffer.write(b64decode(f["img"]))
		# Write the image to the buffer, decoding from base64

		# Seek to the beginning of the buffer
		buffer.seek(0)
		
		# Send image
		
		text = (
			("Ignore Colours", str(f["ignore_colour"]).title(),),
			("Name", f["name"],),
			("Punishment", f["action"],),
			("Reason", f["reason"],)
		)
		
		await message.channel.send(
			"\n".join([": ".join(n for n in text)]),
			file=File(
				fp=buffer,
				filename="filter.png"
			)
		)


def setup(client):
	client.CommandHandler.add_commands(
		AddFilter(client),
		ListFilters(client),
		GetFilter(client)
	)
