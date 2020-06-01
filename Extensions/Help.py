from discord import Embed, Colour
from asyncio import TimeoutError as AsyncioTimeoutError
from Utils.CustomCommand import CustomCommand


class Help:
	
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
		
		self.previous, self.next, self.exit = self.reactions = \
			self.accepted_reactions.keys()
		
	async def run(self, command, message, *args):
		if args:
			# If any arguments were supplied, search for a command
			# with that name
			cmd = self.client.command_handler.get_command(args[0])

			if not cmd:
				# No command with that name was found
				return await self.client.errors.InvalidArgs(
					args[0],
					"command"
				).send(message.channel)
			
			usage = cmd.usage if hasattr(cmd, "usage") else cmd.name
			# The command usage, if the cmd doesn't have a usage
			# field, default to the name
			
			permission_level = (
				"Permission: " +
				self.client.calculate_permissions().as_string(
					cmd.perm_level
				) + f" ({cmd.perm_level})"
			)
			# Create the permission info for this command
			
			aliases = ", ".join(
				[f"`{alias}`" for alias in getattr(cmd, "aliases", [])]
			) or "None"
			# If the command has aliases, wrap each one in a
			# codeblock and separate with a comma
			
			plural = len(getattr(cmd, "aliases", [])) != 1
			# Whether or not to treat the aliases as a plural
			
			embed = Embed(
				type="rich",
				colour=Colour.from_rgb(106, 106, 106),
				title=f"{command.prefix}{usage}",
				description=(
					f"**Description**: {cmd.description}\n**Alia"
					f"s{'es' if plural else ''}**: {aliases}"
				),
			)
			
			embed.set_footer(text=permission_level)

			return await message.channel.send(embed=embed)
		
		categories = {}
		
		commands = [
			cmd for cmd in self.client.command_handler.commands
			if cmd.perm_level <= command.author_perm_level
		]
		# Filter all commands by those which the message author has
		# permission to use
		
		for cmd in commands:
			# If the commands category has already been added to
			# categories, simply append
			if cmd.category.lower() in categories.keys():
				categories[cmd.category.lower()].append(cmd)
			else:
				# If not, just add the category
				categories[cmd.category.lower()] = [cmd]
		
		sorted_categories = {}
		
		sorted_keys = sorted(categories.keys())
		# Sort the categories into alphabetical order
		for key in sorted_keys:
			sorted_categories[key] = categories[key]
		
		categories = sorted_categories

		menu_pages = []
		
		for cat in categories:
			# Create the individual menu pages
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
		# The message which will hold the menu
		
		page = 0
		length = len(menu_pages)
		
		help_embed.description = menu_pages[page]["value"]
		footer = []
		
		if page > 0:
			# Not the first page, there will be a previous page,
			# so add that to the footer
			footer.append(
				self.previous + menu_pages[page - 1]["name"]
			)
		
		if page < length - 1:
			# Not the end page, there will be another page
			# afterwards, so add to the footer
			footer.append(
				menu_pages[page + 1]["name"] + self.next
			)
		
		# Set the footer to show the next / previous pages
		help_embed.set_footer(
			text="  |  ".join(footer).upper() or None
		)
		
		# Set the title to include the category name
		help_embed.title = "Help: " + menu_pages[page]["name"].title()
		
		await msg.edit(embed=help_embed)
		# Start the menu at page 0
		
		while True:
			# Start the menu loop
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
				
				# Wait for the next reaction_add event on this message
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
				
				# Remove the users reaction
				await reaction.remove(user)
				
				if str(reaction.emoji) == self.exit:
					# If the reaction is a cross, exit the menu
					raise AsyncioTimeoutError()
				
				if str(reaction.emoji) == self.next:
					# Right arrow pressed, increment page
					page += 1
					
				if str(reaction.emoji) == self.previous:
					# Left arrow pressed, decrement page
					page -= 1
					
				if page < 0:
					# Somehow page is a negative vale, set to 0
					page = 0
					
				if page >= length:
					# Page is outside the range of the menu (greater),
					# decrement
					page = length - 1
				
				help_embed.description = menu_pages[page]["value"]
				footer = []
				
				if 0 < page:
					# Not the first page, the previous button should
					# exist
					footer.append(
						self.previous + menu_pages[page - 1]["name"]
					)
				
				if page < length - 1:
					# Not the last page, the next button should also
					# exist
					footer.append(
						menu_pages[page + 1]["name"] + self.next
					)
				
				help_embed.set_footer(
					text="  |  ".join(footer).upper() or None
				)
		
				help_embed.title = "Help: " + menu_pages[page][
					"name"
				].title()
				# Set the title of the embed to the category name

				# Update the menu with the new page
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
	client.command_handler.add_command(Help(client))
