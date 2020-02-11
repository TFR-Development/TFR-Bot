from discord import Embed, Colour


class Help:
	def __init__(self, client):
		self.client = client
		
		self.name = "help"
		self.aliases = [
			"h"
		]
		self.perm_level = 0
		self.description = "Shows a command list"
		self.category = "Miscellaneous"
		self.usage = "help [command]"
		
	async def run(self, command, message, *args):
		if args:
			cmd = self.client.CommandHandler.get_command(args[0])

			if not cmd:
				return await self.client.Errors.InvalidArgs(
					args[0],
					"command"
				).send(message.channel)
			
			usage = cmd.usage if hasattr(cmd, "usage") else cmd.name
			
			permission_level = (
				"Permission: " +
				self.client.CalculatePermissions().as_string(
					cmd.perm_level
				) + f" ({cmd.perm_level})"
			)
			
			aliases = ", ".join(
				[f"`{alias}`" for alias in getattr(cmd, "aliases", [])]
			) or "None"
			
			plural = len(getattr(cmd, "aliases", [])) != 1
			
			embed = Embed(
				type="rich",
				colour=Colour.from_rgb(0, 0, 200),
				title=f"{command.prefix}{usage}",
				description=
				f"**Description**: {cmd.description}\n**Alia"
				f"s{'es' if plural else ''}**: {aliases}",
			)
			
			embed.set_footer(text=permission_level)

			return await message.channel.send(embed=embed)
		
		categories = {}
		
		commands = [
			cmd for cmd in self.client.CommandHandler.commands
			if cmd.perm_level <= command.author_perm_level
		]
		
		for cmd in commands:
			if cmd.category.lower() in categories.keys():
				categories[cmd.category.lower()].append(cmd)
			else:
				categories[cmd.category.lower()] = [cmd]

		help_embed = Embed(
			type="rich",
			colour=Colour.from_rgb(106, 106, 106),
			title=f"{self.client.user.name} help"
		)
		
		sorted_categories = {}
		
		sorted_keys = sorted(categories.keys())
		for key in sorted_keys:
			sorted_categories[key] = categories[key]
			
		categories = sorted_categories
		for cat in categories:
			help_embed.add_field(
				name=cat.upper(),
				value="\n".join([
					"**{0}{1}**\n{2}\n".format(
						command.prefix,
						cmd.usage if hasattr(cmd, "usage") else
						cmd.name,
						cmd.description
					) for cmd in sorted(
						categories[cat],
						key=lambda c: c.name
					)
				]),
				inline=False
			)
			
		return await message.channel.send(embed=help_embed)
	

def setup(client):
	client.CommandHandler.add_command(Help(client))
