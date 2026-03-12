from mods_base import build_mod, get_pc, keybind, hook, BoolOption, SliderOption
from unrealsdk import find_class, make_struct
from unrealsdk.hooks import Type, Block, prevent_hooking_direct_calls
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, UClass
from typing import Any


def update_blacklist(option: BoolOption, new_value) -> None:
    class_to_change = message_classes[option.identifier]
    if new_value:
        if class_to_change in class_blacklist:
            class_blacklist.remove(class_to_change)
    else:
        class_blacklist.append(class_to_change)
    return

oidMaxDuration: SliderOption = SliderOption(
    "Max Message Duration",
    10,
    0,
    10,
    0.5,
    False,
    description=f"Set the maximum amount of time a message is allowed to show.\n0 will turn off all messages.\nMost messages are less than 7 seconds.",
)

oidMoney: BoolOption = BoolOption(
    "Money",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidAmmo: BoolOption = BoolOption(
    "Ammo",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidWeapons: BoolOption = BoolOption(
    "Weapons",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidGear: BoolOption = BoolOption(
    "Gear",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidNewMissions: BoolOption = BoolOption(
    "New Missions",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidMissionUpdates: BoolOption = BoolOption(
    "Mission Updates",
    True,
    "Show",
    "Hide",
)

oidChallenges: BoolOption = BoolOption(
    "Challenges",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidWeaponProf: BoolOption = BoolOption(
    "Weapon Proficiencies",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidSkillPoints: BoolOption = BoolOption(
    "Skill Points",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidOutposts: BoolOption = BoolOption(
    "Outpost Discovery",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidLevelUp: BoolOption = BoolOption(
    "Level Up",
    True,
    "Show",
    "Hide",
    on_change=update_blacklist
)

oidMissionDrops: BoolOption = BoolOption(
    "Mission Drops",
    True,
    "Show",
    "Hide",
)

oidShops: BoolOption = BoolOption(
    "Shops",
    True,
    "Show",
    "Hide",
)

message_classes: dict = {
    "Money": find_class("ReceivedCreditsMessage"),
    "Ammo": find_class("ReceivedAmmoMessage"),
    "Weapons": find_class("ReceivedWeaponMessage"),
    "Gear": find_class("ReceivedItemMessage"),
    "New Missions": find_class("MissionFeedbackMessage"),
    "Challenges": find_class("ChallengeFeedbackMessage"),
    "Weapon Proficiencies": find_class("WeaponProficiencyFeedbackMessage"),
    "Skill Points": find_class("SkillPointsFeedbackMessage"),
    "Outpost Discovery": find_class("OutpostDiscoveryMessage"),
    "Level Up": find_class("ExperienceFeedbackMessage"),
}

class_blacklist: list = []

@hook("WillowGame.WillowPlayerController:DisplayHUDMessage", Type.PRE)
def DisplayHUDMessage(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> Any:
    if oidMaxDuration.value <= 0:
        return

    if args.InMessageClass in class_blacklist:
        return Block
    
    #some messages dont have a class
    if not oidMissionUpdates.value and args.MsgType == 4:
        #this iterates over active missions to see if the objective is in the message string
        for mission in obj.WorldInfo.Game.MissionTracker.MissionList:
            for objective in mission.Objectives:
                if objective.ProgressMessage in args.MessageString:
                    return Block
    
    
    if (args.InMessageClass == message_classes["Gear"] 
        and oidGear.value
        and not oidMissionDrops.value):
        for mission in obj.WorldInfo.Game.MissionTracker.MissionList:
            for objective in mission.Objectives:
                progress_message = str(objective.ProgressMessage)
                if ":" in progress_message and progress_message.split(":")[0] in args.MessageString:
                    return Block

    
    if not oidShops.value and args.MessageString == 'Shops have new inventory!':
        return Block

    #print(f"{args.MsgType} >>>> {args.MessageString} >>>> {args.InMessageClass}")
    return


@hook("WillowGame.WillowHUDGFxMovie:AddCriticalText", Type.PRE)
def AddCriticalText(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> Any:
    if args.Duration > oidMaxDuration.value:
        with prevent_hooking_direct_calls():
            args.Duration = oidMaxDuration.value
            func(args)
            return Block


@keybind("Clear Center Messages")
def clear_messages() -> None:
    if not get_pc() or not get_pc().myHUD or not get_pc().myHUD.GetHUDMovie():
        return
    
    message_array = get_pc().myHUD.GetHUDMovie().CriticalTextMessages[0].MessageArray
    for message in message_array:
        message.DestroyTime = 0
    return


build_mod(options=[oidMaxDuration,
                   oidMoney,
                   oidAmmo,
                   oidWeapons,
                   oidGear,
                   oidNewMissions,
                   oidMissionUpdates,
                   oidMissionDrops,
                   oidChallenges,
                   oidLevelUp,
                   oidWeaponProf,
                   oidSkillPoints,
                   oidShops,
                   oidOutposts,])
