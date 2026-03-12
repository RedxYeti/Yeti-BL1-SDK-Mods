from unrealsdk.hooks import Type, add_hook, remove_hook, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction 
from mods_base import hook,build_mod 


@hook("WillowGame.WillowLocalMessage:ClientReceive", Type.PRE)
@hook("WillowGame.WillowPickupMessage:ClientReceive", Type.PRE)
@hook("WillowGame.ReceivedCreditsMessage:ClientCreditReceive", Type.PRE)
@hook("WillowGame.ReceivedAmmoMessage:ClientAmmoReceive", Type.PRE)
@hook("WillowGame.LocalWeaponMessage:ClientWeaponReceive", Type.PRE)
@hook("WillowGame.LocalItemMessage:ClientItemReceive", Type.PRE)
@hook("Engine.LocalMessage:ClientReceive", Type.PRE)
def ClientReceive(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    OutputText.enable()
    return

@hook("Engine.Console:OutputText", Type.PRE)
def OutputText(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    OutputText.disable()
    return Block


build_mod(hooks=[ClientReceive])