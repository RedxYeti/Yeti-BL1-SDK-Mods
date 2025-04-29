from unrealsdk import find_object
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

NewSkills = []
NewCombatSkills = []
NewKillSkills = []

RandomizedSkills = False

def GetNewSkill() -> UObject:
    if not SkillSeed.current_seed:
        raise Exception("No seed selected")

    NewSkill = NewSkills.pop(
        NewSkills.index(SkillSeed.current_seed.random.choice(NewSkills))
    )
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
    global RandomizedSkills, NewCombatSkills, NewKillSkills, NewSkills

    if not SkillSeed.current_seed:
        return

    if not RandomizedSkills:
        for CharacterSet in AllSkillSets:
            NewCombatSkills = []
            NewKillSkills = []

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
