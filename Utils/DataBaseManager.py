from rethinkdb import RethinkDB


class DataBaseManager:
	def __init__(self, client):
		self.r = RethinkDB()
		self.connection = self.r.connect(
			port=28015,
			host="localhost"
		)
		self.client = client
		
	def get_db(self):
		return self.r.db("tfr")
	
	def get_table(self, table):
		t_list = self.get_db().table_list().run(self.connection)
		
		if table in t_list:
			return self.get_db().table(table)
		
		self.get_db().table_create(table).run(self.connection)
		
		return self.get_db().table(table)

	def get_prefix(self, guild):
		guild_conf = list(
			self.get_table("guilds").filter(
				{
					"guild": guild
				}
			).run(self.connection)
		)
		
		if guild_conf:
			guild_conf = guild_conf[0]
			
		if guild_conf and "prefix" in guild_conf.keys():
			return guild_conf["prefix"]
		
		if not guild_conf:
			self.get_table("guilds").insert({
				"guild": guild,
				"prefix": self.client.config["default prefix"]
			}).run(self.connection)
			
		else:
			self.get_table("guilds").get(guild).update({
				"prefix": self.client.config["default prefix"]
			})
			
		return self.client.config["default prefix"]

