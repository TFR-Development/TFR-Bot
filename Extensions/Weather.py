from discord import Embed, Colour
from geopy.geocoders import Nominatim
import re
import datetime


def get_output(w_text):
    # Adds the appropriate weather emoji to w_text
    
    w_low = w_text.lower()
    
    if "tornado" in w_low:
        return "🌪️ " + w_text
    
    if any(x in w_low for x in ["hurricane", "tropical"]):
        return "🌀 " + w_text
    
    if any(x in w_low for x in ["snow", "flurries", "hail"]):
        return "🌨️ " + w_text
    
    if "thunder" in w_low:
        return "⛈️ " + w_text
    
    if any(x in w_low for x in ["rain", "drizzle", "showers", "sleet"]):
        return "🌧️ " + w_text
    
    if "cold" in w_low:
        return "❄️ " + w_text
    
    if any(x in w_low for x in ["windy", "blustery", "breezy"]):
        return "🌬️ " + w_text
    
    if "mostly cloudy" in w_low:
        return "⛅ " + w_text
    
    if any(x in w_low for x in ["partly cloudy", "scattered clouds",
                                "few clouds", "broken clouds"]):
        return "🌤️ " + w_text
    
    if any(x in w_low for x in ["cloudy", "clouds"]):
        return "☁️ " + w_text
    
    if "fair" in w_low:
        return "🌄 " + w_text
    
    if any(x in w_low for x in ["hot", "sunny", "clear"]):
        return "☀️ " + w_text
    
    if any(x in w_low for x in ["dust", "foggy", "haze", "smoky"]):
        return "️🌫️ " + w_text
    
    # No emoji for that text, return text
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
        self.description = "Converts between Fahrenheit, Celsius and " \
                           "Kelvin."
        self.usage = "tempconvert <temperature> <from_type> <to_type>"

    async def run(self, _, message, *args):
        if len(args) == 0:
            return await self.client.errors.MissingArgs(
                "temperature"
            ).send(
                message.channel
            )

        self.client.args_parser.get_args(
            message,
            *args
        )

        if len(args) < 2:
            return await self.client.errors.MissingArgs(
                "from_type"
            ).send(
                message.channel
            )

        if len(args) < 3:
            return await self.client.errors.MissingArgs(
                "to_type"
            ).send(
                message.channel
            )

        temp, from_type, to_type, *_ = args

        types = ["Fahrenheit", "Celsius", "Kelvin"]

        try:
            m = int(args[0])
        except ValueError:
            return await self.client.errors.InvalidArgs(
                args[0],
                "temperature"
            ).send(message.channel)

        args_1_l = args[1].lower()
        
        args_2_l = args[2].lower()

        f = next(
            (
                x for x in types
                if x.lower() == args_1_l or x.lower()[0] == args_1_l[0]
            ), None
        )
        
        t = next(
            (
                x for x in types
                if x.lower() == args_2_l or x.lower()[0] == args_2_l
            ), None
        )

        if not f:
            # Invalid from type
            return await self.client.errors.InvalidArgs(
                args[1],
                "from_type"
            ).send(message.channel)
        if not t:
            # Invalid to type
            return await self.client.errors.InvalidArgs(
                args[2],
                "to_type"
            ).send(message.channel)
        if f == t:
            # Same in as out
            return await self.client.errors.UnchangedOutput(
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
                colour=Colour.from_rgb(234, 111, 255)
            ).add_field(
                name="Input",
                value="{:,}{}{}".format(
                    m,
                    "" if (f == "Kelvin") else "°",
                    f[0]
                ),
                inline=True
            ).add_field(
                name="Output",
                value="{:,}{}{}".format(
                    out_val,
                    "" if (t == "Kelvin") else "°",
                    t[0]
                ),
                inline=True
            )
        )


class Weather:
    @staticmethod
    def get_weather_embed(r=None):
        
        if not r:
            # Non mutable default parameters
            r = {}
            
        # Returns a string representing the weather passed
        main = r["main"]
        weather = r["weather"]
        coord = r["coord"]
        sys = r["sys"]

        # Make sure we get the temps in both F and C
        tc = k_to_c(main["temp"])
        tf = c_to_f(tc)
        min_c = k_to_c(main["temp_min"])
        min_f = c_to_f(min_c)
        max_c = k_to_c(main["temp_max"])
        max_f = c_to_f(max_c)
        lat = coord["lat"]
        lon = coord["lon"]
        
        place = r.get("name", lat)
        country = sys.get("country", lon)
        flag = f":flag_{country.lower()}:" if country else ""
        
        # Gather the formatted conditions
        condition_list = []
        for x, y in enumerate(weather):
            d = y["description"]
            if x == 0:
                d = d.capitalize()
            condition_list.append(get_output(d))
        condition = ", ".join(condition_list)

        return Embed(
            title="Weather for {}, {} {}".format(place, country, flag),
            type="rich",
            colour=Colour.from_rgb(234, 111, 255)
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
            value="High of {}°C ({}°F)".format(max_c, max_f),
        ).add_field(
            name="Daily Low",
            value="Low of {}°C ({}°F)".format(min_c, min_f),
            inline=True
        ).set_footer(
            text=f"Lat: {lat} | Lon: {lon} | Powered by OpenWeatherMap"
            if (place != lat or country != lon) else "Powered by"
                                                     " OpenWeatherMap"
        )

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
            return await self.client.errors.MissingArgs(
                "place_name"
            ).send(
                message.channel
            )

        self.client.args_parser.get_args(
            message,
            *args
        )

        place_name = " ".join(args)

        # Strip anything that's non alphanumeric or a space
        place_name = re.sub(r'([^\s\w]|_)+', '', str(place_name))
        location = self.geo.geocode(str(place_name))

        if location is None:
            return await self.client.errors.PlaceNotFound(
                place_name
            ).send(
                message.channel
            )

        # Just want the current weather
        r = await self.client.DL.async_json(
            "http://api.openweathermap.org/data/2.5/weather?"
            "appid={}&lat={}&lon={}".format(
                self.key,
                location.latitude,
                location.longitude
            )
        )
        
        embed = self.get_weather_embed(r)

        await message.channel.send(
            embed=embed
        )


