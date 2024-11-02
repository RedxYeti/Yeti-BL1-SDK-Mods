import unrealsdk #type: ignore
from unrealsdk import logging #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct #type: ignore
from mods_base import hook,get_pc,ENGINE #type: ignore
import os
import json

ForceReadOnly = False

Initialized = False
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CommandHistory.json")

def LoadJson(obj):
    global file_path
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            consoleData: dict = json.load(file)
            
            #this sorts the commands into populated and unpopulated so the history top and bottom are configured correctly
            Commands = consoleData["Commands"]
            PopulatedCommands = [cmd for cmd in Commands if cmd]
            EmptyCommands = [""] * (len(Commands) - len(PopulatedCommands))
            SortedCommands = PopulatedCommands + EmptyCommands
            
            consoleData["Commands"] = SortedCommands
            
            TotalPopulated = len(PopulatedCommands)
            
            obj.HistoryTop = TotalPopulated
            obj.HistoryBot = 0
            obj.HistoryCur = TotalPopulated
            obj.History = consoleData["Commands"]
    return


@hook(hook_func="Engine.Console:ConsoleCommand",hook_type=Type.POST_UNCONDITIONAL,)
def ConsoleCommandHistory(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global file_path, ForceReadOnly
    if not os.path.exists(file_path): 
        with open(file_path, 'w') as file:
            json.dump({}, file, indent=4)

    if not os.access(file_path, os.W_OK):#readonly
        if ForceReadOnly:
            LoadJson(obj)
        return

    commandDict = {}
    commandDict["Commands"] = obj.History

    with open(file_path, 'w') as file:
        json.dump(commandDict, file, indent=4)
    
    return


@hook(hook_func="Engine.Console:PostRender_Console",hook_type=Type.POST,)
def FillHistory(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global Initialized
    if Initialized:
        return
    
    Initialized = True

    LoadJson(obj)

    return