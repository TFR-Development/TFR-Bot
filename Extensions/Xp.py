from PIL import (
	Image, ImageFont, ImageDraw
)
from io import BytesIO
from discord import (
	File, NotFound, HTTPException
)
from aiohttp import ClientSession
from re import compile as re_compile


class User:
	def __init__(self, user):
		self.user = user
		
	@property
	def tag(self):
		return f"{self.user.name}#{self.user.discriminator}"

	def get(self, item):
		if hasattr(self, item):
			return getattr(self, item)
		
		if hasattr(self.user, item):
			return getattr(self.user, item)
		
		return None


class Xp:
	def __init__(self, client):
		self.client = client
		
		self.name = "xp"
		self.aliases = []
		self.perm_level = 0
		self.description = "Shows XP"
		self.category = "XP"
		self.usage = "xp [user]"
		self.xp = Image.open("xp-template.png")
		self.user_resolvable = re_compile(
			r"^((<@!?)?(\d{17,19})>?|(.{1,32}#\d{4}))$"
		)
		
		self.resolve_mention = re_compile(
			r"(<@!?)?(\d{17,19})(>)?"
		)
		
	async def run(self, _, message, *args):
		xp = self.xp.copy()
		
		xp_saved = xp.load()
		
		modified = BytesIO()
		
		member = User(message.author)
		
		args = list(args)
		
		args = " ".join(args)
		
		if args:
			
			if not self.user_resolvable.match(args):
				return await self.client.Errors.InvalidArgs(
					args,
					"user"
				).send(message.channel)

			user = await self.find_user(args)

			if not user:
				return await self.client.Errors.InvalidArgs(
					args,
					"user"
				).send(message.channel)

			member = User(user)
		
		user_tag = member.tag

		ctx = list(self.client.DataBaseManager.get_table("xp").filter(
			{
				"guild": str(message.guild.id)
			}
		).run(self.client.DataBaseManager.connection))
		
		ctx.sort(key=lambda u: u["xp"], reverse=True)

		rank_lb = None
		total_xp = None
		
		for location, info in enumerate(ctx, 1):
			if info["user"] == str(member.get("id")):
				rank_lb = location
				total_xp = info["xp"]
				break
				
		if not rank_lb:
			return await self.client.Errors.NoXP().send(message.channel)
			
		draw = ImageDraw.Draw(xp)
		font = ImageFont.truetype(
			self.client.config.font_file,
			40 if len(user_tag) <= 15 else 20
		)

		score_font = ImageFont.truetype(
			self.client.config.font_file,
			40
		)
		
		draw.text(
			(140, 80,),
			user_tag,
			(0, 0, 0,),
			font=font
		)
		
		draw.text(
			(100, 220,),
			"Lvl " + str(self.client.DataBaseManager.xp_level(
				message.guild.id,
				member.get("id")
			)),
			(0, 0, 0),
			font=score_font
		)
		
		draw.text(
			(286, 220,),
			f"{rank_lb} / {len(ctx)}",
			(0, 0, 0),
			font=score_font
		)
		
		draw.text(
			(60, 310,),
			f"{total_xp} XP",
			(0, 0, 0),
			font=score_font
		)
		
		avatar_url = str(member.get("avatar_url_as")(
			format="png",
			size=64
		))
		
		async with ClientSession() as session:
			async with session.get(avatar_url) as r_data:
				if r_data.status == 200:
					av_request = await r_data.content.read(-1)
		
		avatar = Image.open(BytesIO(av_request))
		av_loaded = avatar.load()
		
		to_replace = []
		
		for y in range(64, 140):
			for x in range(50, 135):
				if xp_saved[x, y] != (106, 106, 106, 255):
					continue
				
				to_replace.append([x, y])
		
		left_most = sorted(to_replace, key=lambda k: k[0])[0][0]
		up_most = sorted(to_replace, key=lambda k: k[1])[0][1]
		
		for pixel in to_replace:
			xp_saved[
				pixel[0],
				pixel[1]
			] = av_loaded[
				pixel[0] - left_most,
				pixel[1] - up_most
			]
		
		xp.save(modified, "png")
		modified.seek(0)

		await message.channel.send(file=File(
			fp=modified,
			filename="xp.png"
		))

	async def find_user(self, resolvable):
		resolvable = self.resolve_mention.sub(r"\g<2>", resolvable)
		for user in self.client.users:
			if str(user.id) == resolvable:
				return user
			
			if f"{user.name}#{user.discriminator}" == resolvable:
				return user
	
		if resolvable.isdigit():
			try:
				user = await self.client.fetch_user(int(resolvable))
				return user
			except (NotFound, HTTPException, ValueError):
				return None


def setup(client):
	client.CommandHandler.add_command(Xp(client))
