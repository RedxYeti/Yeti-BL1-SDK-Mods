from mods_base import hook, build_mod, BoolOption
from unrealsdk import find_class
from unrealsdk.hooks import Type,Block

globals_default = find_class('GearboxFramework.GearboxGlobals').ClassDefaultObject

@hook("WillowGame.WillowPlayerPawn:PlayDamageCameraShake", Type.PRE)
def PlayDamageCameraShake(*_):
    return Block


@hook("WillowGame.WillowPlayerController:DamageShake", Type.PRE)
def DamageShake(obj, args, ret, func):
    if not oidShake.value:
        return

    Globals = globals_default.GetGearboxGlobals()

    if Globals:
        GlobalsDef = Globals.GetGlobalsDefinition()

    if not GlobalsDef:
        return Block
    
    BigDamageThreshold = GlobalsDef.BigDamageThreshold
    BigDamageShake = GlobalsDef.BigDamageShake
    SmallDamageShake = GlobalsDef.SmallDamageShake
    
    Damage = min(args.Damage, 100)

    if(Damage > BigDamageThreshold):
        DamageShake = BigDamageShake
    else:
        DamageShake = SmallDamageShake

    if(DamageShake != None):
        obj.ClientPlayForceFeedbackWaveform(DamageShake)
    return Block


oidShake = BoolOption(
    "Remove Screen Shake",
    False,
    "On",
    "Off",
    description="This will disable the screen shake as well."
)

build_mod()