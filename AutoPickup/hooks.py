import unrealsdk
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook,get_pc

InteractiveObjects = {}

@hook(
    hook_func="WillowGame.WillowPickup:SpawnPickupParticles",
    hook_type=Type.POST,
)
def SpawnPickupParticles(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    global InteractiveObjects
    if obj.Inventory and obj.Inventory.Class.Name == "WillowUsableItem":
        BaseIO = obj.Base
        if BaseIO in InteractiveObjects.keys() and InteractiveObjects[BaseIO] and obj.bPickupable:
            InteractiveObjects[BaseIO][0].TouchedPickupable(obj)
            InteractiveObjects[BaseIO][0].CurrentSeenPickupable = None
            InteractiveObjects[BaseIO][0].CurrentTouchedPickupable = None


@hook(
    hook_func="WillowGame.WillowInteractiveObject:UsedBy",
    hook_type=Type.POST,
)
def UsedBy(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    global InteractiveObjects
    InteractiveObjects[obj] = [__args.User.Controller]
