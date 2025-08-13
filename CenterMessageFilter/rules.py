from mods_base import BoolOption, ObjectFlags
from unrealsdk import load_package, find_object
from unrealsdk.unreal import notify_changes

loaded_rules = False
rules_io = None

def rule_changed(option, new_value):
    global loaded_rules, rules_io
    if not loaded_rules:
        load_package("dlc2_gd_Colosseum_gameRules")
        rules_io = find_object("InteractiveObjectDefinition","dlc2_gd_Colosseum_gameRules.InteractiveObjects.io_GameRules")
        rules_io.ObjectFlags = ObjectFlags.KEEP_ALIVE
        loaded_rules = True
    rules_io = find_object("InteractiveObjectDefinition","dlc2_gd_Colosseum_gameRules.InteractiveObjects.io_GameRules")
    value = 1 if new_value else 0
    for possibility in rules_io.DefaultBehaviorSet.CustomEvents[10].Behaviors[0].Possibilities:
        possibility_name = str(possibility.Behaviors[0].SkillToActivate.Name).split("_")[-1]
        if possibility_name == option.identifier:
            with notify_changes():
                setattr(possibility.Weight, "BaseValueScaleConstant", value)
            break


oidRuleBeefCake = BoolOption("BeefCake", True, "On", "Off", on_change=rule_changed)
oidRuleCloseCombat = BoolOption("CloseCombat", True, "On", "Off", on_change=rule_changed)
oidRuleDeadAim = BoolOption("DeadAim", True, "On", "Off", on_change=rule_changed)
oidRuleDodgeBall = BoolOption("DodgeBall", True, "On", "Off", on_change=rule_changed)
oidRuleIronhide = BoolOption("Ironhide", True, "On", "Off", on_change=rule_changed)
oidRuleKickAss = BoolOption("KickAss", True, "On", "Off", on_change=rule_changed)
oidRuleLoaded = BoolOption("Loaded", True, "On", "Off", on_change=rule_changed)
oidRuleNaked = BoolOption("Naked", True, "On", "Off", on_change=rule_changed)
oidRuleOverclocked = BoolOption("Overclocked", True, "On", "Off", on_change=rule_changed)
oidRuleRegeneration = BoolOption("Regeneration", True, "On", "Off", on_change=rule_changed)
oidRuleSpastic = BoolOption("Spastic", True, "On", "Off", on_change=rule_changed)
oidRuleWeaponMasters = BoolOption("WeaponMasters", True, "On", "Off", on_change=rule_changed)
oidRuleBodyShot = BoolOption("BodyShot", True, "On", "Off", on_change=rule_changed)
oidRuleHeadShot = BoolOption("HeadShot", True, "On", "Off", on_change=rule_changed)
oidRuleVampire = BoolOption("Vampire", True, "On", "Off", on_change=rule_changed)
oidRuleGetSomeAir = BoolOption("GetSomeAir", True, "On", "Off", on_change=rule_changed)
oidRuleHighSpeed = BoolOption("HighSpeed", True, "On", "Off", on_change=rule_changed)
oidRuleCombatRifle = BoolOption("CombatRifle", True, "On", "Off", on_change=rule_changed)
oidRulePistol = BoolOption("Pistol", True, "On", "Off", on_change=rule_changed)
oidRuleRocketLauncher = BoolOption("RocketLauncher", True, "On", "Off", on_change=rule_changed)
oidRuleShotgun = BoolOption("Shotgun", True, "On", "Off", on_change=rule_changed)
oidRuleSMG = BoolOption("SMG", True, "On", "Off", on_change=rule_changed)
oidRuleSniper = BoolOption("Sniper", True, "On", "Off", on_change=rule_changed)
oidRuleElemental = BoolOption("Elemental", True, "On", "Off", on_change=rule_changed)


all_rules = [
    oidRuleBeefCake,
    oidRuleCloseCombat,
    oidRuleDeadAim,
    oidRuleDodgeBall,
    oidRuleIronhide,
    oidRuleKickAss,
    oidRuleLoaded,
    oidRuleNaked,
    oidRuleOverclocked,
    oidRuleRegeneration,
    oidRuleSpastic,
    oidRuleWeaponMasters,
    oidRuleBodyShot,
    oidRuleHeadShot,
    oidRuleVampire,
    oidRuleGetSomeAir,
    oidRuleHighSpeed,
    oidRuleCombatRifle,
    oidRulePistol,
    oidRuleRocketLauncher,
    oidRuleShotgun,
    oidRuleSMG,
    oidRuleSniper,
    oidRuleElemental
]