from string import ascii_lowercase, ascii_uppercase
from re import escape, compile as re_compile


class TimeParser:
	def __init__(
			self,
			to_parse,
			return_modified=True,
			case_insensitive_markers=True,
			remove_start=False
		):
		
		if not isinstance(to_parse, str):
			raise TypeError("The object to parse must be a string!")
		
		self.to_parse = to_parse
		self.return_modified = return_modified
		self.remove_start = remove_start
		# Only remove the time if it is the first word
		allowed_chars = [
			# Please do not modify this!
			# The program will likely break if you do so
			"y",
			"w",
			"d",
			"h",
			"m",
			"s",
			*[str(x) for x in range(0, 9)]
		]
		temp = []
		self.allowed_chars = allowed_chars
		if case_insensitive_markers:
			for char in allowed_chars:
				if char in (ascii_lowercase + ascii_uppercase):
					temp.append(char.lower())
					temp.append(char.upper())
				else:
					temp.append(char)
			self.allowed_chars = list({*temp})
			# Convert it from a set
			# to a list to remove duplicates
		self.conversion = {
			"y": 31449600000,  # year to millisecond multiplier,
			# defined as 52 weeks
			"w": 604800000,  # week to millisecond multiplier
			"d": 86400000,  # day to millisecond multiplier
			"h": 3600000,  # hour to millisecond multiplier
			"m": 60000,  # minute to millisecond multiplier
			"s": 1000
		}
	
	def parse(self):
		to_parse_split = self.to_parse.split(" ")
		valid = [word for word in to_parse_split if self.is_valid(
			word,
			self.allowed_chars
		)]
		if not valid:
			return None, self.to_parse
		
		for possible in valid:
			previous = ""
			total_time = 0
			for letter in possible:
				if letter.isdigit():
					previous += letter
				else:
					modifier = int(previous)
					modifier *= self.conversion[letter.lower()]
					#  Do it as three lines to make pep 8 happy
					total_time += modifier
					previous = ""  # reset
			if previous != "":
				# Only use this as a time if the whole word is a time,
				# won't accept things like  3d1 but will accept 3d2h
				continue
			if total_time > 0:
				if self.return_modified:
					if self.remove_start:
						modifier_regex = re_compile(
							r"^" + escape(possible) + r"(\b|\s|$)"
						)
					else:
						modifier_regex = re_compile(
							r"(^|\b|\s)" + escape(
								possible
							) + r"(\b|\s|$)"
						)
					return total_time, modifier_regex.sub(
						"",
						self.to_parse,
						1
					).strip()
				else:
					return total_time, self.to_parse
		return None, self.to_parse
	
	def parse_to_string(self):
		ms, original_string = self.parse()
		if not ms:
			return None
		
		times = ["year", "week", "day", "hour", "minute", "second"]
		time_string = ""
		for time in times:
			multiplier = self.conversion[time[0]]
			current_time = ms // multiplier
			ms = ms % multiplier
			
			if current_time != 0:
				plural = "s " if current_time > 1 else " "
				time_string += str(current_time) + " "
				time_string += time.title() + plural
		
		return time_string.strip()
	
	@staticmethod
	def is_valid(test, valid):
		for letter in test:
			if letter not in valid:
				return False
		return True

