from discord import Embed, Colour


class MemberJoin:
	def __init__(self, client):
		self.client = client
		client.event(self.on_member_join)
	
	async def on_member_join(self, member):
		if member.guild.id != 569747786199728150:
			return
		
		join_logs = self.client.get_channel(577905211922841601)
		
		if not join_logs:
			return
		
		await join_logs.send(embed=Embed(
			type="rich",
			title=f"Avatar for {member.name}#{member.discriminator}",
			colour=Colour.from_rgb(238, 144, 101)
		).set_image(url=member.avatar_url))


def setup(client):
	MemberJoin(client)

