from typing import Any #type:ignore
from mods_base import hook, build_mod, keybind, get_pc,BoolOption #type:ignore
from unrealsdk.hooks import Type, Block #type:ignore
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct #type:ignore
from .maps import Map
from .enemies import Enemy

@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def FinalizedMapChange(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> Any:
    map_name = args.NextMapName
    #print(map_name)
    map_class = Map.registry.get(map_name)
    if map_class:
        map_class().on_map_loaded()


@hook("WillowGame.WillowVehicle:Died", Type.PRE)
def AnyVehicleDied(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if not obj.ObjectArchetype:
        return
    
    enemy_balance = obj.ObjectArchetype._path_name()
    #print(enemy_balance)
    enemy_class = Enemy.registry.get(enemy_balance)
    if enemy_class:
        enemy_inst = enemy_class()
        enemy_inst.pawn = obj
        enemy_inst.on_enemy_death()


@hook("WillowGame.WillowPawn:Died", Type.PRE)
def AnyPawnDied(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    if not obj.BalanceDefinitionState or not obj.BalanceDefinitionState.BalanceDefinition:
        return
    enemy_balance = obj.BalanceDefinitionState.BalanceDefinition._path_name()
    #print(enemy_balance)
    enemy_class = Enemy.registry.get(enemy_balance)
    if enemy_class:
        enemy_inst = enemy_class()
        enemy_inst.pawn = obj
        enemy_inst.on_enemy_death()


@hook("WillowGame.WillowPlayerController:openl", Type.PRE)
def LoadGameCheck(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> Any:
    print(args)
    if not oidOasis.value and args.openurl == 'Scrap_Oasis_P?listen':
        func('Arid_Arena_Coliseum_P?listen')
        return Block
        
        
@keybind("Reload Map",description="Saves the game, then fully reloads the current map you're in.")
def reload_map():
    pc = get_pc()
    pc.sg_save_game()
    current_map = pc.WorldInfo.GetMapName()
    pc.ConsoleCommand(f"openl {current_map}")


def xp_gain_toggled(option, new_value):
    value = 0 if new_value else 1
    get_pc().ConsoleCommand(f"set ExperienceResourcePool ExpAllPointsScale {value}")


oidBlockXPGain = BoolOption(
    "Block XP Gain",
    False,
    "On",
    "Off",
    description=f"Stops XP Gain for farming.",
    on_change=xp_gain_toggled
)

oidOasis = BoolOption(
    "Oasis Installed",
    False,
    "On",
    "Off",
    description=f"Turn this on if you have oasis installed.",
    on_change=xp_gain_toggled
)


build_mod(options=[oidBlockXPGain, oidOasis])