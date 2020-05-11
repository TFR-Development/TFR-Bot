from urllib.request import urlopen
from urllib.error import URLError
from json import dumps, loads
from json.decoder import JSONDecodeError


class APIBridge:
	def __init__(self, client):
		self.client = client
	
	@staticmethod
	def request(route, **params):
		try:
			# Make a request to the {route} path of the api,
			# with params converted to a serialized string from a
			# python dictionary
			res = urlopen(
				f"http://localhost:8081/{route}",
				data=dumps(params).encode()
				# Encode the serialized string to bytes
			).read().decode()
			# Read the response and decode it to a string (from bytes)

			# Attempt to deserialize the response into python
			# dictionary and return it
			return loads(res)
			
		except (URLError, JSONDecodeError) as e:
			# Exception while making request or while deserializing
			# Log error and return -1 to indicate error
			print(e)
			return -1
