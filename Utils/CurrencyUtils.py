class CurrencyGuild:
	def __init__(self, client, guild):
		self._guild = guild
		
		self.client = client
	
	def __getattr__(self, item):
		# Can't use hasattr as it causes a recursion error
		try:
			return self.__getattribute__(item)
		except AttributeError:
			pass
		
		try:
			return self._guild.__getattribute__(item)
		except AttributeError:
			pass
		
		raise AttributeError(
			f"class {self.__class__.__name__} has no attribute `{item}`"
		)
	
	@property
	def all_currency(self):
		return sorted(
			self.client.data_base_manager.get_guild_currency(
				str(self.id)
			),
			key=lambda m: m["cur"],
			reverse=True
		)
	
	def get_member(self, user_id):
		if user_id in self._members.keys():
			return CurrencyMember(
				self.client,
				self._members[user_id]
			)
		
		return None

	@property
	def members(self):
		return [
			CurrencyMember(self.client, m) for m in self._guild.members
		]


class CurrencyMember:
	def __init__(self, client, member):
		self.client = client
		self._guild = member.guild
		self._member = member
	
	def __getattr__(self, item):
		# Can't use hasattr as it causes a recursion error
		try:
			return self.__getattribute__(item)
		except AttributeError:
			pass
		
		try:
			return self._member.__getattribute__(item)
		except AttributeError:
			pass
		
		raise AttributeError(
			f"class {self.__class__.__name__} has no attribute `{item}`"
		)
	
	@property
	def cur(self):
		return self.client.data_base_manager.get_currency(
			str(self._guild.id),
			str(self.id)
		).get("cur", 0)
	
	@cur.setter
	def cur(self, amount):
		self.client.data_base_manager.update_member_cur(
			str(self._guild.id),
			str(self.id),
			amount
		)
	
	@property
	def guild(self):
		return CurrencyGuild(self._guild)
	
	@property
	def is_gambling_suspended(self):
		return self.client.data_base_manager.is_gambling_suspended(
			str(self._guild.id),
			str(self.id)
		)


class CurrencyMessage:
	
	def __init__(self, client, message):
		self._message = message
		
		self.client = client
	
		self.mentions = [
			CurrencyMember(client, m) for m in message.mentions
		]
	
	def __getattr__(self, item):
		# Can't use hasattr as it causes a recursion error
		try:
			return self.__getattribute__(item)
		except AttributeError:
			pass
		
		try:
			return self._message.__getattribute__(item)
		except AttributeError:
			pass
		
		raise AttributeError(
			f"class {self.__class__.__name__} has no attribute `{item}`"
		)
	
	@property
	def guild(self):
		return CurrencyGuild(self.client, self._message.guild)
	
	@property
	def author(self):
		return CurrencyMember(self.client, self._message.author)