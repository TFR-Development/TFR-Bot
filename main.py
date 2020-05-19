from discord import Client, Activity
from json import load
from os import listdir
from importlib import import_module
from Utils.CommandHandler import CommandHandler
from Utils.DataBaseManager import DataBaseManager
from Utils.TimeParser import TimeParser
from Utils.Permissions import Permissions as CalculatePermissions
from Utils.JSONReader import JSONReader
from Utils.APIBridge import APIBridge
from Utils.DL import DL
from Utils.ArgsParser import ArgsParser
from Utils.AutoMod import AutoModHandler
from Utils.WebhookUtils import WebhookManager
import Utils.Errors as Errors

with open("config.json") as config_file:
	config = JSONReader(load(config_file))
	

client = Client(
	status="online",
	activity=Activity(
		name="Being Developed"
	)
)

client.CommandHandler = CommandHandler()
client.config = config
client.DataBaseManager = DataBaseManager(client)
client.Errors = Errors
client.TimeParser = TimeParser
client.CalculatePermissions = CalculatePermissions
client.API = APIBridge(client)
client.DL = DL(client)
client.ArgsParser = ArgsParser(client)
client.AutoMod = AutoModHandler(client)
client.WebhookManager = WebhookManager(client)
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

# Run the bot
client.run(config.token)
