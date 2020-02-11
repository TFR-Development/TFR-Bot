from urllib.request import urlopen
from urllib.error import URLError
from json import dumps, loads


class APIBridge:
	def __init__(self, client):
		self.client = client
	
	@staticmethod
	def request(route, **params):
		try:
			res = loads(urlopen(
				f"http://localhost:8081/{route}",
				data=dumps(params).encode()
			).read().decode())
			
			return res
			
		except URLError as e:
			print(e)
			return -1
