from typing import Any #type:ignore
import os

from mods_base import hook, build_mod, keybind, get_pc,BoolOption, ButtonOption,MODS_DIR #type:ignore
from unrealsdk import find_object
from unrealsdk.hooks import Type, Block #type:ignore
from unrealsdk.unreal import BoundFunction, UObject, WrappedStruct #type:ignore

from .maps import Map
from .enemies import Enemy, oidALSlider



@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def FinalizedMapChange(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> Any:
    map_name = args.NextMapName
    #print(map_name)
    map_class = Map.registry.get(map_name)
    if map_class:
        map_class().on_map_loaded()
        
    global reload_bind_hit
    if reload_bind_hit:
        reload_bind_hit = False
        if map_name in dlc4_maps.keys():
            kismet = find_object('SeqVar_Int', f'{dlc4_maps[map_name][0]}')
            kismet.bLinkToAttribute = False
            kismet.IntValue = dlc4_maps[map_name][1]
        else:
            if get_pc().GetCachedProfile().LastVisitedTeleporter == midway_points[map_name]["travel_name"]:
                teleporter = find_object('TeleporterDestination',midway_points[map_name]["teleporter"])
                teleporter.ExitPoints = [find_object('Note', note) for note in midway_points[map_name]["notes"]]


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
    if not oidOasis.value and args.openurl == 'Scrap_Oasis_P?listen':
        func('Arid_Arena_Coliseum_P?listen')
        return Block

  
reload_bind_hit = False
dlc4_maps = {
    'DLC4_Arid_Badlands_p': ['DLC4_Arid_Badlands_p.TheWorld:PersistentLevel.Main_Sequence.SeqVar_Int_1', 60],
    'DLC4_Wayward_Pass_p': ['DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.Main_Sequence.SeqVar_Int_25', 6],
}
midway_points = {
    'dlc1_swamp_ned_p': {"travel_name": "HallowsEndTownEntranceSave",
                         "teleporter": 'dlc1_swamp_ned_p.TheWorld:PersistentLevel.TeleporterDestination_1',
                         "notes": [
                             'dlc1_swamp_ned_p.TheWorld:PersistentLevel.Note_12',
                             'dlc1_swamp_ned_p.TheWorld:PersistentLevel.Note_13',
                             'dlc1_swamp_ned_p.TheWorld:PersistentLevel.Note_14',
                             'dlc1_swamp_ned_p.TheWorld:PersistentLevel.Note_15',
                         ]},

    'dlc1_mill_p': {"travel_name": "LumberYardBridgeEntranceSave",
                    "teleporter": 'dlc1_mill_p.TheWorld:PersistentLevel.TeleporterDestination_0',
                    "notes": [
                        'dlc1_mill_p.TheWorld:PersistentLevel.Note_24',
                        'dlc1_mill_p.TheWorld:PersistentLevel.Note_25',
                        'dlc1_mill_p.TheWorld:PersistentLevel.Note_26',
                        'dlc1_mill_p.TheWorld:PersistentLevel.Note_27',
                    ]},

    'dlc3_NLanceStrip_p': {"travel_name": "RidgewayMidpointEntranceSave",
                           "teleporter": 'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.TeleporterDestination_1',
                           "notes": [
                               'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.Note_40',
                               'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.Note_41',
                               'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.Note_42',
                               'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.Note_43',
                           ]},

    'DLC4_Tartarus_Station_p': {"travel_name": "tartarusstationtown",
                                "teleporter": "DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.TeleporterDestination_2",
                                "notes": [
                                    'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_32',
                                    'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_33',
                                    'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_34',
                                    'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_35',
                                ]},

}
@keybind("Reload Map",description="Saves the game, then fully reloads the current map you're in.")
def reload_map():
    pc = get_pc()
    keybind_map = pc.WorldInfo.GetMapName()
    global reload_bind_hit
    if keybind_map in dlc4_maps.keys():
        reload_bind_hit = True

    if keybind_map in midway_points.keys():
        for key, item in midway_points.items():
            if item["travel_name"] == pc.GetCachedProfile().LastVisitedTeleporter:
                reload_bind_hit = True
                
    pc.sg_save_game()
    current_map = pc.WorldInfo.GetMapName()
    pc.ConsoleCommand(f"openl {current_map}")


def xp_gain_toggled(option, new_value):
    value = 0 if new_value else 1
    get_pc().ConsoleCommand(f"set ExperienceResourcePool ExpAllPointsScale {value}")


def open_drop_chances(option):
    stripped_dir = str(MODS_DIR).strip("sdk_mods")
    full_path = f"{stripped_dir}\\WillowGame\\CookedPC\\DLC\\DedicatedDropsSDK\\BL1 Dedicated Drops Chances.txt"
    if os.path.exists(full_path):
        os.startfile(full_path)



oidDropChances = ButtonOption(
    "Open Drops",
    on_press=open_drop_chances
)


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


build_mod(options=[oidDropChances, oidALSlider, oidBlockXPGain, oidOasis])