class Forecast:
    @staticmethod
    def get_weather_text(r):
        # Returns a string representing the weather passed
        main = r["main"]
        weath = r["weather"]

        # Make sure we get the temps in both F and C
        tc = k_to_c(main["temp"])
        tf = c_to_f(tc)
        min_c = k_to_c(main["temp_min"])
        min_f = c_to_f(min_c)
        max_c = k_to_c(main["temp_max"])
        max_f = c_to_f(max_c)

        # Gather the formatted conditions
        condition_list = []
        for x, y in enumerate(weath):
            d = y["description"]
            if x == 0:
                d = d.capitalize()
            condition_list.append(get_output(d))
        condition = ", ".join(condition_list)

        # Format the description
        desc = "{}°C ({}°F),\n\n{},\n\nHigh of {}°C ({}°F) - Low of" \
               " {}°C ({}°F)\n\n".format(
                    tc, tf,
                    condition,
                    max_c, max_f,
                    min_c, min_f
                )

        return desc

    def __init__(self, client):
        self.client = client

        self.name = "forecast"
        self.aliases = [
            "weatherforecast"
        ]

        self.category = "Utilities"
        self.perm_level = 0
        self.description = "Gets some weather, for 5 days."
        self.usage = "forecast <place_name>"
        self.geo = Nominatim(user_agent="TFR-Bot")
        self.key = self.client.config.openweathermap_key

    async def run(self, _, message, *args):
        if len(args) == 0:
            return await self.client.errors.MissingArgs(
                "place_name"
            ).send(
                message.channel
            )

        self.client.args_parser.get_args(
            message,
            *args
        )

        place_name = " ".join(args)

        # Strip anything that's non alphanumeric or a space
        place_name = re.sub(r'([^\s\w]|_)+', '', str(place_name))
        location = self.geo.geocode(str(place_name))

        if location is None:
            return await self.client.errors.PlaceNotFound(
                place_name
            ).send(
                message.channel
            )

        # We want the 5-day forecast at this point
        r = await self.client.DL.async_json(
            "http://api.openweathermap.org/data/2.5/forecast?appid={}"
            "&lat={}&lon={}".format(
                self.key,
                location.latitude,
                location.longitude
            )
        )

        try:
            city = r["city"]
            city_name = city["name"]
            country = city["country"]
            flag = ":flag_{}:".format(str(country).lower())

            title = "5 Day Forecast for {}, {} {}".format(
                city_name,
                country,
                flag
            )
        except KeyError:
            title = "5 Day Forecast for {}".format(location)

        days = {}
        for x in r["list"]:
            # Check if the day exists - if not, we set up a pre-day
            day = x["dt_txt"].split(" ")[0]
            is_noon = "12:00:00" in x["dt_txt"]
            if day not in days:
                days[day] = {
                    "main": x["main"],
                    "weather": x["weather"],
                    "day_count": 1
                }
                continue
            # Day is in the list - let's check values
            if x["main"]["temp_min"] < days[day]["main"]["temp_min"]:
                days[day]["main"]["temp_min"] = x["main"]["temp_min"]
            if x["main"]["temp_max"] > days[day]["main"]["temp_max"]:
                days[day]["main"]["temp_max"] = x["main"]["temp_max"]
            # Add the temp
            days[day]["main"]["temp"] += x["main"]["temp"]
            days[day]["day_count"] += 1
            # Set the weather data if is noon
            if is_noon:
                days[day]["weather"] = x["weather"]

        embed = Embed(
            type="rich",
            title=title,
            color=Colour.from_rgb(234, 111, 255)
        ).set_footer(
            text="Powered by OpenWeatherMap"
        )

        for day in sorted(days):
            # Average the temp, strip weather duplicates
            days[day]["main"]["temp"] /= days[day]["day_count"]
            embed.add_field(
                name=(
                    datetime.datetime.strptime(day, "%Y-%m-%d")
                    .strftime("%A, %b %d, %Y") + ":"
                ),
                value=self.get_weather_text(days[day]),
                inline=False
            )

        await message.channel.send(embed=embed)


def setup(client):
    client.command_handler.add_commands(
        TempConvert(client),
        Weather(client),
        Forecast(client)
    )
