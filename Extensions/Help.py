from discord import Embed, Colour
from asyncio import TimeoutError as AsyncioTimeoutError


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
		
		self.accepted_reactions = {
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
		
		self.previous, self.next, self.exit = self.reactions = \
			self.accepted_reactions.keys()
		
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
				colour=Colour.from_rgb(106, 106, 106),
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
		
		sorted_categories = {}
		
		sorted_keys = sorted(categories.keys())
		for key in sorted_keys:
			sorted_categories[key] = categories[key]
			
		categories = sorted_categories

		menu_pages = []
		
		for cat in categories:
			menu_pages.append(
				{
					"name": cat,
					"value": "\n".join(
						[
							"**{0}{1}**\n{2}\n".format(
								command.prefix,
								getattr(c, "usage", c.name),
								c.description
							) for c in sorted(
								categories[cat],
								key=lambda n: n.name
							)
						]
					)
				}
			)
			
		help_embed = Embed(
			type="rich",
			colour=Colour.from_rgb(106, 106, 106),
			title=f"{self.client.user.name} Help"
		)
		
		msg = await message.channel.send(
			embed=help_embed
		)
		
		page = 0
		length = len(menu_pages)
		
		help_embed.description = menu_pages[page]["value"]
		footer = []
		
		if page > 0:
			footer.append(
				self.previous + menu_pages[page - 1]["name"]
			)
		
		if page < length - 1:
			footer.append(
				menu_pages[page + 1]["name"] + self.next
			)
		
		help_embed.set_footer(
			text="  |  ".join(footer).upper() or None
		)
		
		help_embed.title = "Help: " + menu_pages[page]["name"].title()
		
		await msg.edit(embed=help_embed)
		
		while True:
			try:
				for reaction_check in self.accepted_reactions:
					check = self.accepted_reactions[reaction_check][
						"check"
					]
					
					keep = check(page, length)
					
					reacted = self.get(
						msg.reactions,
						reaction_check,
						lambda react: str(react.emoji)
					)
					
					if keep and reacted and reacted.me:
						continue
						
					if keep and not (reacted and reacted.me):
						await msg.add_reaction(reaction_check)
						
					if not keep and (reacted and reacted.me):
						await msg.remove_reaction(
							reaction_check,
							msg.guild.me
						)
					
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				
				reaction, user = await self.client.wait_for(
					"reaction_add",
					check=lambda r, u: (
							str(r.emoji) in self.reactions and
							r.me and u.id == message.author.id
							and r.message.id == msg.id
					)
				)
				
				if not reaction:
					raise AsyncioTimeoutError()
				
				await reaction.remove(user)
				
				if str(reaction.emoji) == self.exit:
					raise AsyncioTimeoutError()
				
				if str(reaction.emoji) == self.next:
					page += 1
					
				if str(reaction.emoji) == self.previous:
					page -= 1
					
				if page < 0:
					page = 0
					
				if page == length:
					page -= 1
				
				help_embed.description = menu_pages[page]["value"]
				footer = []
				
				if page > 0:
					footer.append(
						self.previous + menu_pages[page - 1]["name"]
					)
				
				if page < length - 1:
					footer.append(
						menu_pages[page + 1]["name"] + self.next
					)
				
				help_embed.set_footer(
					text="  |  ".join(footer).upper() or None
				)
		
				help_embed.title = "Help: " + menu_pages[page][
					"name"
				].title()

				await msg.edit(
					embed=help_embed
				)
				
			except AsyncioTimeoutError:
				await msg.delete()
				return
				
	@staticmethod
	def get(iterable, key, func=lambda n: n):
		for i in iterable:
			if func(i) == key:
				return i
		return None


def setup(client):
	client.CommandHandler.add_command(Help(client))
