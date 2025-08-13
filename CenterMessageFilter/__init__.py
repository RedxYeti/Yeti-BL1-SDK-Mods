from mods_base import build_mod, hook, BoolOption,NestedOption, get_pc
from unrealsdk import make_struct, find_object, load_package, find_class
from unrealsdk.hooks import Type,Block,prevent_hooking_direct_calls
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction,IGNORE_STRUCT

from .rules import all_rules

from typing import Any
import random 
import math

player_pools = [
    "HealthPool",
    "ShieldPool",
    "Ammo_Patrol_SMG_Pool",
    "Ammo_Repeater_Pistol_Pool",
    "Ammo_Sniper_Rifle_Pool",
    "Ammo_Grenade_Protean_Pool",
    "Ammo_Combat_Rifle_Pool",
    "Ammo_Revolver_Pistol_Pool",
    "Ammo_Rocket_Launcher_Pool",
    "Ammo_Combat_Shotgun_Pool",
]


def keep_alive(in_object:UObject) -> None:
    in_object.ObjectFlags |= 0x4000
    return



@hook("WillowGame.WillowPlayerController:ClientColiseumNotify", Type.PRE)
def ClientColiseumNotify(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    if _args.NotifyType == 2:
        for pool in obj.ResourcePoolManager.ResourcePools:
            if pool and str(pool.Definition.Name) in player_pools:
                pool.CurrentValue = pool.MaxValue
        
        if oidResetCooldowns.value and obj.SkillCooldownPool and obj.SkillCooldownPool.Data:
            obj.SkillCooldownPool.Data.SetCurrentValue(0)

    return


@hook("WillowGame.WillowPlayerController:ClientStartColiseumTimer", Type.PRE)
def ClientStartColiseumTimer(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    if _args.CountdownLength == 1:
        with prevent_hooking_direct_calls():
            _func(6)
            return Block
    return



arena_names = ["dlc2_lobby_p","dlc2_hellburb_p", "dlc2_Gully_P", "dlc2_ruins_p"]
@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def PreCommitMapChange(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    if _args.NextMapName not in arena_names:
        return

    #classic gearbox, each map is just slightly different
    if _args.NextMapName == "dlc2_hellburb_p":
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_0').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_3').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.Rules_UI.SeqAct_Delay_6').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.WaveStructure.SeqAct_Delay_14').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.WaveStructure.SeqAct_Delay_25').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_0').Duration = 3
        find_object('SeqAct_Delay','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_5').Duration = 0

        find_object('SeqEvent_RemoteEvent','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.LootSpawning.SeqEvent_RemoteEvent_1').bEnabled=False
        find_object('SeqEvent_RemoteEvent','dlc2_hellburb_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.RoundLootReward.SeqEvent_RemoteEvent_35').bEnabled=False
    
    elif _args.NextMapName == "dlc2_Gully_P":
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_0').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_3').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.Wave_Structure.SeqAct_Delay_14').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.Wave_Structure.SeqAct_Delay_25').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_0').Duration = 3
        find_object('SeqAct_Delay','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_5').Duration = 0

        find_object('SeqEvent_RemoteEvent','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.LootSpawn.SeqEvent_RemoteEvent_1').bEnabled=False
        find_object('SeqEvent_RemoteEvent','dlc2_Gully_P.TheWorld:PersistentLevel.Main_Sequence.FightStructure.RoundLootReward.SeqEvent_RemoteEvent_35').bEnabled=False 

    elif _args.NextMapName == "dlc2_ruins_p":
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_0').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.SeqAct_Delay_3').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.WaveStructure.SeqAct_Delay_1').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.WaveStructure.SeqAct_Delay_25').Duration = 0.25
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_0').Duration = 3
        find_object('SeqAct_Delay','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.TimeBetweenRounds.SeqAct_Delay_5').Duration = 0

        find_object('SeqEvent_RemoteEvent','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.LootSpawning.SeqEvent_RemoteEvent_1').bEnabled=False
        find_object('SeqEvent_RemoteEvent','dlc2_ruins_p.TheWorld:PersistentLevel.Main_Sequence.FightStructure.RoundLootReward.SeqEvent_RemoteEvent_35').bEnabled=False
    
    elif _args.NextMapName == "dlc2_lobby_p":
        global got_certificate
        if got_certificate[0]:
            hud_opened.enable()

    return

