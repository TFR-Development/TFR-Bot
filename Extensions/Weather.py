from discord import Embed, Colour


class TempConvert:
    @staticmethod
    def f_to_c(f):
        return int((int(f) - 32) / 1.8)

    @staticmethod
    def c_to_f(c):
        return int((int(c) * 1.8) + 32)

    @staticmethod
    def c_to_k(c):
        return int(int(c) + 273)

    @staticmethod
    def k_to_c(k):
        return int(int(k) - 273)

    def f_to_k(self, f):
        return self.c_to_k(self.f_to_c(int(f)))

    def k_to_f(self, k):
        return self.c_to_f(self.k_to_c(int(k)))

    def __init__(self, client):
        self.client = client

        self.name = "tempconvert"
        self.aliases = [
            "tconvert",
            "tempcon"
        ]

        self.category = "Utilities"
        self.perm_level = 0
        self.description = "Converts between Fahrenheit, Celsius, and Kelvin."
        self.usage = "tempconvert [temperature] [from_type] [to_type]"

    async def run(self, _, message, *args):
        if len(args) == 0:
            return await self.client.Errors.MissingArgs(
                "temperature"
            ).send(message.channel)

        args = self.client.API.request(
            route="argparser",
            Message=" ".join(args)
        ).get("Message", [])

        if args == -1:
            return await self.client.Errors.NoAPIConnection().send(
                message.channel
            )

        if len(args) < 1:
            return await self.client.Errors.MissingArgs(
                "temperature"
            ).send(
                message.channel
            )

        if len(args) < 2:
            return await self.client.Errors.MissingArgs(
                "from_type"
            ).send(
                message.channel
            )

        if len(args) < 3:
            return await self.client.Errors.MissingArgs(
                "to_type"
            ).send(
                message.channel
            )

        temp, from_type, to_type, *_ = args

        types = ["Fahrenheit", "Celsius", "Kelvin"]

        try:
            m = int(args[0])
        except ValueError:
            return await self.client.Errors.InvalidArgs(
                args[0],
                "temperature"
            ).send(message.channel)

        f = next((x for x in types if x.lower() == args[1].lower() or x.lower()[:1] == args[1][:1].lower()), None)
        t = next((x for x in types if x.lower() == args[2].lower() or x.lower()[:1] == args[2][:1].lower()), None)

        if not f:
            # Invalid from type
            return await self.client.Errors.InvalidArgs(
                args[1],
                "from_type"
            ).send(message.channel)
        if not t:
            # Invalid to type
            return await self.client.Errors.InvalidArgs(
                args[2],
                "to_type"
            ).send(message.channel)
        if f == t:
            # Same in as out
            return await self.client.Errors.UnchangedOutput(
                str(f),
                str(t)
            ).send(message.channel)

        if f == "Fahrenheit":
            if t == "Celsius":
                out_val = self.f_to_c(m)
            else:
                out_val = self.f_to_k(m)
        elif f == "Celsius":
            if t == "Fahrenheit":
                out_val = self.c_to_f(m)
            else:
                out_val = self.c_to_k(m)
        else:
            if t == "Celsius":
                out_val = self.k_to_c(m)
            else:
                out_val = self.k_to_f(m)

        output = "{:,} {} {} is {:,} {} {}".format(m, "degree" if (m == 1 or m == -1) else "degrees", f, out_val, "degree" if (out_val == 1 or out_val == -1) else "degrees", t)

        await message.channel.send(
            embed=Embed(
                type="rich",
                title="Converted!",
                description=output,
                colour=Colour.from_rgb(111, 255, 141)
            )
        )


def setup(client):
    client.CommandHandler.add_commands(
        TempConvert(client)
    )
