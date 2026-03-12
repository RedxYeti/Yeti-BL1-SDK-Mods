
from mods_base import build_mod, hook, Game
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject


@hook("Engine.PlayerController:StartFire", Type.POST)
def ReloadFix(obj:UObject, *_) -> None:
    if not obj or not obj.Pawn or not obj.Pawn.Weapon:
        return
    weapon = obj.Pawn.Weapon
    
    if weapon and weapon.NeedToReload():
        weapon.BeginReload(0)
    if Game.get_current() in [Game.BL2, Game.AoDK]:
        offhand = obj.Pawn.OffHandWeapon
        if offhand and offhand.NeedToReload():
            offhand.BeginReload(0)
    return

build_mod()