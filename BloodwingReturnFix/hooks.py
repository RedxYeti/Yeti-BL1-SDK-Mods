import unrealsdk
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook,get_pc

@hook(
    hook_func="WillowGame.WillowProjectile:RunCustomEvent",
    hook_type=Type.POST,
)
def BloodwingCalled(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    if __args.EventName == "Return" and obj.Class.Name == "WillowBloodwingProjectile":
        obj.CollisionComponent = None
