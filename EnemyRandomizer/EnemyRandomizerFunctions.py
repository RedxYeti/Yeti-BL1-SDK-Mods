from json import dump, load
from os import makedirs
from os.path import exists

from unrealsdk import find_all, load_package, make_struct, find_object, construct_object, find_class
from unrealsdk.unreal import UObject, WeakPointer, UClass, BoundFunction
from mods_base import get_pc, SETTINGS_DIR
from random import choice, randint

from .EnemyRandomizerLists import MapNames, CarPacks, BlacklistNames, GruntNames, BadassNames, BossNames, FlyingGruntNames, FlyingBadassNames, FlyingBossNames, TurretNames
from .EnemyRandomizerOptions import oidStaticBosses, oidEnemyAllegiance, oidStrictness, oidWanderingBosses


WackyBosses: bool = False #doesnt work yet

SkagAllegiance: UObject = None

LastKnownGameSave: int = -1

CharacterBosses: dict = {}

bFirstTimeStartup: bool = False

PawnClass: UClass = find_class("Pawn")
PopDynamicClass: UClass = find_class("PopulationPoint_Dynamic")

BlacklistClasses: list = ["WillowPlayerController", "WillowPlayerPawn", "PopulationFactoryWillowVehicle"]
RecentlyUsedEnemies: list = []
RecentlyUsedBosses: list = []
SmallBosses: list = []
MediumBosses: list = []
LargeBosses: list = []
AllClass: list = []

AllEnemies: dict = {
    "Grunt": [],
    "FlyingGrunt": [],
    "Badass": [],
    "FlyingBadass": [],
    "Boss": [],
    "FlyingBoss": [],
    "Turrets": [],
    "Vehicles": [],
    "MadMel": [],
    "KromsTurret": [],
}

def keep_alive(Object:UObject) -> None:
    Object.ObjectFlags |= 0x4000
    return


def MovePopulationPoints(MapName:str, *PopulationInfo:tuple) -> None:
    #this moves population points passed to it, i used this for vehicles because they usually got stuck in thier spawn huts
    for Info in PopulationInfo:
        NewLocation = make_struct("Vector", X=Info[1],Y=Info[2],Z=Info[3])
        find_object("PopulationPoint", f"{MapName}.TheWorld:PersistentLevel.PopulationPoint_{Info[0]}").Location = NewLocation
    return



def GetAnyBoss() -> UObject:
    NewBoss = choice(AllEnemies["Boss"])
    while NewBoss in RecentlyUsedBosses:
        NewBoss = choice(AllEnemies["Boss"])
    
    RecentlyUsedBosses.append(NewBoss)
    if len(RecentlyUsedBosses) > 10:
        RecentlyUsedBosses.remove(RecentlyUsedBosses[0])
    
    return NewBoss()


def FindStaticBoss(BossDisplayName:str) -> UObject:
    for Definition in AllEnemies["Boss"]:
        if Definition().Grades[0].GradeModifiers.DisplayName == CharacterBosses[BossDisplayName]:
            return Definition()


def FindBoss(BossDisplayName:str, bBossLocation) -> UObject:
    if bBossLocation:
        if oidStaticBosses.value:
            return FindStaticBoss(BossDisplayName)
        else:
            if BossDisplayName in LargeBosses:
                return GetAnyBoss()
            
            if BossDisplayName in MediumBosses:
                return FindStaticBoss(choice(choice([MediumBosses, SmallBosses])))
            
            if BossDisplayName in SmallBosses:
                return FindStaticBoss(choice(SmallBosses))
    else:
        return GetAnyBoss()

    

def FindEnemy(EnemyList:list) -> UObject:
    global RecentlyUsedEnemies
    NewEnemy = choice(EnemyList)
    while NewEnemy in RecentlyUsedEnemies:
        NewEnemy = choice(EnemyList)
    
    RecentlyUsedEnemies.append(NewEnemy)
    if len(RecentlyUsedEnemies) > 50:
        RecentlyUsedEnemies.remove(RecentlyUsedEnemies[0])

    return NewEnemy()


def FindUnusedBoss(ListToUse, BackupList) -> str:
    if len(ListToUse) > 0:
        ReturnName = choice(ListToUse)
        ListToUse.remove(ReturnName)
        return ReturnName
    else:
        return choice(BackupList)


