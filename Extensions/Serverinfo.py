from discord import Embed, Colour, Member
from functools import reduce


class Serverinfo:
	def __init__(self, client):
		self.client = client
	
		self.name = "serverinfo"
		self.aliases = ["sinfo"]
		self.perm_level = 0
		self.description = "Shows information about the current server"
		self.category = "Info"
		self.usage = "serverinfo"
	
	async def run(self, _, message, *__):
		
		await message.channel.send(
			embed=(
				Embed(
					title="Server Info",
					type="rich",
					description="Emojis: " + self.max_emojis(
						message.guild.emojis, 2000
					),
					colour=Colour.from_rgb(180, 111, 255)
				).add_field(
					name="Server Name",
					value=message.guild.name,
					inline=True
				).add_field(
					name="Server ID",
					value=str(message.guild.id),
					inline=True
				).add_field(
					name="Nitro Boosters",
					value=str(message.guild.premium_subscription_count),
					inline=True
				).add_field(
					name="Owner",
					value="<@" + str(message.guild.owner_id) + ">",
					inline=True
				).add_field(
					name="Region",
					value=message.guild.region,
					inline=True
				).add_field(
					name="Channels",
					value=len(message.guild.channels),
					inline=True
				).add_field(
					name="Roles",
					value=len(message.guild.roles),
					inline=True
				).add_field(
					name="Members",
					value=str(message.guild.member_count),
					inline=True
				).add_field(
					name="Online",
					value=reduce(self.online, message.guild.members),
					inline=True
				).add_field(
					name="Premium Features",
					value=", ".join(
						[
							" ".join([w.title() for w in f.split("_")])
							for f in message.guild.features
						]
					) or "None",
					inline=True
				).set_thumbnail(
					url=self.gen_icon(
						message.guild.id,
						message.guild.icon,
						message.guild.is_icon_animated()
					)
				)
			)
		)

	@staticmethod
	def max_emojis(emojis, limit):
		total = ""
		for location, value in enumerate(emojis):
			if location + 1 == len(emojis):
				if len(total) + len(str(value)) < limit:
					return total + str(value)
				else:
					return total + "..."
			if len(total) + len(str(value)) < limit:
				total += str(value)
			else:
				return total + "..."
		
		return "None"
	
	@staticmethod
	def online(total, member):
		
		if not total or isinstance(total, Member):
			total = 0
		
		status = member.status
		
		if isinstance(status, str):
			return total + 1 if status != "offline" else total
		
		return total + 1 if status.name != "offline" else total
	
	@staticmethod
	def gen_icon(guild_id, icon, animated):
		return f"https://cdn.discordapp.com/icons/{guild_id}/" \
				f"{'a_' if animated else ''}{icon}." \
				f"{'gif' if animated else 'png'}?size=1024"


def setup(client):
	client.CommandHandler.add_command(
		Serverinfo(client)
	)
