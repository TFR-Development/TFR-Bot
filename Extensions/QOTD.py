from discord import Embed, Colour
from random import choice
from asyncio import TimeoutError as AsyncioTimeout
from datetime import datetime


def format_qotd(question, thought, fact):
	return f"**__Question__**\n{question}\n\n**__Thought__**\n" \
			f"{thought}\n\n**__Fact__**\n{fact}"


class QOTDAdd:
	def __init__(self, client):
		self.client = client
		
		self.name = "addqotd"
		self.aliases = [
			"qotdadd",
			"qadd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Adds a QOTD to storage"
		self.usage = "qotdadd \"<question>\" \"<thought>\" \"<fact>\""
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs(
				"question"
			).send(message.channel)
		
		args = self.client.API.request(
			route="argparser",
			Message=" ".join(args)
		).get("Message", [])
		
		if args == -1:
			return await self.client.Errors.NoAPIConnection().send(
				message.channel
			)
		
		if len(args) < 1:
			return await self.client.Errors.MissingArgs(
				"question"
			).send(
				message.channel
			)
		
		if len(args) < 2:
			return await self.client.Errors.MissingArgs(
				"thought"
			).send(
				message.channel
			)
		
		if len(args) < 3:
			return await self.client.Errors.MissingArgs(
				"fact"
			).send(
				message.channel
			)
		
		question, thought, fact, *_ = args

		self.client.DataBaseManager.add_qotd(
			question,
			thought,
			fact,
			message.guild.id,
			message.author.id
		)

		await message.channel.send(
			embed=Embed(
				type="rich",
				title="QOTD Success!",
				description=(
					f"Preview:\n\n"
					f"{format_qotd(question, thought, fact)}"
				),
				colour=Colour.from_rgb(180, 111, 255)
			),
			delete_after=40.0
		)
	

class SendQOTD:
	def __init__(self, client):
		self.client = client
		
		self.name = "sendqotd"
		self.aliases = [
			"qotdsend",
			"qsend"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Sends a QOTD from storage"
		self.usage = "sendqotd"
		
	async def run(self, _, message, *__):
		all_qotd = self.client.DataBaseManager.get_qotd(
			message.guild.id
		)
		
		if len(all_qotd) == 0:
			return await self.client.Errors.NoQOTD().send(
				message.channel
			)
		
		qotd = choice(all_qotd)
		
		channel = self.client.DataBaseManager.get_qotd_channel(
			message.guild.id
		)
		
		if not channel:
			return await self.client.Errors.NoQOTDChannel().send(
				message.channel
			)
		
		guild_channel = message.guild.get_channel(int(channel))
		
		if not guild_channel:
			return await self.client.Errors.InvalidQOTDChannel().send(
				message.channel
			)
		
		role_mention = self.client.DataBaseManager.get_qotd_role(
			message.guild.id
		)
		
		msg_text, r, mentionable = None, None, None
		
		if role_mention:
			r = message.guild.get_role(int(role_mention))
			
			if r:
				mentionable = r.mentionable
				
				await r.edit(
					mentionable=True
				)
				msg_text = f"<@&{r.id}>"
		
		user = await self.client.fetch_user(int(qotd["author"]))
		
		await guild_channel.send(
			content=msg_text,
			embed=Embed(
				type="rich",
				title="QOTD",
				description=format_qotd(
					qotd["question"],
					qotd["thought"],
					qotd["fact"]
				),
				colour=Colour.from_rgb(180, 111, 255)
			).set_footer(
				text=str(user),
				icon_url=str(user.avatar_url)
			)
			
		)
		
		if msg_text:
			await r.edit(
				mentionable=mentionable
			)
			
		self.client.DataBaseManager.remove_qotd(qotd["id"])
		
		response_channel = self.get_response_channel(message.guild)
		
		if not response_channel:
			return
		
		await response_channel.send(f"```{self.format_date()}```")
		
	@staticmethod
	def get_response_channel(guild):
		for c in guild.channels:
			if c.name == "qotd-response":
				return c
		
	@staticmethod
	def format_date():
		date = datetime.now()
		
		start = date.strftime("%A, %B ")
		
		day = date.strftime("%d")
		
		year = date.strftime(" %Y")
		
		exceptions = {
			"1": "st",
			"2": "nd",
			"3": "rd",
			"21": "st",
			"22": "nd",
			"31": "st"
		}
		
		if day in exceptions.keys():
			return start + day + exceptions[day] + year
		
		return start + day + "th" + year


class SetQOTDChannel:
	def __init__(self, client):
		self.client = client
		
		self.name = "setqotdchannel"
		self.aliases = [
			"qotdch",
			"setqotdch"
		]
		
		self.category = "QOTD"
		self.perm_level = 4
		self.description = \
			"Sets the channel the QOTD message will be sent to"
		self.usage = "setqotdchannel <channel>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs("channel").send(
				message.channel
			)
		
		channel_resolvable = "-".join(args)
		
		channel = self.get_channel(message.guild, channel_resolvable)
	
		if not channel:
			return await self.client.Errors.InvalidArgs(
				channel_resolvable,
				"channel"
			).send(message.channel)
		
		self.client.DataBaseManager.set_qotd_channel(
			message.guild.id,
			channel.id
		)
		
		await message.channel.send(embed=Embed(
			type="rich",
			colour=Colour.from_rgb(111, 255, 235),
			title="Channel Updated!",
			description=f"QOTD will now be sent to <#{channel.id}>"
		))
		
	@staticmethod
	def strip_channel(channel):
		channel = channel.strip()
		if channel.startswith("<#"):
			channel = channel[2:]
		if channel.endswith(">"):
			channel = channel[:-1]
			
		return channel

	def get_channel(self, guild, channel_resolvable):
		channel_id = self.strip_channel(channel_resolvable)
		
		for channel in guild.channels:
			if channel_resolvable == channel.name:
				return channel
			if str(channel.id) == channel_id:
				return channel
		return None


class SetQOTDRole:
	def __init__(self, client):
		self.client = client
		
		self.name = "setqotdrole"
		self.aliases = [
			"qotdr",
			"setqotdr"
		]
		
		self.category = "QOTD"
		self.perm_level = 4
		self.description = \
			"Sets the role which will be @mentioned when a QOTD is sent"
		self.usage = "setqotdrole <role>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs("role").send(
				message.channel
			)
			
		role_resolvable = " ".join(args)
		
		role = self.get_role(message.guild, role_resolvable)
		
		if not role:
			return await self.client.Errors.InvalidArgs(
				role_resolvable, "role"
			)
		
		self.client.DataBaseManager.set_qotd_role(
			message.guild.id,
			role.id
		)
		
		await message.channel.send(embed=Embed(
			type="rich",
			colour=Colour.from_rgb(111, 255, 235),
			title="Role Updated!",
			description=(
				f"<@&{role.id}> will now be mentioned when a "
				f"QOTD is sent"
			)
		))
		
	@staticmethod
	def get_role(guild, role_resolvable):
		for r in guild.roles:
			if role_resolvable in [str(r.id), r.name]:
				return r
			
		return None
	
	
