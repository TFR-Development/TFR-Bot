from re import match
from time import time as epoch


def highest_role(roles):
	# Returns a members highest role
	return sorted(roles, key=lambda r: r.position)[-1]


def compare_highest_role(member_1, member_2):
	# Checks if member_1 has a higher role than member_2
	return highest_role(
		member_1.roles
	).position > highest_role(member_2.roles).position


def permission_check(permission):
	# Decorator which ensures bot has sufficient permissions
	def outer_inner(f):
		# f represents the original function
		def inner(*args, **kwargs):
			me = args[1].guild.me

			if permission.lower() != "accept":
				# If the bot doesn't need any permissions i.e. warn
				if not getattr(me.guild_permissions, permission):
					return False, False

			# The role hierarchy allows the bot to take action
			if compare_highest_role(me, args[1]):
				# Run the function and return the result,
				# no permissions should stop it from happening
				# successfully
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
			"delete": self.delete_msg
		}
		
	def gen_perms(self, msg):
		# Checks the permissions (using bots internal permission
		# system) for the message author, allows staff to be bypassed
		return self.client.CalculatePermissions(
			self.client,
			msg.author,
			msg.guild
		).calculate()
		
	async def auto_mod_filter(self, message):
		if self.gen_perms(message) > 0:
			# Ignore messages by staff members
			return False
		
		filters = self.db.get_filters(
			guild=str(message.guild.id),
			channel=str(message.channel.id)
		)
		# Fetch all filters for the guild
		
		if not filters:
			# No filters found, return now
			return False
		
		for f in filters:
			res = match(f["filter"], message.content)
			# Currently only supports Regular Expressions

			if not res:
				# No match
				continue
				
			if f["action"] not in self.filter_actions.keys():
				# Unknown action, how did this happen?
				continue
			
			if message.guild.me.guild_permissions.manage_messages:
				# If the bot has perms to delete the message, do so
				await message.delete()

			successful_punish, create_db = await self.filter_actions[
				f["action"]
			](
				message.author,
				f["reason"]
			)
			# Check if the action was able to be completed
			
			if successful_punish and create_db:
				# If there was no error taking action, log in the db
				self.db.insert_punishment(
					action=f["action"],
					user=str(message.author.id),
					guild=str(message.guild.id),
					reason=f["reason"],
					time=epoch(),
					staff=str(self.client.user.id)
				)
				return True
			
			if successful_punish:
				return True
			
	async def image_filter(self, original, member):
		banned = self.db.get_img_filters(member.guild.id)
		# fetch all the guilds image filters

		# List comprehension to change to the format API expects
		banned_reduced = [
			{
				"Avatar": n["img"],
				"Ignore_colour": n["ignore_colour"]
			} for n in banned
		]
		
		# Make API request
		res = self.client.API.request(
			route="imagefilter",
			avatar=original,
			banned=banned_reduced
		)
	
		print(res)
		
		# Error connecting to API, forced to assume no match
		if res == -1:
			return False

		loc = res.get("Result", -1)
		# If "Result" was not returned as a key, assume -1 (no match)
		
		# API result was no match
		if loc == -1:
			return False
		
		matched = banned[loc]
		
		if matched["action"] not in self.filter_actions.keys():
			# Shouldn't be able to happen, check for the sake of it
			# though
			return False
		
		# Attempt to take action
		success, create_db = await self.filter_actions[
			matched["action"]
		](
			member, matched["reason"]
		)
		
		if success and create_db:
			# If action was successful, log in db
			self.db.insert_punishment(
				action=matched["action"],
				user=str(member.id),
				guild=str(member.guild.id),
				reason=matched["reason"],
				time=epoch(),
				staff=str(self.client.user.id)
			)
			return True
		
		if success:
			return True
			
	@permission_check("ban_members")
	async def ban_user(self, member, reason):
		# Ban member for reason, deleting no messages, given valid
		# permission check
		await member.guild.ban(
			user=member, reason=reason,
			delete_message_days=0
		)
		
		return True, True
	
	@permission_check("kick_members")
	async def kick_user(self, member, reason):
		# Kick member for reason, given valid permission check
		await member.kick(reason=reason)
		return True, True
		
	@permission_check("ban_members")
	async def softban_user(self, member, reason):
		# Softban member for reason (ban and unban but delete 1 day
		# of messages)
		
		guild = member.guild
		# The Guild the member is a part of
		
		await guild.ban(
			user=member, reason=reason,
			delete_message_days=1
		)
		# Ban the member, deleting one day of messages
		
		await guild.unban(member, "Softban")
		# Immediately unban the member
		return True, True

	@permission_check("accept")
	async def strike_user(self, *_):
		# Values used by decorator
		# This function should always be able to run when triggered
		# so it can always log into the db
		return True, True

	@permission_check("accept")
	async def delete_msg(self, *_):
		# Returning False would cause the bot to not insert into the db
		return True, False
