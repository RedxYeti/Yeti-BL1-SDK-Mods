import unrealsdk 
import math

from unrealsdk import find_all, make_struct, find_object, construct_object, load_package, find_class
from unrealsdk.hooks import Type, Block
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction, WeakPointer
from mods_base import hook, get_pc, build_mod, Game
from random import choice, randint

from .EnemyRandomizerOptions import oidEnemyAllegiance, oidStrictness, oidWanderingBosses, oidStaticBosses
from .EnemyRandomizerFunctions import AllEnemies, BlacklistClasses, SkagAllegiance, PawnClass, LastKnownGameSave, PopDynamicClass, AllClass, SmallBosses, MediumBosses, LargeBosses, BossNames
from .EnemyRandomizerFunctions import  MovePopulationPoints, GetPawnBalance, GenerateBossesForSave, RandomizeRapparee, keep_alive
from .EnemyRandomizerLists import MapNames, CarPacks, BlacklistNames, GruntNames, BadassNames, BossNames, FlyingGruntNames, FlyingBadassNames, FlyingBossNames, TurretNames

#DynamicPointNames: list = ["Mount1", "MiddleMount", "FrontMount"]
DynamicPointNames: list = ["TurretPoint", "INAC_Point"]
bFirstTimeStartup: bool = False
GameStageExact: UObject = None