class QOTDList:
	def __init__(self, client):
		self.client = client
		
		self.name = "qotdlist"
		self.aliases = [
			"qotdl",
			"lqotd",
			"listqotd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Lists all QOTD currently stored"
		self.usage = "qotdlist"
		self.accepted_reactions = {
			"➡": {
				"check": lambda page, length: page < length - 1
			},
			"⬅": {
				"check": lambda page, _: page != 0
			},
			"❌": {
				"check": lambda *_: True
			}
		}

	async def run(self, _, message, *__):
		all_qotd = self.client.DataBaseManager.get_all_qotd(
			message.guild.id
		)
		
		if len(all_qotd) == 0:
			return await self.client.Errors.NoQOTD().send(
				message.channel
			)
		
		formatted_qotd = []
		
		user_cache = {}
		
		for qotd in all_qotd:
			qotd_iter_user = int(qotd["author"])
			if qotd_iter_user not in user_cache.keys():
				fetched = await self.client.fetch_user(qotd_iter_user)
				
				user_cache[qotd_iter_user] = {
					"avatar": str(fetched.avatar_url),
					"tag": str(fetched)
				}
			
			formatted_qotd.append(
				{
					"msg": format_qotd(
						qotd["question"],
						qotd["thought"],
						qotd["fact"]
					),
					"user": qotd["author"],
					"id": qotd["id"],
					"avatar": user_cache[qotd_iter_user]["avatar"],
					"tag": user_cache[qotd_iter_user]["tag"]
				}
			)
			
		msg = await message.channel.send(embed=Embed(
			type="rich",
			colour=Colour.from_rgb(111, 255, 235),
			title="QOTD",
			description="Loading"
		))
		
		page = 0
		total_len = len(all_qotd)
		
		await msg.edit(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(111, 255, 235),
				title="QOTD",
				description=formatted_qotd[page]["msg"],
			).set_footer(
				text=(
					f"{formatted_qotd[page]['tag']} | Page "
					f"{page + 1} of {len(formatted_qotd)}"
				),
				icon_url=formatted_qotd[page]["avatar"]
			).set_author(
				name=formatted_qotd[page]['id']
			)
		)
		
		while True:
			try:
				for r in self.accepted_reactions.keys():
					keep = self.accepted_reactions[r]["check"](
						page,
						total_len
					)

					reacted = self.get(
						msg.reactions,
						r,
						lambda react: react.emoji
					)
					
					if keep and reacted and reacted.me:
						continue
					if keep:
						await msg.add_reaction(r)
						continue
						
					if (not keep) and reacted and reacted.me:
						await msg.remove_reaction(r, message.guild.me)
				
				msg = self.get(
					self.client.cached_messages,
					msg.id,
					lambda m: m.id
				)
				
				reaction, user = await self.client.wait_for(
					"reaction_add",
					timeout=300,
					check=lambda react_check, u: (
						react_check.me and u.id == message.author.id
						and react_check.message.id == msg.id
					)
				)
				
				await reaction.remove(user)
				
				if not reaction:
					return await msg.delete()
				
				if reaction and reaction.emoji == "❌":
					return await msg.delete()
				
				if reaction.emoji == "➡":
					page += 1
					
				else:
					page -= 1
					
				if page < 0:
					page = 0
				
				if page == len(formatted_qotd):
					page = len(formatted_qotd) - 1
				
				await msg.edit(
					embed=Embed(
						type="rich",
						colour=Colour.from_rgb(111, 255, 235),
						title="QOTD",
						description=formatted_qotd[page]["msg"],
					).set_footer(
						text=(
							f"{formatted_qotd[page]['tag']} | Page "
							f"{page + 1} of {len(formatted_qotd)}"
						),
						icon_url=formatted_qotd[page]["avatar"]
						).set_author(
						name=formatted_qotd[page]['id']
					)
				)
			
			except AsyncioTimeout:
				return await msg.delete()
	
	@staticmethod
	def get(reactions, key, func=lambda n: n):
		for i in reactions:
			if func(i) == key:
				return i


class RemoveQOTD:
	def __init__(self, client):
		self.client = client
		
		self.name = "qotdremove"
		self.aliases = [
			"qotdrm",
			"rmqotd",
			"removeqotd"
		]
		
		self.category = "QOTD"
		self.perm_level = 2
		self.description = "Removes a QOTD from storage"
		self.usage = "qotdremove <id>"
		
	async def run(self, _, message, *args):
		if len(args) == 0:
			return await self.client.Errors.MissingArgs("QOTD ID").send(
				message.channel
			)

		valid = self.client.DataBaseManager.qotd_exists(
			args[0],
			message.guild.id
		)

		if not valid:
			return await self.client.Errors.InvalidArgs("QOTD ID").send(
				message.channel
			)
		
		self.client.DataBaseManager.remove_qotd(args[0])
		
		await message.channel.send(embed=Embed(
			type="rich",
			colour=Colour.from_rgb(180, 111, 255),
			title="Success!",
			description="QOTD deleted successfully"
		))
		

def setup(client):
	client.CommandHandler.add_commands(
		QOTDAdd(client),
		SendQOTD(client),
		SetQOTDChannel(client),
		SetQOTDRole(client),
		QOTDList(client),
		RemoveQOTD(client),
	)
