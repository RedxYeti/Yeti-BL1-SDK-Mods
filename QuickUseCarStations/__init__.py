from unrealsdk import find_object, find_class, make_struct, load_package #type: ignore
from unrealsdk.hooks import Type #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction #type: ignore
from mods_base import build_mod, keybind, hook, SpinnerOption, BoolOption #type: ignore
from ui_utils import show_hud_message #type: ignore

oidVehicleType: SpinnerOption = SpinnerOption("Vehicle Type",
                                                value="Rocket Runner",
                                                choices=["Rocket Runner", "MG Runner", "Cheta Paw", "Racer", "Lancer"],
                                                wrap_enabled = True,
                                                description="Choose what vehicle spawns.")


oidShowMessage = BoolOption(
    "Show Message",
    True,
    "On",
    "Off",
    description="Enable or disable the message that shows when you look at a car station."
)


LastKnownColorIndex: int = -1

bLookingAtStation: bool = False
bStartedUp: bool = False

CurrentPC: UObject = None
CurrentStation: UObject = None
BaseStation: UObject = None
DLCStation: UObject = None

VehicleDefinitions: dict = {}


def FirstTimeStartup() -> None:
    global BaseStation, DLCStation, VehicleDefinitions
    load_package("ui_vehicle_spawn_station")
    BaseStation = find_object("VehicleSpawnStationGFxDefinition", "ui_vehicle_spawn_station.Definitions.VSSMovieDefinition")
    BaseStation.ObjectFlags |= 0x4000
    load_package("dlc3_gd_vehiclespawnstation")
    DLCStation = find_object("VehicleSpawnStationGFxDefinition", "dlc3_gd_vehiclespawnstation.Definitions.dlc3_VSSMovieDefinition")
    DLCStation.ObjectFlags |= 0x4000
    VehicleDefinitions = {
        "Rocket Runner": BaseStation.VehicleTypes[0],
        "MG Runner": BaseStation.VehicleTypes[1],
        "Cheta Paw": DLCStation.VehicleTypes[0],
        "Racer" : DLCStation.VehicleTypes[1],
        "Lancer" : DLCStation.VehicleTypes[2],
    }
    return


def GetPlayerVehicleOptions(PC:UObject, SlotIndex:int):
    global VehicleDefinitions, BaseStation, DLCStation, LastKnownColorIndex
    if LastKnownColorIndex == -1:
        LastKnownColorIndex = PC.GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(0).VSS_ColorChoice[SlotIndex]

    if oidVehicleType.value == "Rocket Runner" or oidVehicleType.value == "MG Runner":
        CarMaterial = BaseStation.VehicleMaterials[LastKnownColorIndex].Material
    else:
        if oidVehicleType.value == "Cheta Paw":
            CarMaterial =  DLCStation.VehicleMaterials[LastKnownColorIndex].Material
        elif oidVehicleType.value == "Racer":
            CarMaterial = DLCStation.VehicleMaterials[LastKnownColorIndex + 8].Material
        else:
            CarMaterial = DLCStation.VehicleMaterials[LastKnownColorIndex + 16].Material

    return VehicleDefinitions[oidVehicleType.value], CarMaterial


def FinalizeCarSpawn(AvailableCarIndex) -> None:
    global CurrentPC, CurrentStation, bLookingAtStation
    Car, Material  = GetPlayerVehicleOptions(CurrentPC, AvailableCarIndex)

    find_class("GearboxFramework.GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster().DespawnVehicleFromVehicleSpawnStation(AvailableCarIndex)
    
    CurrentPC.StartUsingVehicleSpawnStationTerminal(CurrentStation)

    CurrentPC.SpawnVehicleFromConnectedVehicleSpawnStationTerminal(AvailableCarIndex, Car, Material)
    
    CurrentPC.ServerTryToTeleportToVehicle(AvailableCarIndex, False)

    CurrentPC.Pawn.SetViewRotation(CurrentStation.SpawnPlatforms[AvailableCarIndex].Rotation)

    if oidShowMessage.value:
        CurrentPC.myHUD.GetHUDMovie().ClearTrainingText(0)
        CurrentPC.myHUD.GetHUDMovie().ClearTrainingText(1)

    bLookingAtStation = False
    CurrentStation = None
    CurrentPC = None
    return


@keybind("Spawn Car")
def KeyBindHit() -> None:
    global bLookingAtStation, CurrentPC, CurrentStation 
    if not bLookingAtStation or not CurrentPC or not CurrentStation:
        return
    
    global bStartedUp

    if not bStartedUp:
        FirstTimeStartup()

    PopMaster = find_class("GearboxFramework.GearboxGlobals").ClassDefaultObject.GetGearboxGlobals().GetPopulationMaster()

    VehicleInSlot0 = PopMaster.GetVehicleFromVehicleSpawnStation(0)
    VehicleInSlot1 = PopMaster.GetVehicleFromVehicleSpawnStation(1)

    if not VehicleInSlot0 and not VehicleInSlot1:
        FinalizeCarSpawn(0)
        return
    
    if VehicleInSlot0 and VehicleInSlot0.NumPassengers() == 0:
        FinalizeCarSpawn(0)
        return
    
    if VehicleInSlot0 and not VehicleInSlot1:
        FinalizeCarSpawn(1)
        return
    
    if VehicleInSlot0 and VehicleInSlot1 and VehicleInSlot1.NumPassengers() == 0:
        FinalizeCarSpawn(1)
        return

    #hail mary to put player into a gunner seat
    if VehicleInSlot0 and VehicleInSlot0.NumPassengers() == 1:
        CurrentPC.ServerTryToTeleportToVehicle(0, True)
        bLookingAtStation = False
        CurrentPC = None
        CurrentStation = None
        return
    
    if VehicleInSlot1 and VehicleInSlot1.NumPassengers() == 1:
        CurrentPC.ServerTryToTeleportToVehicle(1, True)
        bLookingAtStation = False
        CurrentPC = None
        CurrentStation = None
        return
    
    bLookingAtStation = False
    CurrentPC = None
    CurrentStation = None
    return


@hook("WillowGame.VehicleSpawnStationGFxMovie:extUpdateColorBox", Type.POST)
def ColorChange(obj: UObject, __args: WrappedStruct, __ret: any, __func: BoundFunction) -> None:
    global LastKnownColorIndex
    LastKnownColorIndex = __args.CellIndex
    return


@hook("WillowGame.WillowHUDGFxMovie:ShowToolTip", Type.POST)
def ShowToolTip(obj: UObject, __args: WrappedStruct, __ret: any, __func: BoundFunction) -> None:
    global bLookingAtStation, CurrentPC, CurrentStation
    if __args.HUDIcon == 1:
        CurrentPC = obj.WPlayerOwner[0]
        CarStation = CurrentPC.CurrentUsableObject
        
        if not CarStation or CarStation.Class.Name != "VehicleSpawnStationTerminal":
            return
        
        bLookingAtStation = True
        CurrentPC = obj.WPlayerOwner[0]
        CurrentStation = CarStation
        if oidShowMessage.value:
            show_hud_message("Quick Use Car Stations", f"Spawn {oidVehicleType.value}?", 999999)

    elif __args.HUDIcon == 0 and bLookingAtStation:
        CurrentPC = None
        CurrentStation = None
        bLookingAtStation = False
        if oidShowMessage.value:
            obj.ClearTrainingText(0)
            obj.ClearTrainingText(1)

    return

build_mod()
