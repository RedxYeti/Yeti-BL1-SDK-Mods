from unrealsdk import find_all, load_package,make_struct,find_object,find_class
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction,WeakPointer
from mods_base import hook, get_pc, SliderOption, build_mod,BoolOption,ObjectFlags,command
from typing import Any

def keep_alive(in_object:UObject):
    in_object.ObjectFlags |= 0x4000
    return

set_knoxx = False

def knoxx_enabled(option, new_value):
    global set_knoxx
    if new_value and not set_knoxx:
        set_knoxx = True
        load_package("dlc3_gd_itempools")
        load_package("gd_itempools")

        load_package("gd_CommandDecks")
        load_package("dlc3_gd_CommandDecks")
        brick_coms = find_object("ItemPartListDefinition", "gd_CommandDecks.Body_Brick.BodyParts_Brick")
        lilith_coms = find_object("ItemPartListDefinition", "gd_CommandDecks.Body_Lilith.BodyParts_Lilith")
        mord_coms = find_object("ItemPartListDefinition", "gd_CommandDecks.Body_Mordecai.BodyParts_Mordecai")
        roland_coms = find_object("ItemPartListDefinition", "gd_CommandDecks.Body_Roland.BodyParts_Roland")
        keep_alive(brick_coms)
        keep_alive(lilith_coms)
        keep_alive(mord_coms)
        keep_alive(roland_coms)

        rare_def = find_object('AttributeInitializationDefinition','gd_Balance.Weighting.Weight_Awesome_5_VeryRare')

        for part in find_object("ItemPartListDefinition", "dlc3_gd_CommandDecks.Body_Loyalty.BodyParts_Brick").WeightedParts:
            brick_coms.WeightedParts.append(part)
        brick_coms.WeightedParts.append(brick_coms.WeightedParts[-1])
        brick_coms.WeightedParts[-1].Part = find_object("ItemPartDefinition", "dlc3_gd_CommandDecks.Body_Command.Brick_Torgue_Ogre")
        brick_coms.WeightedParts[-1].Manufacturers[0].Manufacturer = None

        for part in find_object("ItemPartListDefinition", "dlc3_gd_CommandDecks.Body_Loyalty.BodyParts_Lilith").WeightedParts:
            lilith_coms.WeightedParts.append(part)
        lilith_coms.WeightedParts.append(lilith_coms.WeightedParts[-1])
        lilith_coms.WeightedParts[-1].Part = find_object("ItemPartDefinition", "dlc3_gd_CommandDecks.Body_Command.Lilith_Hyperion_Specter")
        lilith_coms.WeightedParts[-1].Manufacturers[0].Manufacturer = None

        for part in find_object("ItemPartListDefinition", "dlc3_gd_CommandDecks.Body_Loyalty.BodyParts_Mordecai").WeightedParts:
            mord_coms.WeightedParts.append(part)
        mord_coms.WeightedParts.append(mord_coms.WeightedParts[-1])
        mord_coms.WeightedParts[-1].Part = find_object("ItemPartDefinition", "dlc3_gd_CommandDecks.Body_Command.Mordecai_SandS_Truxican")
        mord_coms.WeightedParts[-1].Manufacturers[0].Manufacturer = None

        for part in find_object("ItemPartListDefinition", "dlc3_gd_CommandDecks.Body_Loyalty.BodyParts_Roland").WeightedParts:
            roland_coms.WeightedParts.append(part)
        roland_coms.WeightedParts.append(roland_coms.WeightedParts[-1])
        roland_coms.WeightedParts[-1].Part = find_object("ItemPartDefinition", "dlc3_gd_CommandDecks.Body_Command.Roland_Dahl_Marine")
        roland_coms.WeightedParts[-1].Manufacturers[0].Manufacturer = None

        for character_coms in [brick_coms,lilith_coms,mord_coms,roland_coms]:
            for part in character_coms.WeightedParts:
                if "dlc3" in str(part.part):
                    part.Manufacturers[0].DefaultWeight.InitializationDefinition = rare_def


