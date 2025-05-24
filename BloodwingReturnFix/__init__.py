from pathlib import Path
from mods_base import SETTINGS_DIR
from mods_base import build_mod
from unrealsdk import logging

from .hooks import BloodwingCalled, BloodwingDetonated

# Gets populated from `build_mod` below
__version__: str
__version_info__: tuple[int, ...]

build_mod(
    # These are defaulted
    # inject_version_from_pyproject=True, # This is True by default
    # version_info_parser=lambda v: tuple(int(x) for x in v.split(".")),
    # deregister_same_settings=True,      # This is True by default
    keybinds=[],
    hooks=[BloodwingCalled, BloodwingDetonated],
    commands=[],
    # Defaults to f"{SETTINGS_DIR}/dir_name.json" i.e., ./Settings/bl1_commander.json
    settings_file=Path(f"{SETTINGS_DIR}/BloodwingReturnFix.json"),
)

logging.info(f"Bloodwing Return Fix: {__version__}, {__version_info__}")
import unrealsdk #type: ignore
from unrealsdk import logging #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct #type: ignore
from mods_base import hook,get_pc,ENGINE #type: ignore
import os

Initialized = False
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "CommandHistory.txt")
def ConsoleCommandHistory(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global file_path
    if not os.path.exists(file_path): 
        with open(file_path, 'w') as file:
            file.write("fart")  

    if not os.access(file_path, os.W_OK):#readonly
        return
    
    with open(file_path, 'w') as file:
        file.write("")

    for command in obj.History:
        with open(file_path, 'a') as file:
            file.write(command + '\n')

    return

remove_hook("Engine.Console:ConsoleCommand", Type.POST, "ConsoleCommandHistory")
add_hook("Engine.Console:ConsoleCommand", Type.POST, "ConsoleCommandHistory", ConsoleCommandHistory)

def FillHistory(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    global Initialized, file_path
    if Initialized:
        return
    
    Initialized = True


    with open(file_path, 'r') as file:
        obj.History = [line.strip() for line in file.readlines()]

    logging.info(f'{obj.History}')
    return

remove_hook("Engine.Console:Initialized", Type.POST, "FillHistory")
add_hook("Engine.Console:Initialized", Type.POST, "FillHistory", FillHistory)