got_certificate = [False,0]
@hook("WillowGame.WillowPlayerController:ServerCertificateClosed", Type.PRE)
def ServerCertificateClosed(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    global got_certificate
    if oidBetterLoot.value:
        got_certificate = [True, obj.myHUD.ColiseumOverlayMovie.CachedMaxRound]


@hook("WillowGame.WillowHUD:OpenHUDMovie", Type.POST)
def hud_opened(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    global got_certificate
    load_package("dlc3_uberboss_Dynamic")
    drop_amount = 1 if got_certificate[1] == 5 else 3
    for i in range(drop_amount):
        spawn_loot()
    got_certificate = [False,0]
    hud_opened.disable()


def rotate_yaw(vec, yaw_deg):
    rad = math.radians(yaw_deg)
    x = vec.X
    y = vec.Y
    z = vec.Z
    return make_struct(
        "Vector",
        X=x * math.cos(rad) - y * math.sin(rad),
        Y=x * math.sin(rad) + y * math.cos(rad),
        Z=z
    )


ItemScatterOffset = make_struct("Vector", X=40, Y=0, Z=0)
loot_loc = make_struct("Vector", X=7676,Y=-4901,Z=-81)
def spawn_loot():
    ItemPools = []
    behavior = find_object("SeqAct_ApplyBehavior","dlc3_uberboss_Dynamic.TheWorld:PersistentLevel.Main_Sequence.SeqAct_ApplyBehavior_5").Behaviors[0]
    ItemPoolList = behavior.ItemPoolList
    for PoolIndex, pool in enumerate(ItemPoolList):
        PoolChance = random.random()
        EvaluatedPoolProbability = find_class('AttributeInitializationDefinition').ClassDefaultObject.EvaluateInitializationData(ItemPoolList[PoolIndex].PoolProbability, get_pc().Pawn)
        if((EvaluatedPoolProbability > 0) and PoolChance <= EvaluatedPoolProbability):
            ItemPools.append(ItemPoolList[PoolIndex].ItemPool)
        

    for Pool in ItemPools:
        _, SpawnedInventory = find_class('ItemPool').ClassDefaultObject.SpawnBalancedInventoryFromPool(Pool, get_pc().Pawn.GetExpLevel(), int(get_pc().Pawn.GetExpLevel() * 2.5), get_pc().Pawn, [])                  
        for Inv in SpawnedInventory:
            yaw_deg = (random.randint(0, 32767) * 2)

            DropOffset = rotate_yaw(ItemScatterOffset, yaw_deg)

            drop_position = make_struct(
                "Vector",
                X=loot_loc.X + DropOffset.X,
                Y=loot_loc.Y + DropOffset.Y,
                Z=loot_loc.Z + DropOffset.Z,
            )

            Inv.GetPickup(True, True)
            Inv.DropFrom(drop_position, IGNORE_STRUCT, Pool.bDisablePhysicsDrop)



@hook("WillowGame.Behavior_PlayCharacterSound:ApplyBehaviorToContext", Type.PRE)
def Behavior_PlayCharacterSound(obj:UObject, _args:WrappedStruct, _ret:Any, _func:BoundFunction) -> Any:
    if oidMuteMoxxi.value and obj.DialogType and "dlc2_gd_announcer" in str(obj.DialogType):
        return Block


def option_change(option, new_value):
    if new_value:
        match option.identifier:
            case "XP Gain":
                load_package("dlc2_gd_skills_BigTop")
                xp_skill = find_object("SkillDefinition","dlc2_gd_skills_BigTop.Rule_Colleseum.GameRule_M_EnemyModifiers")
                if len(xp_skill.SkillEffectDefinitions) >= 7:
                    xp_skill.SkillEffectDefinitions.pop(6)
                    keep_alive(xp_skill)

    return


def crowd_setting(option, new_value):
    load_package("dlc2_ambient_audio")
    load_package("dlc2_Crowd")
    Willow_DLC2_CrowdLoopCue = find_object("SoundCue","dlc2_ambient_audio.Willow_DLC2_CrowdLoopCue")
    DLC2_BD_Crowd_LIVE_CheerHigh_MEDCue = find_object("SoundCue", "dlc2_Crowd.DLC2_BD_Crowd_LIVE_CheerHigh_MEDCue")
    DLC2_BD_Crowd_LIVE_CheerHighCue = find_object("SoundCue", "dlc2_Crowd.DLC2_BD_Crowd_LIVE_CheerHighCue")
    DLC2_BD_Crowd_Live_CheerLowCue = find_object("SoundCue", "dlc2_Crowd.DLC2_BD_Crowd_Live_CheerLowCue")
    DLC2_BD_Crowd_LIVE_CheerHigh_SHRTCue = find_object("SoundCue", "dlc2_Crowd.DLC2_BD_Crowd_LIVE_CheerHigh_SHRTCue")

    sound_cues = [
        Willow_DLC2_CrowdLoopCue,
        DLC2_BD_Crowd_LIVE_CheerHigh_MEDCue,
        DLC2_BD_Crowd_LIVE_CheerHighCue,
        DLC2_BD_Crowd_Live_CheerLowCue,
        DLC2_BD_Crowd_LIVE_CheerHigh_SHRTCue,
    ]

    for cue in sound_cues:
        cue.VolumeMultiplier = -1 if new_value else 0.5
        keep_alive(cue)
    return


oidResetCooldowns = BoolOption(
    "Reset Action Skill",
    False,
    "On",
    "Off",
    description="Refills your action skill when waves finish.",
)

oidXPGain = BoolOption(
    "XP Gain",
    False,
    "On",
    "Off",
    description="Enables XP Gain. Requires restart to disable.",
    on_change=option_change
)

oidBetterLoot = BoolOption(
    "Better Loot",
    False,
    "On",
    "Off",
    description="Adds good loot to the Underdome lobby by the stage after you finish a full set.",
    on_change=option_change
)

oidMuteMoxxi = BoolOption(
    "Mute Moxxi",
    False,
    "On",
    "Off",
    description="Turns off all Moxxi dialog.",
)

oidMuteAmbientCrowd = BoolOption(
    "Mute Ambient Crowd",
    False,
    "On",
    "Off",
    description="Mutes the constant screaming crowd sounds, not the callouts that react to playing.",
    on_change=crowd_setting
)

oidRules = NestedOption("Change Rules", rules.all_rules)

build_mod(options=[oidRules,oidResetCooldowns,oidXPGain,oidBetterLoot,oidMuteMoxxi,oidMuteAmbientCrowd])
hud_opened.disable()
