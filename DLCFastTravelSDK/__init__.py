import unrealsdk #type: ignore
from unrealsdk import logging, find_all, load_package,make_struct,find_object,construct_object, find_class #type: ignore
from unrealsdk.hooks import Type, add_hook, remove_hook, Block, log_all_calls,prevent_hooking_direct_calls #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UScriptStruct#type: ignore
from mods_base import hook, get_pc, ENGINE, EInputEvent, keybind, MODS_DIR, build_mod, keybind #type: ignore
from ui_utils import show_hud_message, show_chat_message#type: ignore
from typing import Any
from dataclasses import dataclass

outpost_lookup = None
outpost_def = None
touched_teleporters = []
last_teleport_station = ""
first_map_load = True
def keep_alive(in_object:UObject):
    in_object.ObjectFlags |= 0x4000

def FirstTimeStartup() -> None:
    global outpost_lookup, outpost_def
    load_package('gd_emergencyteleportoutpost')
    outpost_def = find_object('EmergencyTeleportOutpostDefinition','gd_emergencyteleportoutpost.OutpostDefinition')
    keep_alive(outpost_def)
    load_package("gd_RegistrationStationList_dlcft")
    load_package("dlc1_PackageDefinition")
    load_package("dlc2_PackageDefinition")
    load_package("dlc3_PackageDefinition")
    load_package("dlc4_PackageDefinition")
    outpost_lookup = find_object("EmergencyTeleportOutpostLookup","gd_RegistrationStationList_dlcft.Lookups.RegistrationStationLookup")
    keep_alive(outpost_lookup)
    globals_def = find_object("GlobalsDefinition","gd_globals.General.Globals")
    dlc1_globals = find_object("GlobalsDefinition","dlc1_PackageDefinition.CustomGlobals")
    dlc2_globals = find_object("GlobalsDefinition","dlc2_PackageDefinition.CustomGlobals")
    dlc3_globals = find_object("GlobalsDefinition","dlc3_PackageDefinition.CustomGlobals")
    dlc4_globals = find_object("GlobalsDefinition","dlc4_PackageDefinition.CustomGlobals")

    for global_def in [globals_def,dlc1_globals,dlc2_globals,dlc3_globals,dlc4_globals]:
        global_def.TeleporterLookupObject = outpost_lookup
        keep_alive(global_def)

    return



