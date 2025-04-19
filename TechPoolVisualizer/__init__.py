import unrealsdk #type: ignore
from unrealsdk import logging, find_all, load_package,make_struct,find_object #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block, log_all_calls #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct#type: ignore
from mods_base import hook, get_pc, ENGINE, EInputEvent, keybind, build_mod, SliderOption #type: ignore

def ResetVis(SliderOption, Value) -> None:
    TechPoolVis.disable()
    TechPoolVis.enable()
    return


oidSize = SliderOption(
    "Visualizer Size",
    1.5,
    0,
    5,
    0.1,
    display_name="Visualizer Size",
    description="The size of the font of the visualizer, not very flexible seems to round off.",
    on_change=ResetVis
)

oidXPos = SliderOption(
    "Visualizer X Position",
    0,
    0,
    10000,
    1,
    display_name="Visualizer X Position",
    description="The position of the Visualizer in the X axis.",
    on_change=ResetVis
)

oidYPos = SliderOption(
    "Visualizer Y Position",
    0,
    0,
    10000,
    1,
    display_name="Visualizer Y Position",
    description="The position of the Visualizer in the Y axis.",
    on_change=ResetVis
)



@hook("WillowGame.WillowWeapon:AssociateTechPool", Type.POST)
def AssociateTechPool(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    if obj.TechPool.Data:
        TechPoolVis.enable()
    return



@hook("Engine.GameViewportClient:PostRender", Type.POST)
def TechPoolVis(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction):
    if not get_pc().Pawn or not get_pc().Pawn.Weapon:
        TechPoolVis.disable()
        return

    if get_pc().Pawn.Weapon.TechPool.Data:
        value = str(int(get_pc().Pawn.Weapon.TechPool.Data.GetCurrentValue()))
        TextToDraw = f"Tech Pool: {value}"
        canvas = args.Canvas 
        canvas.Font = unrealsdk.find_object("Font", "ui_fonts.font_willowbody_18pt")
        white = unrealsdk.make_struct("Color", R=255,G=255,B=255, A=255)
        canvas.DrawColor = white
        canvas.SetPos(oidXPos.value, oidYPos.value)
        canvas.DrawText(TextToDraw, True, oidSize.value, oidSize.value)
    else:
        TechPoolVis.disable()
        
    return

build_mod(hooks=[AssociateTechPool])