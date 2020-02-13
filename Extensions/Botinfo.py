from discord import Embed, Colour


class Botinfo:
    def __init__(self, client):
        self.client = client

        self.name = "botinfo"
        self.aliases = ["binfo"]
        self.perm_level = 0
        self.description = "Shows information about the bot"
        self.category = "Info"
        self.usage = "botinfo"

    async def run(self, _, message, *__):

        await message.channel.send(
            embed=(
                Embed(
                    title="Bot Info",
                    type="rich",
                    colour=Colour.from_rgb(180, 111, 255)
                ).add_field(
                    name="Username",
                    value=self.client.user.name + "#" + self.client.user.discriminator,
                    inline=True
                ).add_field(
                    name="Bot ID",
                    value=str(self.client.user.id),
                    inline=True
                ).add_field(
                    name="Default Prefix",
                    value=self.client.config.default_prefix,
                    inline=True
                ).add_field(
                    name="Owner",
                    value="<@" + str(self.client.config.owner_id) + ">",
                    inline=True
                ).add_field(
                    name="Admin(s)",
                    value=self.get_admins(
                        self.client.config.bot_admins
                    ),
                    inline=True
                ).add_field(
                    name="Guilds",
                    value=len(self.client.guilds),
                    inline=True
                ).add_field(
                    name="Source",
                    value="[Bot](https://github.com/TFR-Development/TFR-Bot)\n[API](https://github.com/TFR-Development/TFR-API)",
                    inline=True
                ).set_thumbnail(
                    url=self.gen_icon(
                        self.client.user.id,
                        self.client.user.avatar
                    )
                )
            )
        )

    @staticmethod
    def get_admins(admin_list):
        admins = ""
        for admin_id in admin_list:
            admins += "<@{}>\n".format(admin_id)
        return admins

    @staticmethod
    def gen_icon(user_id, icon):
        return f"https://cdn.discordapp.com/avatars/{user_id}/{icon}.png?size=1024"


def setup(client):
    client.CommandHandler.add_command(
        Botinfo(client)
    )