@hook("WillowGame.WillowSaveGameManager:LoadGame", Type.POST)
def finishedloadgame(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global last_teleport_station
    last_teleport_station = obj.GetCachedPlayerProfile(0).LastVisitedTeleporter



@hook("WillowGame.WillowGameInfo:TravelToOutpost", Type.PRE)
def wgi_TravelToOutpost(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    global last_teleport_station
    last_teleport_station = args.OutpostName


@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def PreCommitMapChange(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:
    map_name = args.NextMapName
    print(map_name)
    map_class = FastTravelOutpost.map_registry.get(map_name)
    if map_class:
        map_class().map_loaded()

    return



class FastTravelOutpost():
    map_registry = {}

    def __init_subclass__(cls):
        super().__init_subclass__()
        FastTravelOutpost.map_registry[cls.map_name] = cls#type:ignore

    def __init__(self) -> None:
        self.tp_object:str
        self.outpost_lookup_index:int
        self.name:str
        self.location:WrappedStruct
        self.rotation:WrappedStruct
        self.notes:dict
    
    def map_loaded(self):
        fast_travel = find_object('EmergencyTeleportOutpost', self.tp_object)
        fast_travel.InteractiveObjectDefinition = outpost_def
        fast_travel.OutpostName = self.name

        outpost_lookup.OutpostLookupList[self.outpost_lookup_index].OutpostPathName = fast_travel._path_name()#type:ignore
        if hasattr(self, "location"):
            fast_travel.Location.X = self.location.X
            fast_travel.Location.Y = self.location.Y
            fast_travel.Location.Z = self.location.Z

        if hasattr(self, "rotation"):
            fast_travel.Rotation.Yaw = self.rotation.Yaw

        if hasattr(self, "notes"):
            for note, transform in self.notes.items():
                current_note = find_object('Note',note)
                current_note.Location = transform.location
                current_note.Rotation = transform.rotation
        
        global last_teleport_station
        if last_teleport_station == self.name:
            last_teleport_station = ""
            get_pc().WorldInfo.Game.TeleporterDestinationString = self.tp_object


@dataclass
class ObjectTransform:
    location: WrappedStruct
    rotation: WrappedStruct


class DeadHavenEntrance(FastTravelOutpost):
    map_name = "dlc1_zombieHaven_P"
    outpost_lookup_index = 55
    tp_object= 'dlc1_zombieHaven_P.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "DeadHavenEntranceSave"

    def map_loaded(self):
        return super().map_loaded()


class HallowsEndEntrance(FastTravelOutpost):
    map_name = "dlc1_swamp_ned_p"
    outpost_lookup_index = 56
    tp_object= 'dlc1_swamp_ned_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_1'
    name = "HallowsEndEntranceSave"

    def map_loaded(self):
        outpost_lookup_index = 71
        tp_object= 'dlc1_swamp_ned_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_3'
        name = "HallowsEndTownEntranceSave"
        rotation=make_struct('Rotator',Yaw=-11327)
        fast_travel = find_object('EmergencyTeleportOutpost', tp_object)
        fast_travel.InteractiveObjectDefinition = outpost_def
        fast_travel.OutpostName = name

        outpost_lookup.OutpostLookupList[outpost_lookup_index].OutpostPathName = fast_travel._path_name()#type:ignore

        fast_travel.Rotation = rotation
        
        global last_teleport_station
        if last_teleport_station == name:
            last_teleport_station = ""
            get_pc().WorldInfo.Game.TeleporterDestinationString = tp_object
        return super().map_loaded()


class GenerallyHospitalEntrance(FastTravelOutpost):
    map_name = "dlc1_monsterhouse_p"
    outpost_lookup_index = 57
    tp_object= 'dlc1_monsterhouse_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "GenerallyHospitalEntranceSave"
    rotation = make_struct('Rotator',Yaw=-2783)

    def map_loaded(self):
        return super().map_loaded()


class MillEntrance(FastTravelOutpost):
    map_name = "dlc1_mill_boss_p"
    outpost_lookup_index = 59
    tp_object= 'dlc1_mill_boss_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "MillEntranceSave"
    rotation = make_struct('Rotator',Yaw=59521)
    
    def map_loaded(self):
        return super().map_loaded()
    
                            
class CrimsonTollwayEntrance(FastTravelOutpost):
    map_name = "dlc3_SLanceStrip_p"
    outpost_lookup_index = 60
    tp_object= 'dlc3_SLanceStrip_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "TollwayEntranceSave"
    location=make_struct('Vector',X=101878.1,Y=61417.5,Z=2491.2)
    rotation=make_struct('Rotator',Yaw=-48691)
    
    notes = {
        'dlc3_SLanceStrip_p.TheWorld:PersistentLevel.Note_4': 
            ObjectTransform(
                location=make_struct('Vector',X=101944.5,Y=61657.0,Z=2621.2),
                rotation=make_struct('Rotator',Yaw=-48691)
            ),
        'dlc3_SLanceStrip_p.TheWorld:PersistentLevel.Note_5':
            ObjectTransform(
                location=make_struct('Vector',X=101944.5,Y=61605.3,Z=2621.2),
                rotation=make_struct('Rotator',Yaw=-48691)
            ),
        'dlc3_SLanceStrip_p.TheWorld:PersistentLevel.Note_6':
            ObjectTransform(
                location=make_struct('Vector',X=101944.5,Y=-1130.5,Z=2621.2),
                rotation=make_struct('Rotator',Yaw=-48691)
            ),
        'dlc3_SLanceStrip_p.TheWorld:PersistentLevel.Note_7':
            ObjectTransform(
                location=make_struct('Vector',X=101944.5,Y=-1544.3,Z=2621.2),
                rotation=make_struct('Rotator',Yaw=-48691)
            )
    }
    def map_loaded(self):
        return super().map_loaded()
    

class DeepFathomsEntrance(FastTravelOutpost):
    map_name = "dlc3_southlake_p"
    outpost_lookup_index = 61
    tp_object= 'dlc3_southlake_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_6'
    name = "DeepFathomsEntranceSave"
    rotation=make_struct('Rotator',Yaw=-86238)
    
    def map_loaded(self):
        return super().map_loaded()    


class MoxxisRedLightEntrance(FastTravelOutpost):
    map_name = "dlc3_moxxieplace_p"
    outpost_lookup_index = 62
    tp_object= 'dlc3_moxxieplace_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_1'
    name = "MoxxisRedLightEntranceSave"
    
    def map_loaded(self):
        return super().map_loaded()
    

class CrawmeraxsLairEntrance(FastTravelOutpost):
    map_name = "dlc3_uberboss_p"
    outpost_lookup_index = 63
    tp_object= 'dlc3_uberboss_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "CrawmeraxsLairEntranceSave"
    rotation=make_struct('Rotator',Yaw=-90991)

    def map_loaded(self):
        return super().map_loaded()    


class RoadsEndEntrance(FastTravelOutpost):
    map_name = "dlc3_gondola_p"
    outpost_lookup_index = 64
    tp_object= 'dlc3_gondola_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_16'
    name = "RoadsEndEntranceSave"
    rotation=make_struct('Rotator',Yaw=-85406)

    def map_loaded(self):
        return super().map_loaded()
    

class CrimsonArmoryEntrance(FastTravelOutpost):
    map_name = "dlc3_lancedepot_p"
    outpost_lookup_index = 65
    tp_object= 'dlc3_lancedepot_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "CrimsonArmoryEntranceSave"
    rotation=make_struct('Rotator',Yaw=-4607)

    def map_loaded(self):
        return super().map_loaded()
    

class RidgewayEntrance(FastTravelOutpost):
    map_name = "dlc3_NLanceStrip_p"
    outpost_lookup_index = 66
    tp_object= 'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_3'
    name = "RidgewayEntranceSave"
    rotation=make_struct('Rotator',Yaw=-64895)

    def map_loaded(self):
        outpost_lookup_index = 72
        tp_object= 'dlc3_NLanceStrip_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
        name = "RidgewayMidpointEntranceSave"
        rotation=make_struct('Rotator',Yaw=-23871)
        fast_travel = find_object('EmergencyTeleportOutpost', tp_object)
        fast_travel.InteractiveObjectDefinition = outpost_def
        fast_travel.OutpostName = name

        outpost_lookup.OutpostLookupList[outpost_lookup_index].OutpostPathName = fast_travel._path_name()#type:ignore

        fast_travel.Rotation = rotation
        
        global last_teleport_station
        if last_teleport_station == name:
            last_teleport_station = ""
            get_pc().WorldInfo.Game.TeleporterDestinationString = tp_object
        return super().map_loaded()    


class SunkenSeaEntrance(FastTravelOutpost):
    map_name = "dlc3_lakebed_p"
    outpost_lookup_index = 67
    tp_object= 'dlc3_lakebed_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "SunkenSeaEntranceSave"
    rotation=make_struct('Rotator',Yaw=-87071)

    def map_loaded(self):
        return super().map_loaded()


class CircleOfDutyEntrance(FastTravelOutpost):
    map_name = "dlc3_circle_p"
    outpost_lookup_index = 68
    tp_object= 'dlc3_circle_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_1'
    name = "CircleOfDutyEndEntranceSave"

    def map_loaded(self):
        return super().map_loaded()


class PrisonEntrance(FastTravelOutpost):
    map_name = "dlc3_prison_p"
    outpost_lookup_index = 69
    tp_object= 'dlc3_prison_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_1'
    name = "PrisonEntranceSave"
    rotation=make_struct('Rotator',Yaw=-87071)

    def map_loaded(self):
        return super().map_loaded()
    
class LumberYardEntranceEntrance(FastTravelOutpost):
    map_name = "dlc1_mill_p"
    outpost_lookup_index = 70
    tp_object= 'dlc1_mill_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_3'
    name = "LumberYardEntranceSave"
    rotation=make_struct('Rotator',Yaw=-27744)
    
    def map_loaded(self):
        outpost_lookup_index = 58
        tp_object= 'dlc1_mill_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_5'
        name = "LumberYardBridgeEntranceSave"
        fast_travel = find_object('EmergencyTeleportOutpost', tp_object)
        fast_travel.InteractiveObjectDefinition = outpost_def
        fast_travel.OutpostName = name

        outpost_lookup.OutpostLookupList[outpost_lookup_index].OutpostPathName = fast_travel._path_name()#type:ignore

        fast_travel.Rotation = make_struct('Rotator',Yaw=-15423)
        
        global last_teleport_station
        if last_teleport_station == name:
            last_teleport_station = ""
            get_pc().WorldInfo.Game.TeleporterDestinationString = tp_object
        return super().map_loaded()


class TartarusStationTown(FastTravelOutpost):
    map_name = "DLC4_Tartarus_Station_p"
    outpost_lookup_index = 73
    tp_object= 'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_7'
    name = "tartarusstationtown"
    location=make_struct('Vector',X=3668.6,Y=-1869.5,Z=2122.8)
    rotation=make_struct('Rotator',Yaw=59428)
    
    notes = {
        'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_32': 
            ObjectTransform(
                location=make_struct('Vector',X=3628.0,Y=-714.0,Z=2208.8),
                rotation=make_struct('Rotator',Yaw=40580)
            ),
        'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_35':
            ObjectTransform(
                location=make_struct('Vector',X=3831.7,Y=-928.9,Z=2208.8),
                rotation=make_struct('Rotator',Yaw=40682)
            ),
        'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_34':
            ObjectTransform(
                location=make_struct('Vector',X=4022.7,Y=-1130.5,Z=2211.6),
                rotation=make_struct('Rotator',Yaw=40682)
            ),
        'DLC4_Tartarus_Station_p.TheWorld:PersistentLevel.Note_33':
            ObjectTransform(
                location=make_struct('Vector',X=4090.9,Y=-1544.3,Z=2208.8),
                rotation=make_struct('Rotator',Yaw=40989)
            )
    }
    def map_loaded(self):
        return super().map_loaded()
    

class HyperionDump(FastTravelOutpost):
    map_name = "DLC4_Hyperion_Dump_p"
    outpost_lookup_index = 74
    tp_object= 'DLC4_Hyperion_Dump_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "HDFastTravel"

    def map_loaded(self):
        return super().map_loaded()
    

class SanderGorge(FastTravelOutpost):
    map_name = "DLC4_Sanders_Gorge_p"
    outpost_lookup_index = 75
    tp_object= 'DLC4_Sanders_Gorge_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_2'
    name = "SGFastTravel"
    rotation=make_struct('Rotator',Yaw=-65343)

    def map_loaded(self):
        return super().map_loaded()    


class DividingFaults(FastTravelOutpost):
    map_name = "DLC4_Dividing_Faults_p"
    outpost_lookup_index = 76
    tp_object= 'DLC4_Dividing_Faults_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_0'
    name = "DFFastTravel"
    rotation=make_struct('Rotator',Yaw=57248)

    def map_loaded(self):
        return super().map_loaded()


class ScorchedSnakeCanyon(FastTravelOutpost):
    map_name = "DLC4_SS_Canyon_p"
    outpost_lookup_index = 77
    tp_object= 'DLC4_SS_Canyon_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_2'
    name = "SSCFastTravel"
    rotation=make_struct('Rotator',Yaw=33637)

    def map_loaded(self):
        return super().map_loaded()


class WaywardPass(FastTravelOutpost):
    map_name = "DLC4_Wayward_Pass_p"
    outpost_lookup_index = 78
    tp_object= 'DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_2'
    name = "WaywardPassfasttravel"

    def map_loaded(self):
        return super().map_loaded()


class AridBadlandsRobo(FastTravelOutpost):
    map_name = "DLC4_Arid_Badlands_p"
    outpost_lookup_index = 79
    tp_object= 'DLC4_Arid_Badlands_p.TheWorld:PersistentLevel.EmergencyTeleportOutpost_11'
    name = "ABCFastTravel"
    rotation=make_struct('Rotator',Yaw=47068)

    def map_loaded(self):
        return super().map_loaded()




build_mod(on_enable=FirstTimeStartup)
        



