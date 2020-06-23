from re import compile, sub
from json import dumps, loads
from discord.errors import HTTPException, Forbidden, InvalidArgument


class CustomCommand:
	
	special_line_regex = compile(r"^\(.+\)$")
	cmd_regex = compile(r"(?i)^\(tfr!(\S+)(\s.+)*\)$")
	permission_level_regex = compile(r"(?i)^\(permission (\d+)\)$")
	blacklist_regex = compile(r"(?i)^\(blacklist ([.+$\d ,]+)\)$")
	whitelist_regex = compile(r"(?i)^\(whitelist ([.+$\d ,]+)\)$")
	channel_regex = compile(r"(?i)^\(channel ([.+$\d a-z]+)\)$")
	dm_regex = compile(
		r"(?i)^\(dm (<?@?!?\d{17,19}>?|.{1,32}#\d{4}|\$\d+)\)$"
	)
	# RegEx's used for determining what each line should do

	# User args RegEx's
	user_arg_regex = compile(r"\$(\d+)")
	# Finds individual users args (greedy)

	range_user_arg_regex = compile(r"\$(\d+)\.{2}(\d+)")
	# Finds user args where a range is used
	
	remaining_user_arg_regex = compile(r"\$(\d+)\+")
	# Find user args where it is (group 1) to the end of args
	
	# RegEx's used for cleaning mentions in a message
	everyone_regex = compile(r"@(everyone|here)")
	
	role_mention_regex = compile(r"<@&(\d{17,19})>")
	
	def __init__(self, client, command, creator_perm):
		self.client = client
		self.creator_perm = creator_perm
		self.name = ""
		self.description = ""
		self.permission_level = 0
		self.command_raw = command
		self.data = {}
	
	def is_valid(self):
		# Empty command, invalid
		if self.command_raw == "":
			return False, "Empty Command"
		
		for line in self.command_raw.split("\n"):
			if self.special_line_regex.match(line):
				# If the line is a "special" line (enclosed in
				# brackets, indicates instruction)
				if self.cmd_regex.match(line):
					match = self.cmd_regex.match(line)
					
					cmd = match.group(1)
					
					command = self.client.command_handler.get_command(
						cmd
					)
					
					if not command:
						return False, f"Unknown command `{cmd}`"
					
					if command.perm_level > self.creator_perm:
						return (
								False,
								f"You don't have permission to "
								f"run command {cmd}"
						)
					
					if getattr(command, "no_customs", False):
						# If that command is blacklisted from being
						# used in a custom command
						return (
							False,
							f"The command {cmd} cannot be used in "
							f"custom commands"
						)
				elif self.permission_level_regex.match(line):
					perm = int(
						self.permission_level_regex
						.match(line).group(1)
					)
					
					valid_perms = [
						p["level"] for p in
						self.client.calculate_permissions.perms
					]
					
					if perm not in valid_perms:
						return (
							False,
							f"Permission level {perm} not recognised"
						)
		return True, ""
	
	def dump(self):
		if self.data != {}:
			return dumps(self.data)
		
		data = {
			"permission": 0,
			"blacklisted": [],
			"whitelisted": [],
			"actions": [],
			"command_raw": self.command_raw
		}
		
		highest_arg = 0
		
		msg_content = ""
		
		for line in self.command_raw.split("\n"):
			
			for match in self.range_user_arg_regex.findall(line):
				max_range = int(match[1])
				
				if max_range > highest_arg:
					highest_arg = max_range
			
			for match in self.user_arg_regex.findall(line):
				if int(match) > highest_arg:
					highest_arg = int(match)
			
			blacklist_match = self.blacklist_regex.match(line)
			if blacklist_match:
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
				
				blacklisted = blacklist_match.group(1).replace(" ", "")
				data["blacklisted"].extend(blacklisted.split(","))
				continue
				
			whitelist_match = self.whitelist_regex.match(line)
			
			if whitelist_match:
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
				
				whitelisted = whitelist_match.group(1).replace(" ", "")
				data["whitelisted"].extend(whitelisted.split(","))
				continue
			
			cmd_match = self.cmd_regex.match(line)
			
			if cmd_match:
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
					
				data["actions"].append(
					{
						"type": "cmd",
						"name": cmd_match.group(1),
						"args": (
							"" if len(cmd_match.groups()) == 2
							else cmd_match.group(2)
						)
					}
				)
				continue
				
			channel_match = self.channel_regex.match(line)
			
			if channel_match:
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
					
				data["actions"].append(
					{
						"type": "channel",
						"args": channel_match.group(1)
					}
				)
				continue
			
			dm_match = self.dm_regex.match(line)
			
			if dm_match:
				
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
				
				data["actions"].append(
					{
						"type": "dm",
						"args": dm_match.group(1)
					}
				)
				continue
			
			permission_match = self.permission_level_regex.match(line)
			
			if permission_match:
				if msg_content != "":
					data["actions"].append(
						{
							"type": "message",
							"args": msg_content
						}
					)
					msg_content = ""
				
				data["permission"] = int(permission_match.group(1))
				continue
			
			if msg_content:
				msg_content += "\n" + line
			else:
				msg_content = line
		
		if msg_content:
			data["actions"].append(
				{
					"type": "message",
					"args": msg_content
				}
			)
		
		data["highest_arg"] = highest_arg
		
		self.data = data
		
		return dumps(data)
	
	@classmethod
	def load(cls, conf, client, name, description):
		self = cls.__new__(cls)

		self.data = loads(conf)
		self.client = client
		self.name = name
		self.description = description
		self.permission_level = self.data.get("permission", 0)
		self.command_raw = self.data.get("command_raw")

		return self

	@property
	def perm_level(self):
		return self.permission_level

	def add_args(self, content, args, member):
		content = self.remaining_user_arg_regex.sub(
			lambda m: " ".join(args[int(m.group(1)) - 1:]),
			content
		)
		
		content = self.range_user_arg_regex.sub(
			lambda m: " ".join(
				args[
					int(m.group(1))-1:
					int(m.group(2)):
					1 if int(m.group(1)) < int(m.group(2)) else -1
				]
			),
			content
		)
		
		return self.user_arg_regex.sub(
			lambda m: args[int(m.group(1)) - 1],
			content
		).replace(
			"{mention}",
			f"<@{member.id}>"
		).replace(
			"{tag}",
			str(member)
		)
	
	@staticmethod
	def get_channel(channels, resolvable):
		for c in channels:
			if resolvable.strip() == f"<#{c.id}>":
				return c
			if resolvable.strip() == str(c.id):
				return c
			if resolvable.strip() == c.name:
				return c
		return None
	
	@staticmethod
	def get_user(members, resolvable):
		for m in members:
			if resolvable.strip() in [f"<@{m.id}>", f"<@!{m.id}"]:
				return m
			if resolvable.strip() == str(m.id):
				return m
			if resolvable.strip() in [m.name, str(m)]:
				return m
		return None
	
	async def run(self, message, msg_args):
		if self.data.get("highest_arg", 1) > len(msg_args):
			return
		
		author_perm_level = self.client.calculate_permissions(
			self.client,
			message.author,
			message.guild
		).calculate()
		
		if author_perm_level < self.permission_level:
			return
		
		for b in self.data["blacklisted"]:
			if str(message.author.id) in b:
				# Handles mentions and direct ID
				# User blacklist
				return

			for r in message.author.roles:
				# Role blacklist
				if str(r.id) == b or r.name == b:
					return

			if message.channel.name == b or str(message.channel.id) == b:
				# Channel blacklist
				return

		if self.data["whitelisted"]:
			# A whitelist system exists
			
			authorised = False
			# Whether or not the message meets the whitelist in
			# at least one way
			for w in self.data["whitelist"]:
				# Check author id, channel id and channel name first
				authorised = (
						str(message.author.id) == w or
						str(message.channel.id) == w or
						message.channel.name == w
				)
				if authorised:
					# If the user authorised, end checks here
					break
					
				for r in message.author.roles:
					# Check all of the users roles (name and id)
					authorised = r.name == w or r.id == w
					if authorised:
						# End checks here
						break
				if authorised:
					# Escape outer loop
					break
			if not authorised:
				# The user failed the whitelist, return now
				return
		
		original_channel = message.channel
		
		channel = message.channel
		# The channel to send messages to
		
		member = message.author
		
		for action in self.data["actions"]:
			args = self.add_args(action["args"], msg_args, member)
			if action["type"] == "channel":
				c = self.get_channel(message.guild.channels, args)
				
				if not c:
					await self.send(
						original_channel,
						self.clean(
							f"Unable to find channel {args}",
							message
						)
					)
					
					channel = original_channel
					continue
					
				channel = c
				
			elif action["type"] == "dm":
				u = self.get_user(message.guild.members, args)
				
				if not u:
					await self.send(
						original_channel,
						self.clean(
							f"Unable to find member {args}",
							message
						)
					)
					return
				
				dm_channel = u.dm_channel
				
				if not dm_channel:
					await u.create_dm()
					dm_channel = u.dm_channel
					
				channel = dm_channel
		
			elif action["type"] == "cmd":
				cmd = action["name"]
				
				command = self.client.command_handler.get_command(cmd)
				
				command.author_perm_level = (
					self.client.calculate_permissions(
						self.client,
						message.author,
						message.guild
					)
				)
				
				if getattr(command, "typing", False):
					async with channel.typing():
						await command.run(
							command, message, *args.split(" ")
						)
				else:
					message.channel = channel
					await command.run(
						command, message, *args.split(" ")
					)
			elif action["type"] == "message":
				args = self.clean(args, message)
				
				if len(args) == 0 or len(args) > 2000:
					continue
					
				await self.send(channel, args)
			
	@staticmethod
	async def send(channel, *args, **kwargs):
		try:
			await channel.send(*args, **kwargs)
		except (HTTPException, Forbidden, InvalidArgument):
			pass

	def clean(self, content, message):
		content = self.role_mention_regex.sub(
			lambda m: (
				(lambda r: f"@{r.name}" if r else m.group(0))(
					message.guild.get_role(
						int(m.group(1))
					)
				)
			),
			content
		)
		
		content = self.everyone_regex.sub(
			lambda m: f"@\u200b{m.group(1)}",
			content
		)
		
		return content
