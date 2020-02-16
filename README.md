# <img src="https://i.imgur.com/DWTbzf4.png" align="left" width="4%"> TFR Bot

<div align="center">
    <p>
        <a href="https://github.com/TFR-Development/TFR-Bot/actions">
            <img src="https://github.com/TFR-Development/TFR-Bot/workflows/Python%20application/badge.svg" alt="Build">
        </a>
        <a href="https://dependabot.com">
            <img src="https://api.dependabot.com/badges/status?host=github&repo=TFR-Development/TFR-Bot" alt="Dependabot Status">
        </a>
        <a href="https://github.com/TFR-Development/TFR-Bot">
            <img src="https://img.shields.io/github/downloads/TFR-Development/TFR-Bot/total.svg" alt="GitHub Total Download Count">
        </a>
        <a href="https://github.com/TFR-Development/TFR-Bot">
            <img src="https://img.shields.io/github/license/mashape/apistatus.svg" alt="License">
        </a>
        <a href="https://github.com/TFR-Development/TFR-Bot">
            <img src="https://img.shields.io/github/languages/top/TFR-Development/TFR-Bot.svg" alt="Language">
        </a>
        <a href="https://github.com/TFR-Development/TFR-Bot/releases">
            <img src="https://img.shields.io/github/v/release/TFR-Development/TFR-Bot" alt="Release">
        </a>
    </p>
    <p>
        <a href="https://discord.furretreat.rocks">
            <img src="https://discordapp.com/api/v6/guilds/569747786199728150/embed.png?style=banner2" alt="Discord">
        </a>
    </p>
    <p>
        <a href="https://twitter.com/furretreat">
            <img src="https://img.shields.io/twitter/follow/furretreat?style=social" alt="Twitter">
        </a>
    </p>
</div>

## A Discord bot for [The Fur Retreat.](https://discord.furretreat.rocks)

### Prerequisites

- Python 3
- RethinkDB
- TFR-API

For some commands, the bot requires the [TFR-API](https://github.com/TFR-Development/TFR-API). Please check the README.md for install instructions.

### Setup

#### Virtual Environment
1. Create a virtual environment by navigating into the project folder and then running `python3 -m venv .` in your terminal.
2. Once this has completed, run `cd venv/scripts` and then `activate` or `activate.bat` depending on your OS.
3. Run `cd ../../` and then `pip3 install requirements.txt`.
4. Setup a RethinkDB server and then run `python3 main.py`, the bot should be online now.

#### No Virtual Environment
1. Run `pip3 install -r requirements.txt`.
2. Setup a RethinkDB server.
3. Run `python3 main.py`.
The bot should be online now.

#### Setting up RethinkDB

[This official guide](https://rethinkdb.com/docs/install/) will link to the RethinkDB site, giving instructions and downloadable files for different operating systems.

Once you've downloaded the server and ran it, make sure to create the database named `tfr`.

### Project Information

#### Developers

- [Ben](https://github.com/Ben071) 
    - <img src="https://i.imgur.com/WksIWPO.png" align="left" width="2%"> <a href="https://twitter.com/BenjiTheFurry">Twitter</a>
    - <img src="https://i.imgur.com/ddZTLOt.png" align="left" width="2%"> Benji#6666
- [Jack](https://github.com/Jack073) 
    - <img src="https://i.imgur.com/ddZTLOt.png" align="left" width="2%"> jac.k12#9409

#### License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).
