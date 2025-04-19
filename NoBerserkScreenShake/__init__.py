from unrealsdk import find_object, load_package #type: ignore
from unrealsdk.hooks import Type #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction #type: ignore
from mods_base import build_mod, hook #type: ignore

bFirstTimeSetup: bool = False

def FirstTimeSetup() -> None:
    global bFirstTimeSetup
    bFirstTimeSetup = True

    load_package('gd_Brick')
    Corrosive = find_object('ExplosionDefinition','gd_Brick.Effects.Explosion_Corrosive_128')
    Shock = find_object('ExplosionDefinition','gd_Brick.Effects.Explosion_Shock_128')
    Explosive = find_object('ExplosionDefinition','gd_Brick.Effects.Explosion_Explosive_128')
    Incendiary = find_object('ExplosionDefinition','gd_Brick.Effects.Explosion_Incendiary_128')

    Corrosive.ObjectFlags |= 0x4000
    Shock.ObjectFlags |= 0x4000
    Explosive.ObjectFlags |= 0x4000
    Incendiary.ObjectFlags |= 0x4000

    Corrosive.CameraAnim = None
    Shock.CameraAnim = None
    Explosive.CameraAnim = None
    Incendiary.CameraAnim = None

    MainMenuLoad.disable()
    return

@hook("Engine.WorldInfo:IsMenuLevel", Type.POST)
def MainMenuLoad(obj: UObject, __args: WrappedStruct, __ret: any, __func: BoundFunction) -> None:
    global bFirstTimeSetup
    if not bFirstTimeSetup:
        bFirstTimeSetup = True
        FirstTimeSetup()
    return

build_mod(on_enable=FirstTimeSetup)
