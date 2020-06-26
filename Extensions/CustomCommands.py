from Utils.CustomCommand import CustomCommand
from discord import Colour, Embed
from discord.errors import NotFound, Forbidden
from asyncio import TimeoutError as AsyncioTimeoutError


class CustomCommandAdd:
	def __init__(self, client):
		self.client = client
		self.name = "addcommand"
		
		self.no_customs = True
		# Stop custom commands from creating new custom commands
		
		self.aliases = []
		self.perm_level = 4
		self.description = (
				"Creates a new custom command\nParameters can be found"
				" by running the `cchelp` command"
			)
		self.category = "Administration"
		self.usage = "addcommand <name> <description> <command>"
		self.aliases = [
			"addcc"
		]
	
	async def run(self, cmd, message, *args):
		res = self.client.API.request(
			route="argparser",
			message=" ".join(args)
		)
		
		if res == -1:
			return await self.client.errors.NoAPIConnection().send(
				message.channel
			)
		
		res = res.get("Message", [])
		
		if len(res) < 1:
			return await self.client.errors.MissingArgs("name").send(
				message.channel
			)
		
		if len(res) < 2:
			return await (
				self.client
				.errors
				.MissingArgs("description")
				.send(message.channel)
			)
		
		if len(res) < 3:
			return await (
				self.client
				.errors
				.MissingArgs("command body")
				.send(message.channel)
			)
			
		name, description, body, *_ = res
		
		body = body.strip()
		command = CustomCommand(
			self.client,
			body,
			cmd.author_perm_level
		)
		
		is_valid, reason = command.is_valid()
		
		if not is_valid:
			return await (
				self.client
				.errors
				.CustomCommandError(reason)
				.send(message.channel)
			)
	
		exists = self.client.data_base_manager.custom_command_exists(
			name,
			str(message.guild.id)
		)
		
		if exists:
			return await message.channel.send("Already exists")
	
		self.client.data_base_manager.add_custom_command(
			str(message.guild.id),
			name,
			description,
			command.dump()
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				title="Success",
				description=f"Command {name} created successfully"
			)
		)


class CCHelp:
	
	help_embed = Embed(
		type="rich",
		title="Custom commands",
		colour=Colour.from_rgb(180, 111, 255),
		description="\n\n".join(
			(
				"`(blacklist <id> [id...])` - Blacklists the user / "
				"channel / role from using the command - if multiple "
				"arguments are given they must be separated with a "
				"comma",
				"`(channel <id/name>)` - Sets the response channel for "
				"consequent messages, can be used multiple times",
				"`(dm <id>)` - Sets the response channel for "
				"consequent messages to the given users DM's",
				"`(permission <int>)` - The permission level required "
				"to use the command",
				"`(tfr!<cmd> [args])` - Runs the command `cmd` with "
				"the given args",
				"`(whitelist <id> [id... ])` - The same as blacklist "
				"but whitelists them instead",
				"**User args:**",
				"`$x` - The xth word after the command trigger",
				"`$x+` - From the xth word after the command trigger "
				"to the end of supplied args",
				"`$x..y` - All the args between x and y (both ends "
				"inclusive)",
				"**Message author arguments**",
				"`{mention}` - Replaced with the mention of the user "
				"who ran the command",
				"`{tag}` - Replaced with the tag of the user who ran "
				"the command"
				
			)
		)
	)
	
	def __init__(self, client):
		self.client = client
		self.name = "cchelp"
		self.aliases = []
		self.perm_level = 4
		self.description = (
			"Lists the parameters available in custom commands"
		)
		self.category = "Administration"
		self.usage = "cchelp"
		
	async def run(self, _, message, *__):
		await message.channel.send(
			embed=self.help_embed
		)


class RemoveCommand:
	def __init__(self, client):
		self.client = client
		
		self.name = "removecommand"
		self.aliases = [
			"rmcommand"
			"removecc"
			"rmcc"
		]
		self.perm_level = 4
		self.category = "Administration"
		self.usage = "removecommand <name>"
		self.description = "Removes the custom command with the given "
		"name"
		
	async def run(self, _, message, *args):
		name = " ".join(args)
		
		exists = self.client.data_base_manager.custom_command_exists(
			name,
			str(message.guild.id)
		)
		
		if not exists:
			return await self.client.errors.MissingCommand(name).send(
				message.channel
			)
	
		self.client.data_base_manager.remove_custom(
			name,
			str(message.guild.id)
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				title="Success",
				description=f"Deleted command {name}"
			)
		)
		
		
