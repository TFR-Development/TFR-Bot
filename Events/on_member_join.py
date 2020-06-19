from discord import (
	Embed, Colour, HTTPException, NotFound, DiscordException
)
from base64 import b64encode


class MemberJoin:
	def __init__(self, client):
		self.client = client
		client.event(self.on_member_join)
	
	async def on_member_join(self, member):
		try:
			av = await member.avatar_url_as(
				format="png",
				size=1024
			).read()

			# Run image AutoMod against new users avatar
			await self.client.auto_mod.image_filter(
				b64encode(av).decode(),
				member
			)

		except (DiscordException, HTTPException, NotFound):
			# Exceptions from fetching users avatar, fail silently
			pass

		join_logs = self.client.get_channel(577905211922841601)
		
		if not join_logs:
			return
		
		# Send a message to the join logs channel with the users
		# (enlarged). The link to the users avatar
		# And a link to a reverse image search result
		await join_logs.send(
			embed=Embed(
				type="rich",
				title=f"Avatar for {member}",
				colour=Colour.from_rgb(238, 144, 101),
				description=(
					f"[Avatar]({member.avatar_url})\n"
					"[Reverse Image Search]("
					"https://images.google.com/searchbyimage?"
					"image_url=" +
					str(member.avatar_url).replace(':', '%3A').replace(
						'/', '%2F'
					) + ")"
				)
			).set_image(
				url=str(member.avatar_url)
			)
		)


def setup(client):
	MemberJoin(client)

