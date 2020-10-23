from importlib import import_module
from json import load
from os import listdir

from discord import Client, Activity, Intents

import Utils.Errors as Errors
from Utils.APIBridge import APIBridge
from Utils.ArgsParser import ArgsParser
from Utils.AutoMod import AutoModHandler
from Utils.CommandHandler import CommandHandler
from Utils.DL import DL
from Utils.DataBaseManager import DataBaseManager
from Utils.JSONReader import JSONReader
from Utils.Permissions import Permissions as CalculatePermissions
from Utils.TimeParser import TimeParser
from Utils.WebhookUtils import WebhookManager
from Utils.CoolDownManager import CoolDownManager

with open("config.json") as config_file:
	config = JSONReader(load(config_file))

intents = Intents.none()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.guild_reactions = True

client = Client(
	status="online",
	activity=Activity(
		name="Being Developed"
	),
	intents=intents,
)

client.command_handler = CommandHandler()
client.config = config
client.data_base_manager = DataBaseManager(client)
client.errors = Errors
client.TimeParser = TimeParser
client.calculate_permissions = CalculatePermissions
client.cooldown_manager = CoolDownManager()
client.API = APIBridge(client)
client.DL = DL(client)
client.args_parser = ArgsParser(client)
client.auto_mod = AutoModHandler(client)
client.webhook_manager = WebhookManager(client)
client.failed_events = []
client.failed_commands = []

import_errors = (
	NameError,
	SyntaxError,
	IndentationError,
	ImportError
)

for file in listdir("Events"):
	# Load all event files
	
	if not file.endswith(".py"):
		# Not a python file, ignore
		continue
	
	module = None
	
	try:
		module = import_module(f"Events.{file.split('.')[0]}")
	except import_errors as e:
		client.failed_events.append((file, e,))
		continue
	
	if not hasattr(module, "setup"):
		# The file doesn't have a setup function, warn and continue
		print(f"Unable to load {file}, missing setup function")
		client.failed_events.append((file, "Missing setup function",))
		continue
	
	module.setup(client)

for extension in listdir("Extensions"):
	# Load all command files
	
	if not extension.endswith(".py"):
		# Not a python file
		continue
	
	cmd = None
	try:
		cmd = import_module(f"Extensions.{extension.split('.')[0]}")
	except import_errors as e:
		client.failed_commands.append((extension, e,))
		continue
	
	if not hasattr(cmd, "setup"):
		# File has no setup function, warn and continue
		print(f"Unable to load {extension}, missing setup function")
		client.failed_commands.append((extension, "Missing setup",))
		continue
	
	cmd.setup(client)

if __name__ == "__main__":
	# Run the bot
	client.run(config.token)
