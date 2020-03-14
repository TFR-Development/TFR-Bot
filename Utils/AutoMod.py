from re import match
from time import time as epoch


def highest_role(roles):
	return sorted(roles, key=lambda r: r.position)[-1]


def compare_highest_role(member_1, member_2):
	return highest_role(
		member_1.roles
	).position > highest_role(member_2.roles).position


def permission_check(permission):
	def outer_inner(f):
		def inner(*args, **kwargs):
			me = args[1].guild.me
			if permission.lower() != "accept":
				if not getattr(me.guild_permissions, permission):
					return False
			if compare_highest_role(me, args[1]):
				return f(*args, **kwargs)
			return False
		return inner
	
	return outer_inner


class AutoModHandler:
	def __init__(self, client):
		self.client = client
		
		self.db = self.client.DataBaseManager
		
		self.filter_actions = {
			"ban": self.ban_user,
			"kick": self.kick_user,
			"softban": self.softban_user,
			"strike": self.strike_user,
			"delete": lambda *_: None
		}
		
	def gen_perms(self, msg):
		return self.client.CalculatePermissions(
			self.client,
			msg.author,
			msg.guild
		).calculate()
		
	async def auto_mod_filter(self, message):
		if self.gen_perms(message) > 0:
			return False
		
		filters = self.db.get_filters(
			guild=str(message.guild.id),
			channel=str(message.channel.id)
		)
		
		if not filters:
			return False
		
		for f in filters:
			res = match(f["filter"], message.content)
			
			if not res:
				continue
				
			if f["action"] not in self.filter_actions.keys():
				continue
				
			await message.delete()
			
			successful_punish = await self.filter_actions[f["action"]](
				message.author,
				f["reason"]
			)
			
			if successful_punish:
				self.db.insert_punishment(
					action=f["action"],
					user=str(message.author.id),
					guild=str(message.guild.id),
					reason=f["reason"],
					time=epoch(),
					staff=str(self.client.user.id)
				)
				return True
			
	async def image_filter(self, url, member, reason):
		banned = self.db.get_img_filters(member.guild.id)
		
		banned_reduced = [
			{
				"Avatar": n["img"],
				"Ignore_colour": n["ignore_colour"]
			} for n in banned
		]
		
		res = self.client.API.request(
			route="imagefilter",
			avatar=url,
			banned=banned_reduced,
		)
		
		if res == -1:
			return False
		
		loc = res.get("Result", -1)
		
		if loc == -1:
			return False
		
		matched = banned[loc]
		
		if matched["action"] not in self.filter_actions.keys():
			# Shouldn't be able to happen, check for the sake of it
			# though
			return False
		
		success = await self.filter_actions[matched["action"]](
			member, reason
		)
		
		if success:
			self.db.insert_punish(
				action=matched["action"],
				user=str(member.id),
				guild=str(member.guild.id),
				reason=matched["reason"],
				time=epoch(),
				staff=str(self.client.user.id)
			)
			return True
			
	@permission_check("ban_members")
	async def ban_user(self, member, reason):
		await member.guild.ban(
			user=member, reason=reason,
			delete_message_days=0
		)
		
		return True
	
	@permission_check("kick_members")
	async def kick_user(self, member, reason):
		await member.kick(reason=reason)
		return True
		
	@permission_check("ban_members")
	async def softban_user(self, member, reason):
		guild = member.guild
		
		await guild.ban(
			user=member, reason=reason,
			delete_message_days=1
		)
		await guild.unban(member, "Softban")
		return True

	@permission_check("accept")
	async def strike_user(self, _, __):
		# Values used by decorator
		return True
