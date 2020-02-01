# TFR Bot

[![Python application](https://github.com/TFR-Development/TFR-Bot/workflows/Python%20application/badge.svg)](https://github.com/TFR-Development/TFR-Bot/actions)
[![GitHub](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/TFR-Development/TFR-Bot)
[![Language Badge](https://img.shields.io/github/languages/top/TFR-Development/TFR-Bot.svg)](https://github.com/TFR-Development/TFR-Bot)

[![Discord](https://img.shields.io/discord/569747786199728150?label=Discord&logo=Discord)](https://discord.furretreat.rocks)
[![Twitter Follow](https://img.shields.io/twitter/follow/furretreat?style=social)](https://twitter.com/FurRetreat)

## A Discord bot for [The Fur Retreat.](https://discord.furretreat.rocks)

### Setup

#### Virtual Environment
1. Create a virtual environment by navigating into the project folder and then running `python -m venv .` in your terminal.
2. Once this has completed, run `cd venv/scripts` and then `activate` or `activate.bat` depending on your OS.
3. Run `cd ../../` and then `pip install requirements.txt`.
4. Setup a RethinkDB server and then run `python main.py`, the bot should be online now.

#### No Virtual Environment
1. Run `pip install -r requirements.txt`.
2. Setup a RethinkDB server.
3. Run `python main.py`.
The bot should be online now.

#### Setting up RethinkDB

[This official guide](https://rethinkdb.com/docs/install/) will link to the RethinkDB site, giving instructions and downloadable files for different operating systems.

Once you've downloaded the server and ran it, make sure to create the database named `tfr`.
