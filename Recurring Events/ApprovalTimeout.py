from discord.utils import find
from datetime import timedelta, datetime
from discord import Embed
from discord.errors import Forbidden


class ApprovalTimeout:
    def __init__(self, client):
        self.client = client
        self.day = timedelta(days=1)
        
    async def run(self):
        tfr = find(
            lambda g: g.id == 569747786199728150,
            self.client.guilds
        )
        
        if not tfr:
            return
        
        unverified_role = find(
            lambda r: r.id == 589414318609661962,
            tfr.roles
        )
        
        if not unverified_role:
            return
        
        unverified_members = unverified_role.members

        now = datetime.now()
        
        unverified_members = list(
            filter(
                lambda member: (now - member.joined_at) >= self.day,
                unverified_members
            )
        )
        
        for m in unverified_members:
            # @everyone, @Unverified
            if len(m.roles) != 2:
                continue
            try:
                await m.send(embed=Embed(
                        title="The Fur Retreat",
                        type="rich",
                        description=(
                                "You have been kicked from The Fur "
                                "Retreat as you didn't verify within 24"
                                " hours of joining, you are welcome to "
                                "rejoin the server [here]("
                                "https://discord.furretreat.rocks/) and"
                                " this punishment will be removed"
                        )
                ))
            
            except Forbidden:
                pass
            
            await m.kick(reason="Failed to verify")
            
            
def setup(setup_event, client):
    setup_event(
        ApprovalTimeout(client),
        3600
    )
    
    # Run this once an hour
