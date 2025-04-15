from unrealsdk.hooks import Type, Block #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction#type: ignore
from mods_base import hook, build_mod #type: ignore

@hook("WillowGame.WillowInteractiveObject:AnnounceEligibleMissions", Type.PRE)
def test(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    return Block

build_mod()