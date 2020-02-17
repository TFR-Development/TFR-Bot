from discord import Embed, Colour
from geopy.geocoders import Nominatim
import re


def get_output(w_text):
    if "tornado" in w_text.lower():
        return "🌪️ " + w_text
    if any(x in w_text.lower() for x in ["hurricane", "tropical"]):
        return "🌀 " + w_text
    if any(x in w_text.lower() for x in ["snow", "flurries", "hail"]):
        return "🌨️ " + w_text
    if "thunder" in w_text.lower():
        return "⛈️ " + w_text
    if any(x in w_text.lower() for x in ["rain", "drizzle", "showers", "sleet"]):
        return "🌧️ " + w_text
    if "cold" in w_text.lower():
        return "❄️ " + w_text
    if any(x in w_text.lower() for x in ["windy", "blustery", "breezy"]):
        return "🌬️ " + w_text
    if "mostly cloudy" in w_text.lower():
        return "⛅ " + w_text
    if any(x in w_text.lower() for x in ["partly cloudy", "scattered clouds", "few clouds", "broken clouds"]):
        return "🌤️ " + w_text
    if any(x in w_text.lower() for x in ["cloudy", "clouds"]):
        return "☁️ " + w_text
    if "fair" in w_text.lower():
        return "🌄 " + w_text
    if any(x in w_text.lower() for x in ["hot", "sunny", "clear"]):
        return "☀️ " + w_text
    if any(x in w_text.lower() for x in ["dust", "foggy", "haze", "smoky"]):
        return "️🌫️ " + w_text
    return w_text


def f_to_c(f):
    return int((int(f) - 32) / 1.8)


def c_to_f(c):
    return int((int(c) * 1.8) + 32)


def c_to_k(c):
    return int(int(c) + 273)


def k_to_c(k):
    return int(int(k) - 273)


def f_to_k(f):
    return c_to_k(f_to_c(int(f)))


def k_to_f(k):
    return c_to_f(k_to_c(int(k)))


class TempConvert:
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
        self.usage = "tempconvert <temperature> <from_type> <to_type>"

    async def run(self, _, message, *args):
        if len(args) == 0:
            return await self.client.Errors.MissingArgs(
                "temperature"
            ).send(
                message.channel
            )

        self.client.ArgsParser.get_args(
            message,
            *args
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
                out_val = f_to_c(m)
            else:
                out_val = f_to_k(m)
        elif f == "Celsius":
            if t == "Fahrenheit":
                out_val = c_to_f(m)
            else:
                out_val = c_to_k(m)
        else:
            if t == "Celsius":
                out_val = k_to_c(m)
            else:
                out_val = k_to_f(m)

        await message.channel.send(
            embed=Embed(
                title="Converted!",
                type="rich",
                colour=Colour.from_rgb(111, 255, 141)
            ).add_field(
                name="Input",
                value="{:,} {} {}".format(m, "degree" if (m == 1 or m == -1) else "degrees", f),
                inline=True
            ).add_field(
                name="Output",
                value="{:,} {} {}".format(out_val, "degree" if (out_val == 1 or out_val == -1) else "degrees", t),
                inline=True
            )
        )


class Weather:
    @staticmethod
    def get_weather_embed(r={}):
        # Returns a string representing the weather passed
        main = r["main"]
        weather = r["weather"]
        coord = r["coord"]
        sys = r["sys"]

        # Make sure we get the temps in both F and C
        tc = k_to_c(main["temp"])
        tf = c_to_f(tc)
        minc = k_to_c(main["temp_min"])
        minf = c_to_f(minc)
        maxc = k_to_c(main["temp_max"])
        maxf = c_to_f(maxc)
        lat = coord["lat"]
        lon = coord["lon"]
        try:
            place = r["name"]
            country = sys["country"]
            flag = ":flag_{}:".format(str(country).lower())
        except KeyError:
            place = lat
            country = lon
            flag = ""

        # Gather the formatted conditions
        condition_list = []
        for x, y in enumerate(weather):
            d = y["description"]
            if x == 0:
                d = d.capitalize()
            condition_list.append(get_output(d))
        condition = ", ".join(condition_list)

        embed = Embed(
            title="Weather for {}, {} {}".format(place, country, flag),
            type="rich",
            colour=Colour.from_rgb(111, 255, 141)
        ).add_field(
            name="Current Temperature",
            value="{}°C ({}°F)".format(tc, tf),
            inline=True
        ).add_field(
            name="Condition",
            value=condition,
            inline=True
        ).add_field(
            name="Daily High",
            value="High of {}°C ({}°F)".format(maxc, maxf),
        ).add_field(
            name="Daily Low",
            value="Low of {}°C ({}°F)".format(minc, minf),
            inline=True
        ).set_footer(
            text="Lat: {} | Lon: {}".format(lat, lon) if (place != lat or country != lon) else ""
        )

        return embed

    def __init__(self, client):
        self.client = client

        self.name = "weather"
        self.aliases = [
            "currentweather"
        ]

        self.category = "Utilities"
        self.perm_level = 0
        self.description = "Gets some weather."
        self.usage = "weather <place_name>"
        self.geo = Nominatim(user_agent="TFR-Bot")
        self.key = self.client.config.openweathermap_key

    async def run(self, _, message, *args):
        if len(args) == 0:
            return await self.client.Errors.MissingArgs(
                "place_name"
            ).send(
                message.channel
            )

        self.client.ArgsParser.get_args(
            message,
            *args
        )

        place_name = " ".join(args)

        # Strip anything that's non alphanumeric or a space
        place_name = re.sub(r'([^\s\w]|_)+', '', str(place_name))
        location = self.geo.geocode(str(place_name))

        if location is None:
            return await self.client.Errors.PlaceNotFound(
                place_name
            ).send(
                message.channel
            )

        # Just want the current weather
        r = await self.client.DL.async_json(
            "http://api.openweathermap.org/data/2.5/weather?appid={}&lat={}&lon={}".format(
                self.key,
                location.latitude,
                location.longitude
            ))
        embed = self.get_weather_embed(r)

        await message.channel.send(
            embed=embed
        )


def setup(client):
    client.CommandHandler.add_commands(
        TempConvert(client),
        Weather(client)
    )
