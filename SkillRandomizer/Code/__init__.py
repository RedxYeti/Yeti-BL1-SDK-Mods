from unrealsdk import find_object, load_package
from unrealsdk.hooks import Type
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction
from mods_base import hook, build_mod, SETTINGS_DIR
from random import Random
from . import seed_system
import os
import json

from typing import Any


version0 = seed_system.SeedFormat(
    version=0, format_string="xxxxx-xxxxx", seed_options=()
)



class SkillSeed(seed_system.Seed):
    seeds_file = SETTINGS_DIR / "Skill Randomizer Seeds.txt"
    seed_formats = (version0,)

    random: Random

    def enable(self) -> None:
        global RandomizedSkills
        RandomizedSkills = False

        self.random = Random(self.data)


from .SkillDefinitions import (
    BrickSkills,
    LilithSkills,
    MordecaiSkills,
    RolandSkills,
    CombatSkills,
    KillSkills,
    GeneralSkills,
)

from .ClassMods import (
    BrickComs,
    LilithComs,
    MordecaiComs,
    RolandComs,
    AllBuffedSkills,
)

BrickSkillsSet = find_object(
    "PlayerSkillSetDefinition",
    "gd_Skills2_Brick.SkillSet.PlayerSkillSet_Brick",
)
BrickSkillsSet.ObjectFlags |= 0x4000

LilithSkillsSet = find_object(
    "PlayerSkillSetDefinition",
    "gd_Skills2_Lilith.SkillSet.PlayerSkillSet_Lilith",
)
LilithSkillsSet.ObjectFlags |= 0x4000

MordecaiSkillsSet = find_object(
    "PlayerSkillSetDefinition",
    "gd_skills2_Mordecai.SkillSet.PlayerSkillSet_Mordecai",
)
MordecaiSkillsSet.ObjectFlags |= 0x4000

RolandSkillsSet = find_object(
    "PlayerSkillSetDefinition",
    "gd_skills2_Roland.SkillSet.PlayerSkillSet_Roland",
)
RolandSkillsSet.ObjectFlags |= 0x4000

AllSkillSets = [
    BrickSkillsSet,
    LilithSkillsSet,
    MordecaiSkillsSet,
    RolandSkillsSet,
]
CharacterSpecificSkills = [
    BrickSkills,
    LilithSkills,
    MordecaiSkills,
    RolandSkills,
]
AllComs = [
    BrickComs,
    LilithComs,
    MordecaiComs,
    RolandComs,
]

NewSkills = []
NewCombatSkills = []
NewKillSkills = []
SkillsForComs = []
AttributesForComs = []

RandomizedSkills = False

def SetUpComs(CharacterIndex:int) -> None:
    if len(SkillsForComs) < 1:
        return

    load_package("gd_CommandDecks")
    load_package("dlc3_gd_CommandDecks")
    for Com in AllComs[CharacterIndex]:
        Com = find_object('ItemPartDefinition', Com)
        Com.ObjectFlags |= 0x4000
        AddedSkills = []
        
        for SlotEffect in Com.AttributeSlotEffects:
            if SlotEffect.SlotName in ["Aug1", "Aug2", "Aug3"]:
                for key, value in AllBuffedSkills.items():
                    if SlotEffect.AttributeToModify == find_object('AttributeDefinition', value):
                        if key not in SkillsForComs:
                            RandomAttribute = find_object('AttributeDefinition', SkillSeed.current_seed.random.choice(AttributesForComs))
                            while RandomAttribute in AddedSkills:
                                RandomAttribute = find_object('AttributeDefinition', SkillSeed.current_seed.random.choice(AttributesForComs))

                            if len(SkillsForComs) >= 3:
                                AddedSkills.append(RandomAttribute)
                            
                            SlotEffect.AttributeToModify = RandomAttribute
                        break
                        
    AddedSkills = []  
    return


def GetNewSkill() -> UObject:
    if not SkillSeed.current_seed:
        raise Exception("No seed selected")

    NewSkill = NewSkills.pop(
        NewSkills.index(SkillSeed.current_seed.random.choice(NewSkills))
    )

    if NewSkill in AllBuffedSkills.keys():
        SkillsForComs.append(NewSkill)
        AttributesForComs.append(AllBuffedSkills[NewSkill])

    NewSkillObject = find_object("SkillDefinition", NewSkill)
    if NewSkill in CombatSkills:
        NewCombatSkills.append(NewSkillObject)
    if NewSkill in KillSkills:
        NewKillSkills.append(NewSkillObject)
    return NewSkillObject


@hook("WillowGame.WillowGFxLobbySinglePlayer:LaunchSaveGame", Type.PRE)
def LaunchedGame(
    obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction
):
    global RandomizedSkills, NewCombatSkills, NewKillSkills, NewSkills, SkillsForComs, AttributesForComs

    if not SkillSeed.current_seed:
        return

    if not RandomizedSkills:
        for CharacterSet in AllSkillSets:
            NewCombatSkills = []
            NewKillSkills = []
            SkillsForComs = []
            AttributesForComs = []

            NewSkills = (
                CharacterSpecificSkills[AllSkillSets.index(CharacterSet)]
                + GeneralSkills
            )

            for i in range(3):
                Tier = CharacterSet.LeftBranch.Tiers[i]
                Tier.Skills[0] = GetNewSkill()
                Tier.Skills[1] = GetNewSkill()
            CharacterSet.LeftBranch.Tiers[3].Skills[0] = GetNewSkill()

            for i in range(3):
                Tier = CharacterSet.MiddleBranch.Tiers[i]
                Tier.Skills[0] = GetNewSkill()
                Tier.Skills[1] = GetNewSkill()
            CharacterSet.MiddleBranch.Tiers[3].Skills[0] = GetNewSkill()

            for i in range(3):
                Tier = CharacterSet.RightBranch.Tiers[i]
                Tier.Skills[0] = GetNewSkill()
                Tier.Skills[1] = GetNewSkill()
            CharacterSet.RightBranch.Tiers[3].Skills[0] = GetNewSkill()

            CharacterSet.CombatSkills = NewCombatSkills
            CharacterSet.InstinctSkillAugmentations = NewKillSkills

            SetUpComs(AllSkillSets.index(CharacterSet))

        RandomizedSkills = True

    return


build_mod(
    options=(
        SkillSeed.new_seed_menu(),
        SkillSeed.edit_seeds_button(),
        SkillSeed.select_seed_menu(),
    ),
    on_enable=SkillSeed.enable_seed,
    on_disable=SkillSeed.disable_seed,
)
