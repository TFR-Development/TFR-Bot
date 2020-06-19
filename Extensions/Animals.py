from json import loads
from random import choice
from discord import Embed, Colour
from aiohttp import ClientSession


async def fetch_url(url, key, fallback):
	async with ClientSession() as session:
		async with session.get(url) as data:
			if data.status != 200:
				return fallback
			res = loads(await data.read())
			
			return res.get(key) or fallback


class Dog:
	def __init__(self, client):
		self.fallback = [
			"pembroke/n02113023_6801.jpg",
			"retriever-golden/n02099601_5736.jpg",
			"lhasa/n02098413_21411.jpg",
			"spaniel-brittany/n02101388_3673.jpg",
			"mountain-swiss/n02107574_1246.jpg",
			"terrier-norwich/n02094258_905.jpg",
			"leonberg/n02111129_4149.jpg",
			"pug/n02110958_11256.jpg",
			"hound-afghan/n02088094_4501.jpg",
			"pointer-german/n02100236_3612.jpg",
			"setter-english/n02100735_3942.jpg",
			"malamute/n02110063_16612.jpg",
			"terrier-dandie/n02096437_85.jpg",
			"retriever-flatcoated/n02099267_2284.jpg",
			"cairn/n02096177_599.jpg",
			"spaniel-blenheim/n02086646_1514.jpg",
			"spaniel-sussex/n02102480_4415.jpg",
			"malinois/n02105162_6134.jpg",
			"hound-basset/n02088238_8520.jpg",
			"terrier-silky/n02097658_4992.jpg",
			"bullterrier-staffordshire/n02093256_12785.jpg",
			"corgi-cardigan/n02113186_1447.jpg",
			"appenzeller/n02107908_2382.jpg",
			"briard/n02105251_6146.jpg",
			"terrier-norfolk/n02094114_3177.jpg",
			"cattledog-australian/IMG_2432.jpg",
			"appenzeller/n02107908_6019.jpg",
			"spaniel-blenheim/n02086646_669.jpg",
			"terrier-sealyham/n02095889_4159.jpg",
			"retriever-curly/n02099429_198.jpg",
			"poodle-standard/n02113799_961.jpg",
			"terrier-westhighland/n02098286_4708.jpg",
			"spaniel-brittany/n02101388_74.jpg",
			"wolfhound-irish/n02090721_3866.jpg",
			"shihtzu/n02086240_7454.jpg",
			"sheepdog-english/n02105641_5049.jpg",
			"whippet/n02091134_14297.jpg",
			"pitbull/20190710_143021.jpg",
			"collie-border/n02106166_7447.jpg",
			"terrier-fox/n02095314_2472.jpg",
		]
		self.client = client
		self.name = "dog"
		self.aliases = []
		self.perm_level = 0
		self.description = "Shows a random dog image"
		self.category = "Fun"
		self.usage = "dog"

	async def run(self, _, message, *__):
		url = await fetch_url(
			"https://dog.ceo/api/breeds/image/random",
			"message",
			"https://images.dog.ceo/breeds/" + choice(self.fallback)
		)  # Fetches a random dog image url
		
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255)
			).set_image(
				url=url
			)
		)

		
class Fox:
	def __init__(self, client):
		self.fallback = []
		self.client = client
		self.name = "fox"
		self.aliases = []
		self.perm_level = 0
		self.description = "Shows a random fox image"
		self.category = "Fun"
		self.usage = "fox"
		
	@staticmethod
	async def run(_, message, *__):
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255)
			).set_image(
				url=await fetch_url(
					"https://randomfox.ca/floof/",
					"image",
					"http://randomfox.ca/images/14.jpg"
				)
			)
		)


class Panda:
	def __init__(self, client):
		self.fallback = []
		self.client = client
		self.name = "panda"
		self.aliases = [
			"jayden",
			"jayderp"
		]
		self.perm_level = 0
		self.description = "Shows a random panda image"
		self.category = "Fun"
		self.usage = "panda"
	
	@staticmethod
	async def run(_, message, *__):
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255)
			).set_image(
				url=await fetch_url(
					"https://some-random-api.ml/img/panda",
					"link",
					"https://i.imgur.com/nxwRXLj.jpg"
				)
			)
		)


class Bird:
	def __init__(self, client):
		self.fallback = [
			"4bK06.jpg",
			"wU61L.jpg",
			"tfAer.jpg",
			"turdl.gif",
			"YSbJ6.jpg",
			"6boJq.jpg",
			"8Jioa.png",
			"jQdMr.jpg",
			"hCFo5.jpg",
			"KrTpt.jpg",
			"CLegE.jpg",
			"dlr9g.jpg",
			"QKcy3.png",
			"blerb.jpg",
			"scorb.jpg",
			"dlr9g.jpg",
			"MjgBK.jpg",
			"NFXmq.jpg",
			"HlVjd.jpg",
			"BSwVX.jpg",
			"r59mz.png",
			"AcAZE.jpg"
		]
		self.client = client
		self.name = "bird"
		self.aliases = [
			"birb"
		]
		self.perm_level = 0
		self.description = "Shows a random bird image"
		self.category = "Fun"
		self.usage = "bird"

	async def run(self, _, message, *__):
		await message.channel.send(
			embed=Embed(
				type="rich",
				colour=Colour.from_rgb(180, 111, 255)
			).set_image(
				url=
				"https://random.birb.pw/img/" + await fetch_url(
					"http://random.birb.pw/tweet.json/",
					"file",
					choice(self.fallback)
				)
			)
		)


def setup(client):
	client.command_handler.add_commands(
		Dog(client),
		Fox(client),
		Panda(client),
		Bird(client)
	)