oidKnoxxItems = BoolOption(
    "Knoxx Classmods",
    False,
    "On",
    "Off",
    description="Adds Knoxx class mods to everything.",
    on_change=knoxx_enabled,
)

block_xp_gain = False
def block_xp_gain_toggled(option, new_value):
    global block_xp_gain
    block_xp_gain = new_value
    value = 0 if new_value else 1
    get_pc().ConsoleCommand(f"set ExperienceResourcePool ExpAllPointsScale {value}")

@command("togglexp")
def toggle_xp(args):
    global block_xp_gain
    block_xp_gain = not block_xp_gain
    oidBlockXPGain.value = block_xp_gain
    value = 0 if block_xp_gain else 1
    message = "Off" if block_xp_gain else "On"
    get_pc().ConsoleCommand(f"set ExperienceResourcePool ExpAllPointsScale {value}")
    print(f"[Yeti's QoL Patch] XP Gain: {message}")
    mod.save_settings()



oidBlockXPGain = BoolOption(
    "Block XP Gain",
    False,
    "On",
    "Off",
    description=f"Stops XP Gain.",
    on_change=block_xp_gain_toggled
)

def slowdown_toggle(option, new_value):
    value = "TotalEncumbrance" if new_value else ""
    encumbrance = find_object("AttributeDefinition","d_attributes.Encumbrance.TotalEncumbrance")
    encumbrance.ValueResolverChain[0].PropertyName = value


oidEridianSlowdown = BoolOption(
    "Eridian Slowdown",
    False,
    "On",
    "Off",
    description="Disables the movement speed penatly on eridian weapons.",
    on_change=slowdown_toggle
)

#def add_berserk_boost(option, new_value):
#    #berserk_boost = find_object("SkillDefinition","gd_Skills_Brick.Action.A_Berserk_BerserkBoost")
#    #berserk_boost.SkillEffectDefinitions[0].ModifierType = 1
#    #berserk_boost.SkillEffectDefinitions[0].BaseModifierValue.BaseValueConstant = -12000 if new_value else -40
#    berserk_boost = find_object("AttributeInitializationDefinition","gd_Skills2_Brick.MiscData.Berserk_init_HealthRegen")
#    berserk_boost.ValueFormula.Multiplier.BaseValueScaleConstant = 1.5 if new_value else 0.03
#
#oidBetterBerserk = BoolOption(
#    "Better Initial Berserk Health",
#    False,
#    "On",
#    "Off",
#    description="With this on, starting Berserk will add much more HP."
#)

