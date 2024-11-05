from pathlib import Path
import unrealsdk #type: ignore
from unrealsdk import logging #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct #type: ignore
from mods_base import hook,get_pc,ENGINE, build_mod, SETTINGS_DIR #type: ignore

__version__: str
__version_info__: tuple[int, ...]

def ClientReceive(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    def OutputText(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
        remove_hook("Engine.Console:OutputText", Type.PRE, "OutputText")
        return (Block)
    add_hook("Engine.Console:OutputText", Type.PRE, "OutputText", OutputText)

#All Hooks point to the same function, no point in making multiple
add_hook("WillowGame.WillowLocalMessage:ClientReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("WillowGame.WillowPickupMessage:ClientReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("WillowGame.ReceivedCreditsMessage:ClientCreditReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("WillowGame.ReceivedAmmoMessage:ClientAmmoReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("WillowGame.LocalWeaponMessage:ClientWeaponReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("WillowGame.LocalItemMessage:ClientItemReceive", Type.PRE, "ClientReceive", ClientReceive)
add_hook("Engine.LocalMessage:ClientReceive", Type.PRE, "ClientReceive", ClientReceive)

build_mod()

logging.info(f"Quiet Console Loaded: {__version__}, {__version_info__}")