def GetPawnBalance(DisplayName:str) -> UObject:
    RandomBalance: UObject = None
    if oidStrictness.value == "Strict":
        if DisplayName in GruntNames:
            RandomBalance = FindEnemy(AllEnemies["Grunt"])
        elif DisplayName in FlyingGruntNames:
            #aibal = find_object('AIPawnBalanceDefinition','gd_Balance_Enemies_Humans.Guardians.Pawn_Balance_Guardian_Sera')
            #load_package("BL1EnemyRandomizer")
            #aibal.AIPawnArchetype.ControllerTemplate = find_object('WillowMind','BL1EnemyRandomizer.Character.Mind_Sera')
            RandomBalance = choice(AllEnemies["FlyingGrunt"])()
            #RandomBalance = choice(AllEnemies["FlyingGrunt"])()
        elif DisplayName in BadassNames:
            RandomBalance = FindEnemy(AllEnemies["Badass"])
        elif DisplayName in FlyingBadassNames:
            RandomBalance = choice(AllEnemies["FlyingBadass"])()
        elif DisplayName in BossNames:
            RandomBalance = FindBoss(DisplayName, True)
        elif DisplayName in FlyingBossNames:
            RandomBalance = choice(AllEnemies["FlyingBoss"])()


    elif oidStrictness.value == "Chaos Light":
        if DisplayName in GruntNames or DisplayName in BadassNames:
            RandomBalance = FindEnemy(choice([AllEnemies["Grunt"],AllEnemies["Badass"]]))
        elif DisplayName in FlyingGruntNames or DisplayName in FlyingBadassNames:
            RandomBalance = choice(choice([AllEnemies["FlyingGrunt"],AllEnemies["FlyingBadass"]]))()
        elif DisplayName in BossNames:
            RandomBalance = FindBoss(DisplayName, True)
        elif DisplayName in FlyingBossNames:
            RandomBalance = choice(AllEnemies["FlyingBoss"])()
        
    
    else:
        if DisplayName in GruntNames or DisplayName in BadassNames or DisplayName in BossNames:
            RandomBalance = choice(choice([AllEnemies["Grunt"],AllEnemies["Badass"], AllEnemies["Boss"]]))()
        elif DisplayName in FlyingGruntNames or DisplayName in FlyingBadassNames or DisplayName in FlyingBossNames:
            RandomBalance = choice(choice([AllEnemies["FlyingGrunt"],AllEnemies["FlyingBadass"],AllEnemies["FlyingBoss"]]))()
        
    
    if DisplayName in TurretNames:
        RandomBalance = choice(AllEnemies["Turrets"])()


    if DisplayName not in BossNames and DisplayName not in FlyingBossNames and oidWanderingBosses.value > 0 and randint(1,100) <= oidWanderingBosses.value:
        if DisplayName in GruntNames or DisplayName in BadassNames:
            RandomBalance = FindBoss(DisplayName, False)
        else:
            RandomBalance = choice(AllEnemies["FlyingBoss"])()

    return RandomBalance


def GenerateBossesForSave() -> None:
    global SmallBosses, MediumBosses, LargeBosses, BossNames, CharacterBosses, LastKnownGameSave

    ID = get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(0).SaveGameId
    LastKnownGameSave = ID

    makedirs(f"{SETTINGS_DIR}\\EnemyRandomizer\\Bosses\\",exist_ok=True)
    file_path = f"{SETTINGS_DIR}\\EnemyRandomizer\\Bosses\\{ID}.json"
    
    CharacterBosses = {}
    if not exists(file_path):
        BossesDict = {}
        if not WackyBosses:
            BackupSmall = SmallBosses.copy()
            BackupMedium =  MediumBosses.copy()
            BackupLarge = LargeBosses.copy()
            for name in BossNames:
                if name in SmallBosses:
                    BossesDict[name] = FindUnusedBoss(BackupSmall, SmallBosses)
                elif name in MediumBosses:
                    BossesDict[name] = FindUnusedBoss(BackupMedium, MediumBosses)
                elif name in LargeBosses:
                    BossesDict[name] = FindUnusedBoss(BackupLarge, LargeBosses)
        else:
            BossNamesCopy = [Name for Name in BossNames]
            for name in BossNames:
                if len(BossNamesCopy) > 0:
                    NextBoss = choice(BossNamesCopy)
                    BossesDict[name] = NextBoss
                    BossNamesCopy.remove(NextBoss)
                else:
                    BossesDict[name] = choice(BossNames)
                    
        with open(file_path, 'w') as file:
            dump(BossesDict, file, indent=4)
        CharacterBosses = BossesDict
    else:
        with open(file_path, 'r') as file:
            CharacterBosses = load(file)
    return


def RandomizeRapparee(Children:list) -> None:
    for Child in Children:
        if hasattr(Child, "PopulationDef"):
            RandomAIPawn = choice(AllEnemies["Grunt"])().AIPawnArchetype

            NewCrane = construct_object("WillowAICranePawn", get_pc())

            OldCrane = Child.PopulationDef.ActorArchetypeList[0].SpawnFactory.PawnBalanceDefinition.AIPawnArchetype

            crane_default = NewCrane.Class.ClassDefaultObject

            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            for attr in dir(RandomAIPawn):
                if "bound function" not in str(getattr(RandomAIPawn, attr)):
                    try:
                        print(f"{attr}: {getattr(RandomAIPawn, attr)}")
                    except:
                        continue


            NewCrane.bUseCrane = OldCrane.bUseCrane
            NewCrane.CraneSplineName = OldCrane.CraneSplineName
            NewCrane.CraneSingleBoneName = OldCrane.CraneSingleBoneName
            NewCrane.CraneSpline = OldCrane.CraneSpline
            NewCrane.CraneSingleBone = OldCrane.CraneSingleBone
            NewCrane.CraneMidPointPercent = OldCrane.CraneMidPointPercent
            NewCrane.CraneMidPointOffset = OldCrane.CraneMidPointOffset
            NewCrane.CraneEndPointOffset = OldCrane.CraneEndPointOffset
            NewCrane.CraneMinDot = OldCrane.CraneMinDot
            NewCrane.CraneMinDistance = OldCrane.CraneMinDistance
            NewCrane.CraneMaxDistance = OldCrane.CraneMaxDistance
            NewCrane.CraneHeightScale = OldCrane.CraneHeightScale
            NewCrane.MyDummy = OldCrane.MyDummy
            NewCrane.GoalLocation = OldCrane.GoalLocation
            Child.PopulationDef.ActorArchetypeList[0].SpawnFactory.PawnBalanceDefinition.AIPawnArchetype = NewCrane
    return




"""
TODO
"Spike", enemy

no weapons, fix min gamestage

"""