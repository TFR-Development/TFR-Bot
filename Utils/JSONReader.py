class JSONReader:
	def __init__(self, json_file):
		for attr in json_file.keys():
			setattr(self, attr.replace(" ", "_"), json_file[attr])