#This has to be here instead of in functions, dont ask me why because i dont know
#when it was in functions it wouldnt keep alive some enemies and it would set some enemies allegiance to none
def FirstTimeStartup() -> None:
    global bFirstTimeStartup, AllEnemies, SkagAllegiance, SmallBosses, MediumBosses, LargeBosses, BossNames, AllClass, GameStageExact

    SkagAllegiance = find_object("PawnAllegiance","gd_allegiance.CreatureEnemy.SkagAllegiance")
    load_package("gd_Balance")
    GameStageExact = find_object('AttributeDefinition','gd_Balance.EnemyLevel.EnemyLevel_GameStage_exact')

    keep_alive(SkagAllegiance)
    #finds all the vehicles in the specified packages, sets allegiance to none or enemies cant get in to certain vehicles
    Vehicles = []
    for Packs in CarPacks:
        load_package(Packs)
        for WillowVehicle in find_all("WillowVehicle", False):
            if WillowVehicle.DisplayName and WillowVehicle not in Vehicles:
                Vehicles.append(WillowVehicle)
                WillowVehicle.Allegiance = None
                keep_alive(WillowVehicle)
                if WillowVehicle.DisplayName == "Mad Mel":
                    AllEnemies["MadMel"] = WeakPointer(WillowVehicle)
                elif WillowVehicle.DisplayName == "Krom's Turret":
                    AllEnemies["KromsTurret"] = WeakPointer(WillowVehicle)
                elif WillowVehicle.DisplayName != "Mulciber Mk2":
                    AllEnemies["Vehicles"].append(WeakPointer(WillowVehicle))

        get_pc().ConsoleCommand("obj garbage")
    Vehicles = []

    #this iterates over every level and its streaming levels, loads them, and then sorts them in SortEnemiesForLevel()
    #Map names was created by loading every map and tracking which maps actually added to the find_all("AIPawnBalanceDefinition") in SortEnemiesForLevel()
    #This can be recreated for any class
    lists = find_all("LevelDependencyList")
    for Entry in lists:
        for persistent in Entry.LevelList:
            if str(persistent.PersistentMap) in MapNames:
                mainmap = persistent.PersistentMap
                load_package(str(mainmap))
                for map in persistent.SecondaryMaps:
                    load_package(str(map))

                for AIPawnBalanceDef in find_all("AIPawnBalanceDefinition", False):
                    if (
                        AIPawnBalanceDef not in AllClass 
                        and AIPawnBalanceDef.AIPawnArchetype 
                        and "Player" not in str(AIPawnBalanceDef.AIPawnArchetype.Allegiance)
                        and "Friendly" not in str(AIPawnBalanceDef.AIPawnArchetype.Allegiance)
                        and AIPawnBalanceDef.Grades
                        and AIPawnBalanceDef.Grades[0].GradeModifiers.DisplayName
                        ):
                            AllClass.append(AIPawnBalanceDef)
                            DisplayName = AIPawnBalanceDef.Grades[0].GradeModifiers.DisplayName 
                            if DisplayName == "" or DisplayName in BlacklistNames:
                                continue

                            if AIPawnBalanceDef.Grades[0].GameStageRequirement.MinGameStage > 0:
                                AIPawnBalanceDef.Grades[0].GameStageRequirement.MinGameStage = 0

                            if DisplayName in GruntNames:
                                AllEnemies["Grunt"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in FlyingGruntNames:
                                AllEnemies["FlyingGrunt"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in BadassNames:
                                AllEnemies["Badass"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in FlyingBadassNames:
                                AllEnemies["FlyingBadass"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in BossNames:
                                AllEnemies["Boss"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in FlyingBossNames:
                                AllEnemies["FlyingBoss"].append(WeakPointer(AIPawnBalanceDef))
                            elif DisplayName in TurretNames:
                                AllEnemies["Turrets"].append(WeakPointer(AIPawnBalanceDef))
                            else:
                                print(DisplayName)

                            keep_alive(AIPawnBalanceDef)
                            keep_alive(AIPawnBalanceDef.AIPawnArchetype)

                            AIPawnBalanceDef.AIPawnArchetype.ActorSpawnCost = 0

                            for Grade in AIPawnBalanceDef.Grades:
                                Grade.GradeModifiers.ExpLevel = 0

                            if oidEnemyAllegiance.value:
                                AIPawnBalanceDef.AIPawnArchetype.Allegiance = SkagAllegiance
                            
                            if DisplayName in BossNames and AIPawnBalanceDef.AIPawnArchetype and AIPawnBalanceDef.AIPawnArchetype.CylinderComponent:
                                Height = AIPawnBalanceDef.AIPawnArchetype.CylinderComponent.CollisionHeight 
                                if Height > 115 and DisplayName not in LargeBosses:
                                    LargeBosses.append(DisplayName)
                                elif Height < 115 and Height >= 74 and DisplayName not in MediumBosses:
                                    MediumBosses.append(DisplayName)
                                elif Height < 74 and DisplayName not in SmallBosses:
                                    SmallBosses.append(DisplayName)

                get_pc().ConsoleCommand("obj garbage")

    AllClass = []

    BadTongue = find_object('AIPawnBalanceDefinition','gd_Tentacles.population.Pawn_Balance_Tentacle_Tongue')
    for PawnDef in AllEnemies["Grunt"]:
        if PawnDef() == BadTongue:
            AllEnemies["Grunt"].remove(PawnDef)
            break
 
    #fixes enemies tposing at low levels due to weapon level restrictions
    for Balance in find_all("InventoryBalanceDefinition"):
        if len(Balance.Manufacturers) and Balance.InventoryDefinition and Balance.InventoryDefinition.Class._inherits(find_class("WeaponTypeDefinition")):
            for Manufacturer in Balance.Manufacturers:
                if len(Manufacturer.Grades):
                    Manufacturer.Grades[0].GameStageRequirement.MinGameStage = 0


    bFirstTimeStartup = True
    return



@hook("WillowGame.PopulationFactoryBalancedAIPawn:CreatePopulationActor", Type.PRE)
@hook("WillowGame.PopulationFactoryBalancedAIPawn:RestorePopulatedAIPawn", Type.PRE)
def CreatePopulationActor(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction) -> None:
    if args.SpawnLocationContextObject.Class.Name in BlacklistClasses:
        return
    
    if hasattr(obj.PawnBalanceDefinition, "AIPawnArchetype") and oidEnemyAllegiance.value:
        obj.PawnBalanceDefinition.AIPawnArchetype.Allegiance = SkagAllegiance


    if not obj.PawnBalanceDefinition.Grades or not obj.PawnBalanceDefinition.Grades[0].GradeModifiers.DisplayName:
        
            return
        
    if args.SpawnLocationContextObject.Class._inherits(PopDynamicClass) and args.SpawnLocationContextObject.DynamicPointName not in DynamicPointNames:
        return

    if args.SpawnLocationContextObject.Class._inherits(PawnClass) and args.SpawnLocationContextObject.MenuName == "RandomizedEnemy":
        if "Scorpio" not in str(obj.PawnBalanceDefinition.Grades[0].GradeModifiers.DisplayName):
            return


    DisplayName: str = obj.PawnBalanceDefinition.Grades[0].GradeModifiers.DisplayName
    NewDisplay: str = ""
    
    OriginalPawnDef: UObject = obj.PawnBalanceDefinition

    obj.PawnBalanceDefinition = GetPawnBalance(DisplayName)

    print(f"{DisplayName} >>> {obj.PawnBalanceDefinition.Name}")
    
    #obj.PawnBalanceDefinition = find_object("AIPawnBalanceDefinition","dlc3_gd_balance_enemies.SkagRiders.Pawn_Balance_SkagRider3Rider")
    
    NewDisplay = obj.PawnBalanceDefinition.Grades[0].GradeModifiers.DisplayName

    if not obj.PawnBalanceDefinition.DefaultExpLevel.BaseValueAttribute:
        obj.PawnBalanceDefinition.DefaultExpLevel.BaseValueAttribute = GameStageExact


    #if "Sera" in NewDisplay:
    #    PerchDef = obj.PawnBalanceDefinition.AIPawnArchetype.BodyClass.PerchDefs[0]
    #    AboveSpawnPerch = get_pc().Pawn.Spawn(find_class("Perch"))
    #    AboveSpawnPerch.PerchDef = PerchDef
    #    AboveSpawnPerch.Location = args.SpawnLocationContextObject.Location
    #    AboveSpawnPerch.Location.Z += 1000
#
    #    AbovePlayerPerch = get_pc().Pawn.Spawn(find_class("Perch"))
    #    AbovePlayerPerch.PerchDef = PerchDef
    #    AbovePlayerPerch.Location = get_pc().Pawn.Location
    #    AbovePlayerPerch.Location.Z += 1000


        #aibal = find_object('AIPawnBalanceDefinition','gd_Balance_Enemies_Humans.Guardians.Pawn_Balance_Guardian_Sera')
        #load_package("BL1EnemyRandomizer")
        #obj.PawnBalanceDefinition.AIPawnArchetype.ControllerTemplate = find_object('WillowMind','BL1EnemyRandomizer.Character.Mind_Sera')

    with unrealsdk.hooks.prevent_hooking_direct_calls():
        RandomAI = obj.CreatePopulationActor(args.Master, args.SpawnLocationContextObject, args.SpawnLocation, args.SpawnRotation, args.GameStage, args.AwesomeLevel)

        NewLocation = args.SpawnLocation
        if not RandomAI:
            #Moves the spawn location forward in hopes of passing a collision check during the native function GearboxFramework.PopulationMaster:SpawnPopulationControlledActor
            #thanks commander
            SpawnObject = args.SpawnLocationContextObject
        
            pitch = SpawnObject.Rotation.Pitch / 65535 * math.tau
            yaw   = SpawnObject.Rotation.Yaw / 65535 * math.tau

            NewLocation.Z += math.sin(pitch) * 400
            NewLocation.X += math.cos(yaw) * math.cos(pitch) * 400
            NewLocation.Y += math.sin(yaw) * math.cos(pitch) * 400

            RandomAI = obj.CreatePopulationActor(args.Master, args.SpawnLocationContextObject, NewLocation, args.SpawnRotation, args.GameStage, args.AwesomeLevel)
        
        obj.PawnBalanceDefinition = OriginalPawnDef

        if RandomAI:
            RandomAI.MenuName = "RandomizedEnemy"
            return Block, RandomAI

        else:
            print(f"failed on {NewDisplay}")
            return
    return



@hook("WillowGame.PopulationFactoryWillowVehicle:CreatePopulationActor", Type.PRE)
def CreatePopulationActorVehicle(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction) -> None:
    if not args.SpawnLocationContextObject or not obj.VehicleArchetype:
        return

    OriginalPawnDef: UObject = obj.VehicleArchetype
    DisplayName = OriginalPawnDef.DisplayName

    BossChance = oidWanderingBosses.value > 0 and randint(1,100) <= oidWanderingBosses.value
    if DisplayName == "Mulciber Mk2":
        if BossChance:
            NewVehicle = AllEnemies["KromsTurret"]()
            obj.VehicleArchetype = NewVehicle
        else:
            return
    
    else:
        if BossChance:
            NewVehicle = AllEnemies["MadMel"]()
            obj.VehicleArchetype = AllEnemies["MadMel"]()
        else:
            NewVehicle = choice(AllEnemies["Vehicles"])()
            obj.VehicleArchetype = NewVehicle


    print(f"{DisplayName} >>> {NewVehicle.DisplayName}")

    with unrealsdk.hooks.prevent_hooking_direct_calls():
        RandomAI = obj.CreatePopulationActor(args.Master, args.SpawnLocationContextObject, args.SpawnLocation, args.SpawnRotation, args.GameStage, args.AwesomeLevel)
        obj.VehicleArchetype = OriginalPawnDef
        
        if not RandomAI:
            return 

        return Block, RandomAI


@hook("WillowGame.WillowGameInfo:PreCommitMapChange", Type.POST)
def PreCommitMapChange(obj: UObject, args: WrappedStruct, ret: any, func: BoundFunction) -> None:
    global bFirstTimeStartup
    if not bFirstTimeStartup:
        FirstTimeStartup()


    global LastKnownGameSave
    if LastKnownGameSave == -1 or get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(0).SaveGameId != LastKnownGameSave:
        if get_pc().GetWillowGlobals().GetWillowSaveGameManager().GetCachedPlayerProfile(0).SaveGameId != -1:
            GenerateBossesForSave()
            

    if args.NextMapName: 
        CurrentMap = args.NextMapName
        if oidEnemyAllegiance.value:
            #fall back, a few change depending on population defintions. mostly vehicles
            for Den in find_all("PopulationOpportunityDen"):
                if Den.PopulationDef and hasattr(Den.PopulationDef, "ActorArchetypeList"):
                    for ArchetypeList in Den.PopulationDef.ActorArchetypeList:
                        if hasattr(ArchetypeList.SpawnFactory, "SpawnAllegiance"):
                            ArchetypeList.SpawnFactory.SpawnAllegiance = SkagAllegiance

        if CurrentMap == "arid_p":
            #Mission aspects on dens add to the objective index on the specified mission
            SkagsAtTheGateDen = find_object("PopulationOpportunityDen", "Arid_Firestone.TheWorld.PersistentLevel.PopulationOpportunityDen_25")
            SkagsAtTheGateMission = find_object("MissionDefinition", "Z0_Missions.Missions.M_KillSkags_Zed")
            SkagsAtTheGateDen.Aspect.MissionObjective.MissionDefinition = SkagsAtTheGateMission
            SkagsAtTheGateDen.Aspect.MissionObjective.ObjectiveIndex = 0

            EightBanditsDen = find_object("PopulationOpportunityDen", "arid_p.TheWorld.PersistentLevel.PopulationOpportunityDen_11")
            EightBanditsMission = find_object("MissionDefinition", "Z0_Missions.Missions.M_KillBandits")
            EightBanditsDen.Aspect.MissionObjective.MissionDefinition = EightBanditsMission
            EightBanditsDen.Aspect.MissionObjective.ObjectiveIndex = 0

            DoorKnockingPopPoint = find_object("PopulationPoint", "Arid_Firestone.TheWorld.PersistentLevel.PopulationPoint_49")
            DoorKnockingPopPoint.OnSpawnCustomizations = []
        
        elif CurrentMap == "dlc3_uberboss_p":
            CrawDen = find_object("PopulationOpportunityDen", "dlc3_uberboss_Dynamic.TheWorld.PersistentLevel.PopulationOpportunityDen_1")
            CrawMission = find_object("MissionDefinition", "dlc3_SideMissions.SideMissions.M_dlc3_UberBoss")
            CrawDenAspect = construct_object("MissionPopulationAspect", CrawDen)
            CrawMissionData = make_struct("MissionObjectiveIndexData",
                                          MissionDefinition=CrawMission,
                                          ObjectiveIndex=0)
            
            CrawDenAspect.MissionObjective = CrawMissionData
            CrawDen.Aspect = CrawDenAspect

        elif CurrentMap == "interlude_1_p":
            #check move population points
            MovePopulationPoints("interlude_1_p",
                (1, 22413.248047, -2352.802002, -331.698242),
                (4, -10715.802734, -6337.351074, -1816.044067),
                (6, -9399.456055, -7161.020508, -1807.000000),
                (21, 64.796272, 17568.341797, -938.000061),
                (26, 18896.353516, -4999.597656, -531.448914),
                (39, 18896.353516, -4999.597656, -531.448914),
                (64, -64120.851563, 55000.476563, -654.350037),
                (237, -56781.304688, 45611.671875, -704.544800),
            )
        
        elif CurrentMap == "Interlude_2_P":
            MovePopulationPoints("Interlude_2_P",
                (0, -39087.046875, -16618.818359, -3137.785889),
                (3, 13819.433594, -5053.785156, -3326.185059),
                (14, -11107.236328, -32704.330078, -2321.000000),
            )

        elif CurrentMap == "dlc3_SLanceStrip_p":
            MovePopulationPoints("dlc3_SLanceStrip_p",
                (41, 50529.714844, 31163.833984, 2629.525879),
                (42, -482.958618, -15230.033203, 2622.451172),
                (87, -63484.609375, 8519.750000, 4672.900879),        
            )

        elif CurrentMap == "dlc3_southlake_p":
            MovePopulationPoints("dlc3_southlake_p",
                (33, 18559.240234,-12930.267578, 1085.715332),
                (35, 34110.972656, -11141.905273, 2452.328369),
                (59, -3045.892578, -6369.351563, 548.898682),
                (129, 43688.187500, 8131.606445, 2347.645996),
            )
        
        elif CurrentMap == "dlc3_NLanceStrip_p":
            MovePopulationPoints("dlc3_NLanceStrip_p",
                (87, -99919.148438, 1535.209229, -1.721651),
                (88, -48509.617188, -3988.847168, 24.105003),
                (108, 6782.114746, -29630.259766, -2005.109863),
            )

    return

build_mod(options=[oidStrictness, oidWanderingBosses, oidEnemyAllegiance, oidStaticBosses])

"""
TODO

"""