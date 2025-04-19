from unrealsdk import find_object, load_package, find_class, construct_object
from typing import Any
from unrealsdk.hooks import Type 
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction 
from mods_base import build_mod, hook, BoolOption, SliderOption


def DivideFalloff(Option,Value):
    global Falloff
    Falloff = Value/10
    return


oidWeaponsGear = BoolOption(
    "Weapons and Gear Only",
    False,
    "On",
    "Off",
    description="With this enabled, only weapons and gear will have lights. Otherwise every item will have a light.",
)

oidBrightness = SliderOption(
    "Light Brightness",
    5,
    1,
    15,
    1,
    True,
    description="Choose how bright you want the lights.\nDefault Value: 5",
)

oidRadius = SliderOption(
    "Light Radius",
    150,
    10,
    1024,
    10,
    False,
    description="Choose how far you want the light radius to go.\nDefault Value: 150",
)

oidFalloff = SliderOption(
    "Light Falloff",
    40,
    1,
    80,
    1,
    True,
    on_change=DivideFalloff,
    description=("Choose the falloff of the light radius."
                 "\nLower Values make the brightness extend to the edges of the light making the edges sharper. Default Value: 40"),
)

GlobalsDef: UObject = find_class("WillowGlobals").ClassDefaultObject.GetWillowGlobals().GetGlobalsDefinition()

ClassWhitelist: list = ["WillowWeapon", "WillowEquipAbleItem", "WillowUsableItem"]

def EnableLight(Pickupable:UObject):
    #if not Pickupable.Pickupable_IsEnabled():
    #    #dont want a light  if its not enabled
    #    return

    

    if not Pickupable.Inventory:
        return

    for Component in Pickupable.Components:
        if Component and Component.Class.Name == "PointLightComponent":
            #dont know if this is needed but dont want 2 lights
            return
    
    
    global ClassWhitelist
    if Pickupable.Inventory.Class.Name not in ClassWhitelist:
        return
    
    

    if oidWeaponsGear.value and Pickupable.Inventory.Class.Name == "WillowUsableItem":
        return
    
    
    Light = construct_object("PointLightComponent", Pickupable)

    #player settings
    Light.Brightness = oidBrightness.value
    Light.Radius = oidRadius.value
    Light.FalloffExponent = oidFalloff.value

    #lifts the light up just above the pickupable
    Light.Translation.Z = 15

    #shadows dont work correctly and this adds a bunch of performance. all these values are true by default on pointlightcomponents
    Light.CastShadows = False
    Light.CastStaticShadows = False
    Light.CastDynamicShadows = False
    Light.bCastCompositeShadow = False

    Light.LightColor = GlobalsDef.GetRarityColorForLevel(Pickupable.InventoryRarityLevel)

    Pickupable.WorldBodyAttachComponent(Light)
    return


@hook("WillowGame.WillowPickup:SpawnPickupParticles", Type.PRE)
def InventoryAssociated(obj: UObject, __args: WrappedStruct, __ret: Any, __func: BoundFunction) -> None:
    EnableLight(obj)
    return


build_mod()
