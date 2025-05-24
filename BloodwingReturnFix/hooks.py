import unrealsdk
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook,get_pc

@hook(hook_func="WillowGame.WillowProjectile:RunCustomEvent",hook_type=Type.POST,)
def BloodwingCalled(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    if obj.Class.Name == "WillowBloodwingProjectile" and __args.EventName == "Return":
        obj.CollisionComponent = None

@hook(
    hook_func="WillowGame.WillowProjectile:Detonate",
    hook_type=Type.POST,
)
def BloodwingDetonated(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    if obj.Class.Name == "WillowBloodwingProjectile":
        obj.InstigatorController.RetrieveBloodwing(False, 0)
