from re import compile as re_compile, error as re_error, match, escape
from discord import Embed, Colour
from asyncio import TimeoutError as AsyncioTimeoutError


class AddChannelFilter:
	
	punishments = [
		"ban",
		"softban",
		"kick",
		"strike",
		"delete"
	]

	def __init__(self, client):
		self.client = client
		
		self.name = "addchannelfilter"
		self.aliases = ["acf"]
		self.perm_level = 4
		self.description = "Adds a channel filter (Regular Expression)"
		self.description += "\nPunishments:" + ", ".join(
			[f"`{i}`" for i in self.punishments]
		)
		self.category = "Administration"
		self.usage = (
			"addchannelfilter \"<punishment>\" \"<filter>\" "
			"\"<channel>\" \"[reason]\""
		)
	
	@staticmethod
	def get_channel(guild, channel_resolvable):
		if match(r"^<#\d{17,19}>", channel_resolvable):
			channel_resolvable = channel_resolvable[2:-1]
			
		if channel_resolvable.isdigit():
			ch = guild.get_channel(int(channel_resolvable))
			
			if ch:
				return ch
		
		for c in guild.channels:
			if c.name.lower() == channel_resolvable.lower():
				return c
			
		return None
	
	async def run(self, _, message, *args):
		args = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		)
		
		if args == -1:
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		args = args.get("Message", [])
		
		if len(args) < 1:
			return await self.client.Errors.MissingArgs(
				"punishment"
			).send(message.channel)
		
		punishment = args[0].lower()
		
		if punishment not in self.punishments:
			return await self.client.Errors.InvalidArgs(
				punishment, "punishment"
			).send(message.channel)
		
		if len(args) < 2:
			return await self.client.Errors.MissingArgs(
				"RegEx filter"
			)
		
		try:
			_ = re_compile(args[1])
		except re_error as e:
			return await self.client.Errors.InvalidRegEx(
				e
			).send(message.channel)
		
		if len(args) < 3:
			return await self.client.Errors.MissingArgs(
				"channel"
			).send(message.channel)
		
		channel = self.get_channel(message.guild, args[2])
		
		if not channel:
			return await self.client.Errors.InvalidArgs(
				args[2], "channel"
			).send(message.channel)
		
		reason = "[AUTOMOD FILTER]" if len(args) == 3 else args[3]
		
		self.client.DataBaseManager.add_text_filter(
			punishment, args[1], channel.id, reason,
			str(message.guild.id)
		)

		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Success!",
				colour=Colour.from_rgb(111, 255, 235)
			).add_field(
				name="Punishment",
				value=punishment,
				inline=True
			).add_field(
				name="RegEx Filter",
				value=escape(args[1]).replace(r"\ ", " "),
				inline=True
			).add_field(
				name="Channel",
				value=f"<#{channel.id}>",
				inline=True
			).add_field(
				name="Reason",
				value=reason,
				inline=True
			),
			delete_after=30.0
		)
		
		
class ListFilters:
	
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
		self.name = "listchannelfilters"
		self.aliases = ["lcf"]
		self.perm_level = 4
		self.description = "Lists all channel filters"
		self.category = "Administration"
		self.usage = "listchannelfilters [#channel]"

		self.left_arrow, self.right_arrow, self.cross = (
			self.accepted_reactions.keys()
		)
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			channel = None
			
		else:
			channel = AddChannelFilter.get_channel(
				message.guild,
				"-".join(args)
			)
			
			if not channel:
				return await self.client.Errors.InvalidArgs(
					"-".join(args),
					"channel"
				)
			
			channel = channel.id
			
		filters = self.client.DataBaseManager.get_filters(
			message.guild.id,
			channel
		)
		
		if not filters:
			affected = f"<#{channel}>" if channel else \
				message.guild.name
			
			return await message.channel.send(
				embed=Embed(
					type="rich",
					title="No Filters",
					description=f"No filters are set in {affected}",
					colour=Colour.from_rgb(255, 70, 73)
				)
			)
	
		msg = await message.channel.send(
			embed=Embed(
				type="rich",
				description="Loading!",
				colour=Colour.from_rgb(111, 255, 235)
			)
		)
		
		page, length = 0, len(filters)
		
		await msg.edit(
			embed=self.gen_embed(filters[page])
		)
		
		while True:
			try:
				for reaction in self.accepted_reactions:
					check = self.accepted_reactions[reaction]["check"]
					
					valid = check(page, length)
					
					reacted = self.get(
						msg.reactions,
						reaction,
						lambda re: str(re.emoji)
					)
					
					if reacted and reacted.me and valid:
						continue
						
					if not (reacted and reacted.me) and valid:
						await msg.add_reaction(reaction)
						continue
						
					if not valid and (reacted and reacted.me):
						await msg.remove_reaction(
							reaction, msg.guild.me
						)
				
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				
				r, u = await self.client.wait_for(
					"reaction_add",
					check=lambda react, user: (
							str(react.emoji) in self.accepted_reactions
							and react.me and
							user.id == message.author.id and
							react.message.id == msg.id
					)
				)
				
				if not (r and u) or (r and str(r.emoji)) == self.cross:
					return await msg.delete()
				
				await msg.remove_reaction(r, u)
				
				if str(r.emoji) == self.right_arrow:
					page += 1
					
				elif str(r.emoji) == self.left_arrow:
					page -= 1
				
				if page < 0:
					page = 0
					
				if page == length:
					page -= 1
				
				await msg.edit(
					embed=self.gen_embed(filters[page])
				)
				
			except AsyncioTimeoutError:
				return await msg.delete()
	
	@staticmethod
	def get(iterable, key, func=lambda n: n):
		for i in iterable:
			if func(i) == key:
				return i
		return None
	
	@staticmethod
	def gen_embed(f):
		embed = Embed(
			type="rich",
			title=f["id"],
			colour=Colour.from_rgb(111, 255, 235)
		).add_field(
			name="Punishment",
			value=f["action"].title(),
			inline=True
		).add_field(
			name="Reason",
			value=f["reason"],
			inline=True
		).add_field(
			name="RegEx Filter",
			value=escape(f["filter"]).replace(
				r"\ ", " "
			),
			inline=True
		)
		
		if "channel" in f.keys():
			embed.add_field(
				name="Channel",
				value=f"<#{f['channel']}>"
			)

		return embed


class RemoveChannelFilter:
	def __init__(self, client):
		self.client = client
		self.name = "removechannelfilter"
		self.aliases = ["rmcf"]
		self.perm_level = 4
		self.description = "Removes a given channel filter"
		self.category = "Administration"
		self.usage = "removechannelfilter <id>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs("id").send(
				message.channel
			)
		
		valid = self.client.DataBaseManager.filter_exists(
			message.guild.id,
			args[0],
			"text"
		)
		
		if not valid:
			return await self.client.Errors.InvalidArgs(
				args[0], "id"
			).send(
				message.channel
			)
		
		(
			self.client.DataBaseManager.get_table("filters")
			.get(args[0])
			.delete()
			.run(self.client.DataBaseManager.connection)
		)
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				title="Success!",
				description="Filter removed successfully.",
				colour=Colour.from_rgb(111, 255, 235)
			),
			delete_after=20.0
		)


def setup(client):
	client.CommandHandler.add_commands(
		AddChannelFilter(client),
		ListFilters(client),
		RemoveChannelFilter(client)
	)
