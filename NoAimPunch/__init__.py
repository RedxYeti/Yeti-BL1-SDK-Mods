from mods_base import hook, build_mod
from unrealsdk.hooks import Type,Block


@hook("WillowGame.WillowPlayerController:ShakeView", Type.PRE)
def ShakeView(obj, args, ret, func):
    if args.NewViewShake.RotMag.Z == 400 and args.NewViewShake.RotRate.Z == 20 and args.NewViewShake.RotTime == 0.25:
        return Block

build_mod()