import unrealsdk
from unrealsdk import logging
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook,get_pc

import random

@hook(
    hook_func="WillowGame.WillowPawn:PostBeginPlay",
    hook_type=Type.POST,
)
def PawnSpawned(
    obj: UObject,
    __args: WrappedStruct,
    __ret: any,
    __func: BoundFunction,
) -> None:
    if obj.Class.Name != "WillowPlayerPawn":
        #ScaleBehavior = unrealsdk.construct_object("Engine.Behavior_ChangeScale", obj)
        #ScaleBehavior.Scale = random.uniform(0.2, 1.8)
        #NoEvent: WrappedStruct = None
        #ScaleBehavior.ApplyBehaviorToContext(obj, None, None, None, NoEvent)
        newsize = random.uniform(0.2, 1.8)
        collisioncylinder = obj.CollisionComponent
        obj.SetDrawScale(newsize)
        collisioncylinder.CollisionHeight = collisioncylinder.CollisionHeight * newsize
        
        collisioncylinder.CollisionRadius = collisioncylinder.CollisionRadius * newsize
    