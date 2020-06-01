from PIL import (
	Image, ImageFont, ImageDraw
)  # Image utils
from io import BytesIO  # Buffer for uploading image
from discord import (
	File, NotFound, HTTPException
)
from aiohttp import ClientSession  # For making HTTP requests
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
		
		self.typing = True
		
	async def run(self, _, message, *args):
		# Copies the open PIL.Image xp template
		# So changes are reset every time the command is ran
		xp = self.xp.copy()
		
		xp_saved = xp.load()
		
		modified = BytesIO()
		# Create a BytesIO buffer
		
		member = User(message.author)
		
		# Convert the immutable tuple to a mutable list
		args = list(args)
		
		args = " ".join(args)
		
		if args:
			# A user was supplied as an argument
			if not self.user_resolvable.match(args):
				# args isn't a user resolvable
				return await self.client.errors.InvalidArgs(
					args,
					"user"
				).send(message.channel)

			user = await self.find_user(args)

			if not user:
				# No user found from the resolvable
				return await self.client.errors.InvalidArgs(
					args,
					"user"
				).send(message.channel)

			member = User(user)
		
		user_tag = member.tag
		
		# Retrieve the total xp for the guild to form a leader board
		ctx = list(
			self.client.data_base_manager.get_table("xp").filter(
				{
					"guild": str(message.guild.id)
				}
			).run(self.client.data_base_manager.connection)
		)
		
		ctx.sort(key=lambda u: u["xp"], reverse=True)
		# Sort the leader board based on total xp

		rank_lb = None
		total_xp = None
		
		for location, info in enumerate(ctx, 1):
			# Search to find the users position on the lb
			if info["user"] == str(member.get("id")):
				rank_lb = location
				total_xp = info["xp"]
				break
				
		if not rank_lb:
			# Couldn't find there user in the lb (somehow??)
			return await self.client.errors.NoXP().send(message.channel)
			
		draw = ImageDraw.Draw(xp)
		
		font = ImageFont.truetype(
			self.client.config.font_file,  # Set font file
			40 if len(user_tag) <= 15 else 20  # Set font size
		)

		score_font = ImageFont.truetype(
			self.client.config.font_file,  # Set font file
			40  # Set font size (constant)
		)
		
		rank_font = ImageFont.truetype(
			self.client.config.font_file,  # Set font file
			30  # Set font size (constant)
		)
		
		# Add the user tag to the image
		draw.text(
			(140, 80,),
			user_tag,
			(0, 0, 0,),
			font=font
		)
		
		# Add the users level to the image
		draw.text(
			(120, 220,),
			"Lvl " + str(
				self.client.data_base_manager.xp_level(
					str(message.guild.id),
					str(member.get("id"))
				)
			),
			(0, 0, 0),
			font=score_font
		)
		
		# Add the users position on the leaderboard to the image
		draw.text(
			(286, 220,),
			f"{rank_lb} / {len(ctx)}",
			(0, 0, 0),
			font=rank_font
		)
		
		# Add total xp to image
		draw.text(
			(60, 310,),
			f"{total_xp} XP",
			(0, 0, 0),
			font=score_font
		)
		
		# Format user avatar url link as png (64 x 64)
		avatar_url = str(
			member.get("avatar_url_as")(
				format="png",
				size=64
			)
		)
		
		av_request = None
		
		async with ClientSession() as session:
			async with session.get(avatar_url) as r_data:
				if r_data.status == 200:
					av_request = await r_data.content.read(-1)
		
		if not av_request:
			# if some exception causes a status != 200
			return await self.client.errors.FetchAvatarError().send(
				message.channel
			)
		
		avatar = Image.open(BytesIO(av_request))
		# Open the avatar as a PIL.Image
		av_loaded = avatar.load()
		
		to_replace = []
		
		for y in range(64, 140):
			for x in range(50, 135):
				# Approximate range of the image slot
				
				if xp_saved[x, y] != (106, 106, 106, 255):
					continue
				# Colour check to find exact range
				
				to_replace.append((x, y,))
		
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
		
		# Write the xp image to the "modified" buffer
		xp.save(modified, "png")
		
		# Seek to 0 as saving (calls write()) sets the position to
		# the end of the write (in this case EOF)
		modified.seek(0)

		# Send file
		await message.channel.send(
			file=File(
				fp=modified,
				filename="xp.png"
			)
		)

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
	client.command_handler.add_command(Xp(client))