class CustomCommandList:
	
	accepted_reactions = {
		"◀": {
			"check": lambda page, _: page != 0
		},
		"▶": {
			"check": lambda page, length: page < length - 1
		},
		"❌": {
			"check": lambda *_: True
		}
	}
	
	left, right, cross = reactions = accepted_reactions.keys()
	
	def __init__(self, client):
		self.client = client
		
		self.name = "listcustoms"
		self.aliases = []
		self.perm_level = 0
		self.category = "Administration"
		self.usage = "listcustoms"
		self.description = (
			"Displays all custom commands you have permission to use"
		)
	
	async def run(self, command, message, *_):
		commands = self.client.data_base_manager.get_customs(
			str(message.guild.id)
		)

		if len(commands) == 0:
			return await message.channel.send(
				embed=Embed(
					type="rich",
					colour=Colour.from_rgb(180, 111, 255),
					title="No custom commands set",
					description=
					"This server has no custom commands added"
				)
			)
		
		commands_parsed = [
			CustomCommand.load(
				c["body"],
				self.client,
				c["name"],
				c["description"]
			) for c in commands
		]
		
		commands_parsed = [
			c for c in commands_parsed
			if c.permission_level <= command.author_perm_level
		]
		
		if len(commands_parsed) == 0:
			return await message.channel.send(
				embed=Embed(
					type="rich",
					title="No commands available",
					description="There is no commands available you "
					"have permission to use",
					colour=Colour.from_rgb(180, 111, 255)
				)
			)
		
		commands_parsed.sort(key=lambda c: c.name.lower())
		
		page = 0
		
		length = len(commands_parsed)
		
		c = commands_parsed[page]
		
		msg = await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255),
				title=c.name,
				description=(
					f"Description: `{c.description}`"
					f"```yaml\n{self.escape(c.command_raw)}```"
				)
			).set_footer(
				text=f"Permission level: {c.permission_level}"
			)
		)
		
		while True:
			try:
				for reaction_check in self.accepted_reactions:
					# Iter over all the possible accepted reactions,
					# checking only the correct ones are currently on
					# the message
					check = self.accepted_reactions[reaction_check][
						"check"
					]
					# The lambda function to determine whether or not
					# to keep this reaction
					
					keep = check(page, length)
					
					reacted = self.get(
						msg.reactions,
						reaction_check,
						lambda react: str(react.emoji)
					)
					# Get the MessageReaction
					
					if keep and reacted and reacted.me:
						# The reaction should exist and the bot has
						# reacted already, continue
						continue
					
					if keep and not (reacted and reacted.me):
						# The reaction should exist but the bot
						# hasn't reacted, add reaction
						await msg.add_reaction(reaction_check)
						continue
					
					if not keep and (reacted and reacted.me):
						# The reaction shouldn't exist but the bot as
						# reacted, remove the reaction
						await msg.remove_reaction(
							reaction_check,
							msg.guild.me
						)
					
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				# Update the message from cache
				
				reaction, user = await self.client.wait_for(
					"reaction_add",
					check=lambda r, u: (
						# Check the bot has added this reaction
						# as well so its valid and the correct
						# user reacted
						str(r.emoji) in self.reactions and
						r.me and u.id == message.author.id
						and r.message.id == msg.id
					)
				)
				
				if not (reaction and user):
					raise AsyncioTimeoutError()
				
				await reaction.remove(user)
				
				if str(reaction.emoji) == self.cross:
					# Close the menu here
					raise AsyncioTimeoutError()
				
				if str(reaction.emoji) == self.right:
					# Right arrow pressed, increment page
					page += 1
				
				if str(reaction.emoji) == self.left:
					# Left arrow pressed, decrement page
					page -= 1
					
				if page < 0:
					# Prevent negative page
					page = 0
					
				if page >= length:
					# Prevent page out of limits (upper)
					page = length - 1
					
				c = commands_parsed[page]
				
				await msg.edit(
					embed=Embed(
						type="rich",
						colour=Colour.from_rgb(180, 111, 255),
						title=c.name,
						description=(
							f"Description: {c.description}\n"
							f"```yaml\n{self.escape(c.command_raw)}```"
						)
					).set_footer(
						text=f"Permission level: {c.permission_level}"
					)
				)
				
			except (Forbidden, NotFound, AsyncioTimeoutError):
				break
		
		try:
			await msg.delete()
		except NotFound:
			# Message already deleted
			pass

	@staticmethod
	def get(iterable, key, func=lambda n: n):
		for i in iterable:
			if func(i) == key:
				return i
		return None

	@staticmethod
	def escape(msg):
		return msg.replace("```", r"\```")


def setup(client):
	client.command_handler.add_commands(
		CustomCommandAdd(client),
		RemoveCommand(client),
		CustomCommandList(client),
		CCHelp(client)
	)
