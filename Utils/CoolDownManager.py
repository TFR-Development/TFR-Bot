from time import time as epoch


class CoolDownManager:
	def __init__(self):
		self.cooldowns = {}
		
	def clean(self):
		now = epoch()
		for cooldown_name, cooldown in self.cooldowns.values():
			for key, time in cooldown.items():
				if time <= now:
					del self.cooldowns[cooldown_name][key]
	
	def add(self, group, key, time):
		if group not in self.cooldowns:
			self.cooldowns[group] = {}
		
		self.cooldowns[group][key] = time
		
	def in_cooldown(self, group, key):
		if group not in self.cooldowns:
			return False
		
		if key not in self.cooldowns[group]:
			return False
			
		if self.cooldowns[group][key] >= epoch():
			return True
		
		del self.cooldowns[group][key]
		return False

	def get_cooldown(self, group, key):
		if not self.in_cooldown(group, key):
			return 0
		
		return self.cooldowns[group][key] - epoch()
