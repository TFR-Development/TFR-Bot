class ArgsParser:
    def __init__(self, client):
        self.client = client

    def get_args(self, message, *args):
        args = self.client.API.request(
            route="argparser",
            Message=" ".join(args)
        ).get("Message", [])

        if args == -1:
            return self.client.errors.NoAPIConnection().send(
                message.channel
            )

        return args
