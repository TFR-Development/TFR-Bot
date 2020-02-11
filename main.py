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

for file in listdir("Events"):

	if not file.endswith(".py"):
		continue
	
	module = import_module(f"Events.{file.split('.')[0]}")
	
	if not hasattr(module, "setup"):
		print(f"Unable to load {file}, missing setup function")
		continue
		
	module.setup(client)
	
for extension in listdir("Extensions"):
	
	if not extension.endswith(".py"):
		continue

	cmd = import_module(f"Extensions.{extension.split('.')[0]}")
	
	if not hasattr(cmd, "setup"):
		print(f"Unable to load {extension}, missing setup function")
		continue
		
	cmd.setup(client)

client.run(config.token)
