from discord import Activity, ActivityType
from random import randint


class UpdateStatus:
    def __init__(self, client):
        self.client = client

    async def run(self):
        users = "{} users".format(str(len(self.client.users)))
        guilds = "{} guilds".format(str(len(self.client.guilds)))
        prefix = "for {}help".format(self.client.config.default_prefix)

        statuses = [
            users,
            guilds,
            prefix
        ]

        await self.client.change_presence(
            activity=Activity(
                type=ActivityType.watching,
                name=statuses[randint(0, 2)]
            )
        )


def setup(setup_event, client):
    setup_event(
        UpdateStatus(client),
        15
    )