@hook("WillowGame.WillowWeapon:AttachMuzzleFlash", Type.PRE)
def QOLSlop_AttachMuzzleFlash(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if MuzzleFlashScaler.value < 100:
        obj.FirstPersonMuzzleFlash.SetScale(MuzzleFlashScaler.value/100)
    return

MuzzleFlashScaler = SliderOption(
    "Muzzle Flash Scale",
    100,
    0,
    100,
    1,
    description=f"Control the scale of muzzle flashes, 50 would be 50% scale."
)


def set_ffyl(option, new_value):
    injured_def = find_object("InjuredDefinition","gd_PlayerShared.injured.PlayerInjuredDefinition")
    keep_alive(injured_def)
    if new_value:
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.X = 0
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Y = 0
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Z = 0
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.X = 0
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Y = 0
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Z = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.X = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Y = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Z = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.X = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Y = 0
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Z = 0
    else:
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.X = 1.5
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Y = 1.5
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Z = 1.5
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.X = 0.9
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Y = 1.4
        injured_def.MultiPlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Z = 1.4
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.X = 1.5
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Y = 1.5
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_Highlights.Z = 1.5
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.X = 0.9
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Y = 1.4
        injured_def.SinglePlayerTargetedBehaviors[0].OverlayParameters.DestPostProcessOverlay.Scene_MidTones.Z = 1.4

oidDarkFFYL = BoolOption(
    "Dark FFYL",
    False,
    "On",
    "Off",
    description="Removes the screen getting darker while in FFYL. Does not disable other screen effects.",
    on_change=set_ffyl
)

more_nades_set = False
def more_nades(option, new_value):
    global more_nades_set
    if new_value and not more_nades_set:
        more_nades_set = False
        load_package("gd_balance_shopping")
        load_package("dlc1_gd_balance_shopping")

        ammo_machine_vanilla = find_object('InteractiveObjectBalanceDefinition','gd_balance_shopping.VendingMachineGrades.ObjectGrade_VendingMachine_GrenadesAndAmmo')
        keep_alive(ammo_machine_vanilla)
        ammo_machine_zombies = find_object('InteractiveObjectBalanceDefinition','dlc1_gd_balance_shopping.VendingMachineGrades.dlc1_ObjectGrade_VendingMachine_GrenadesAndAmmo')
        keep_alive(ammo_machine_zombies)

        grenade_pool = ammo_machine_vanilla.DefaultLoot[1].ItemAttachments[0].ItemPool

        attachments_struct = make_struct("LootAttachmentData",
                                        ItemPool=grenade_pool)
        
        attachments_struct.PoolProbability.BaseValueConstant = 1
        attachments_struct.PoolProbability.BaseValueScaleConstant = 1

        for i in range(5):
            ammo_machine_vanilla.DefaultLoot[0].ItemAttachments.append(attachments_struct)
            ammo_machine_zombies.DefaultLoot[0].ItemAttachments.append(attachments_struct)

oidMoreNadeMods = BoolOption(
    "More Nade Mods",
    False,
    "On",
    "Off",
    description="Adds more grenade mods to ammo vendors, similar to bl2.",
    on_change=more_nades
)



@hook("WillowGame.WillowPawn:TakeFallingDamage", Type.PRE)
def QOLSlop_TakeFallingDamage(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if oidFallDamage.value:
        return Block
    
oidFallDamage = BoolOption(
    "Fall Damage",
    False,
    "On",
    "Off",
    description="Removes all fall damage."
)
    
def speed_skills(option, new_value):

    intuition = find_object('SkillDefinition','gd_Skills2_Lilith.Elemental.Intuition')
    intuition_speed = intuition.SkillEffectDefinitions[0]
    intuition_presentation = intuition.SkillEffectPresentations[0]
    cauterize = find_object('SkillDefinition','gd_skills2_Roland.Medic.Cauterize')
    cauterize.SkillEffectDefinitions.append(intuition_speed)
    cauterize.SkillEffectPresentations.append(intuition_presentation)
    cauterize.SkillDescription = "Shooting team members heals them.  This effect also works with grenades and rockets. Killing an enemy increases your movement speed for a few seconds."
    smirk = find_object('SkillDefinition','gd_skills2_Mordecai.Sniper.Smirk')
    smirk.SkillEffectDefinitions.append(intuition_speed)
    smirk.SkillEffectPresentations.append(intuition_presentation)
    smirk.SkillDescription = "All players on your team (including you) gain additional experience when you kill an enemy with a Critical Hit. Killing an enemy increases your movement speed for a few seconds."
    roland_skillset = find_object('PlayerSkillSetDefinition','gd_skills2_Roland.SkillSet.PlayerSkillSet_Roland')
    if cauterize not in roland_skillset.CombatSkills:
        return
    roland_skillset.CombatSkills.remove(cauterize)
    roland_skillset.InstinctSkillAugmentations.append(cauterize)
    mord_skillset = find_object('PlayerSkillSetDefinition','gd_skills2_Mordecai.SkillSet.PlayerSkillSet_Mordecai')
    mord_skillset.CombatSkills.remove(smirk)
    mord_skillset.InstinctSkillAugmentations.append(smirk)
    keep_alive(cauterize)
    keep_alive(smirk)
    keep_alive(intuition)


oidSpeedSkills = BoolOption(
    "Speed Skills",
    False,
    "On",
    "Off",
    description="Makes Smirk and Cauterize kill skills that speed you up the same amount as Intuition.\nChange this before selecting your character or it will just increase your movement speed.",
    on_change=speed_skills
)



@hook("WillowGame.WillowInteractiveObject:UsedBy", Type.POST)
def QOLSlop_TurretUsedBy(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if not oidAxtonTurret.value:
        return
    if args.User and args.User.Controller.ScorpioSpawnedActor:
        if obj.AssociatedOutpostName == args.User.Name:
            obj.Behavior_ChangeUsability(2)
            setattr(obj.CylinderComponent, "CollisionHeight", 0)
            setattr(obj.CylinderComponent, "CollisionRadius", 0)
            
            controller = args.User.Controller
            time_left = 1 - controller.ActionSkillTime
            controller.ScorpioSpawnedActor.KilledBy(None)
            controller.StartActiveSkillCooldown()
            skill_data = args.User.Controller.SkillCooldownPool.Data
            amount_back = (time_left * skill_data.MaxValue) * 0.75
            controller.SkillCooldownPool.Data.SetCurrentValue(amount_back)



@hook("WillowGame.WillowPawn:PlayLanded", Type.POST)
def QOLSlop_TurretLanded(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if not oidAxtonTurret.value or obj.MatineeGroupName == "landed_turret":
        return
    if obj.ObjectArchetype and obj.ObjectArchetype._path_name() == "gd_AutomatedTurret.PawnArchetype.Pawn_AutomatedTurret_Scorpio":
        obj.MatineeGroupName = "landed_turret"
        io = get_pc().Spawn(find_class("WillowInteractiveObject"))
        default = find_class("InteractiveObjectDefinition").ClassDefaultObject
        default.TriggerRadius = 100
        default.TriggerHeight = 50
        io.InteractiveObjectDefinition = default
        io.PostBeginPlay()
        io.AssociatedOutpostName = obj.PlayerMaster.Pawn.Name
        io.Location = obj.Location

        setattr(obj.CylinderComponent, "CollisionHeight", 50)
        setattr(obj.CylinderComponent, "CollisionRadius", 100)

        default.TriggerRadius = 0
        default.TriggerHeight = 0



@hook("WillowGame.WillowPlayerController:DisableSkillInputForSkillNumber", Type.PRE)
def QOLSlop_TurretDisableSkillInput(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if not oidAxtonTurret.value:
        return
    if obj.PlayerClass.CharacterName != 0:
        return
    if obj.PlayerSkills[args.SkillNumber].Definition == obj.PlayerClass.PlayerSkillSet.ActionSkill:
        if obj.bBehindView and "Vehicle" not in str(obj.Pawn):
            return Block, True


@hook("WillowGame.WillowPawn:Died", Type.PRE)
def QOLSlop_TurretKilledEnemy(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    if not oidAxtonTurret.value:
        return
    if not args.Killer or not hasattr(args.Killer, "MyWillowPawn"):
        return
    if hasattr(args.Killer.MyWillowPawn, "PlayerMaster") and args.Killer.MyWillowPawn.PlayerMaster:
        args.Killer.MyWillowPawn.PlayerMaster.Pawn.GoFromInjuredToHealthy()
        

oidAxtonTurret = BoolOption(
    "Axton Style Turret",
    False,
    "On",
    "Off",
    description="Makes Rolands turret like Axtons turret in Bl2. Use it to recall it and get some cooldown back and doesn't die when you go down."
)


def can_players_use(inv_def) -> bool:
    if inv_def.RequiredCharacter == 0:
        return True
    player_numbers = [(player.Owner.PlayerClass.CharacterName + 1) for player in get_pc().WorldInfo.GRI.PRIArray]
    return int(inv_def.RequiredCharacter) in player_numbers


def clean_inv_bals(class_name):
    for invbal_def in find_all("InventoryBalanceDefinition"):
        if invbal_def.InventoryDefinition and str(invbal_def.InventoryDefinition.InventoryClass.Name) == str(class_name):
            if not can_players_use(invbal_def.InventoryDefinition):
                for manufacturer in invbal_def.Manufacturers:
                    for grade in manufacturer.Grades:
                        grade.GameStageRequirement.MinGameStage = 100


@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def QOLSlop_coms_map_change(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction) -> None:

    map_name = args.NextMapName
    if map_name in ["Loader", "FakeEntry"]:
        return
    
    if not get_pc().PlayerClass:
        return
    
    if oidNoWastedComs.value:
        clean_inv_bals("WillowEquipAbleItem")

    if oidNoWastedArtifacts.value:
        clean_inv_bals("WillowUsableItem")

    

oidNoWastedComs = BoolOption(
    "No Wasted Coms",
    False,
    "On",
    "Off",
    description="Disables Class Mods for classes not in the game from spawning.\n Requires game restart if turning off, teammate joining, or changing character classes."
)
oidNoWastedArtifacts = BoolOption(
    "No Wasted Artifacts",
    False,
    "On",
    "Off",
    description="Disables Artifacts for classes not in the game from spawning.\n Requires game restart if turning off, teammate joining, or changing character classes."
)

@hook("WillowGame.WillowGlobals:IsCodeUnlocked", Type.PRE)
def QOLSlop_IsCodeUnlocked(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    return Block, oidPreOrder.value

oidPreOrder = BoolOption(
    "Pre Order Unlocks",
    False,
    "On",
    "Off",
    description="New Characters will start with the Mercenary Pack Pre Order Bonus."
)

@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def QOLSlop_MapChange(obj:UObject, args:WrappedStruct, ret:Any, func:BoundFunction) -> Any:
    if oidArmoryDoor.value and args.NextMapName == "dlc3_lancedepot_p":
        pc = get_pc()
        PlayThroughNumber = pc.GetCurrentPlaythrough()
        in_mission = find_object("MissionDefinition", 'dlc3_SideMissions.SideMissions.M_dlc3_GetLoot03')
        for mission in pc.MissionPlaythroughData[PlayThroughNumber].MissionList:
            if mission.MissionDef == in_mission and mission.Status == 4:
                death = find_object("Object", "dlc3_lancedepot_p.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_Death_0")
                door = find_object("Object", "dlc3_lancedepot_Dynamic.TheWorld:PersistentLevel.Main_Sequence.GrabLootMissions.SeqAct_Interp_6")
                door2 = find_object("Object", "dlc3_lancedepot_Dynamic.TheWorld:PersistentLevel.Main_Sequence.GrabLootMissions.SeqAct_Interp_8")
                link = make_struct("SeqOpOutputInputLink",
                                    LinkedOp=door,
                                    InputLinkIdx=0)
                link2 = make_struct("SeqOpOutputInputLink",
                                    LinkedOp=door2,
                                    InputLinkIdx=0)
                death.OutputLinks[0].Links.append(link)
                death.OutputLinks[0].Links.append(link2)
        return
    
    if oidTboneDoors.value and args.NextMapName == "dlc3_HUB_p":
        closed_doors = [
        find_object('WillowInteractiveObject','dlc3_HUB_p.TheWorld:PersistentLevel.WillowInteractiveObject_17'),
        find_object('WillowInteractiveObject','dlc3_HUB_p.TheWorld:PersistentLevel.WillowInteractiveObject_82'),
        find_object('WillowInteractiveObject','dlc3_HUB_p.TheWorld:PersistentLevel.WillowInteractiveObject_42'),
        ]
        load_package("dlc3_doors_usable")
        Door_StartOpen = find_object("InteractiveObjectDefinition","dlc3_doors_usable.Door_StartOpen")
        for door in closed_doors:
            door.InteractiveObjectDefinition = Door_StartOpen

oidArmoryDoor = BoolOption(
    "Open Armory Door",
    False,
    "On",
    "Off",
    description="With this on, the main armory door (behind where Knoxx spawns) will open after killing Knoxx after completing 'It's like Christmas!'."
)

oidTboneDoors = BoolOption(
    "Open T-Bone Doors",
    False,
    "On",
    "Off",
    description="With this on, the doors in T-Bone Junction will be open by default."
)



mod = build_mod()
