from mods_base import get_pc
from unrealsdk import find_object, make_struct
from unrealsdk.unreal import UObject, WrappedStruct

def get_mission_status(mission_name:str) -> int:
    pc = get_pc()
    PlayThroughNumber = pc.GetCurrentPlaythrough()
    in_mission = find_object("MissionDefinition", mission_name)
    for mission in pc.MissionPlaythroughData[PlayThroughNumber].MissionList:
        if mission.MissionDef == in_mission:
            return mission.Status
    return 0

def make_new_link(link_op:UObject, index:int = 0) -> WrappedStruct:
    return make_struct("SeqOpOutputInputLink",
                        LinkedOp=link_op,
                        InputLinkIdx=index)

class Map:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Map.registry[cls.name] = cls#type:ignore

    def on_map_loaded(self):
        pass


class SkagGully(Map):
    name = "Arid_SkagGully_P"

    def on_map_loaded(self):
        nine_toes_replay = find_object("Object", "Arid_SkagGully_NineToes.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionStatusChanged_1")
        nine_toes_toggle = find_object("Object", "Arid_SkagGully_NineToes.TheWorld:PersistentLevel.Main_Sequence.SeqAct_Toggle_0")
        nine_toes_replay.OutputLinks[3].Links = [make_new_link(nine_toes_toggle)]


class DahlHeadlands(Map):
    name = "interlude_1_p"

    def on_map_loaded(self):
        mel_mission_disabler = find_object("Object", "interlude_1_p.TheWorld:PersistentLevel.Main_Sequence.MadMel.GateLogic.WillowSeqEvent_MissionObjectiveComplete_0")
        starting_mel_runners = find_object("Object", "interlude_1_p.TheWorld:PersistentLevel.Main_Sequence.MadMel.GateLogic.SeqAct_ActivateRemoteEvent_0")
        mel_mission_disabler.OutputLinks[0].Links = [make_new_link(starting_mel_runners)]
        

class RustCommonsEast(Map):
    name = "Trash_p"

    def on_map_loaded(self):
        jaynis_den = find_object('PopulationOpportunityDen','Trash_Aquaduct.TheWorld:PersistentLevel.PopulationOpportunityDen_8')
        jaynis_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)        


class SaltFlats(Map):
    name = "Interlude_2_P"

    def on_map_loaded(self):
        final_artifact_mission_kismet = find_object('Object','Interlude_2_Digger.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionStatusChanged_0')
        ramp_to_flynt = find_object('Object','Interlude_2_Digger.TheWorld:PersistentLevel.Main_Sequence.SeqAct_Delay_1')
        final_artifact_mission_kismet.OutputLinks[3].Links.append(make_new_link(ramp_to_flynt))

        elevator_trigger_0 = find_object('Object','Interlude_2_P.TheWorld:PersistentLevel.Main_Sequence.Digger.Elevators.SeqEvent_Used_0')
        elevator_trigger_1 = find_object('Object','Interlude_2_P.TheWorld:PersistentLevel.Main_Sequence.Digger.Elevators.SeqEvent_Used_1')
        elevator_trigger_0.ReTriggerDelay = 1
        elevator_trigger_1.ReTriggerDelay = 1

        elevator_up_matinee = find_object('Object','Interlude_2_P.TheWorld:PersistentLevel.Main_Sequence.Digger.Elevators.SeqAct_Interp_5')
        elevator_down_matinee = find_object('Object','Interlude_2_P.TheWorld:PersistentLevel.Main_Sequence.Digger.Elevators.SeqAct_Interp_2')
        
        play_speed = 1 if get_mission_status('Z1_Missions.Missions.M_FinalArtifact') != 4 else 2.5
        
        elevator_up_matinee.PlayRate = play_speed
        elevator_down_matinee.PlayRate = play_speed


class TheBackdoor(Map):
    name = "Interlude_2_Cave_P"

    def on_map_loaded(self):
        level_loaded = find_object("Object", "Interlude_2_Cave_P.TheWorld:PersistentLevel.Main_Sequence.BossFight.SeqEvent_LevelLoaded_0")
        if get_mission_status("Z2_Missions.Missions.M_unknown") == 4:
            steele_matinee = find_object("Object", "Interlude_2_Cave_P.TheWorld:PersistentLevel.Main_Sequence.BossFight.SeqAct_Interp_0")
            level_loaded.OutputLinks[0].Links = steele_matinee.OutputLinks[0].Links
        else:
            bool_check = find_object("Object", "Interlude_2_Cave_P.TheWorld:PersistentLevel.Main_Sequence.BossFight.SeqCond_CompareBool_0")
            level_loaded.OutputLinks[0].Links = [make_new_link(bool_check)]
        

class TheVault(Map):
    name = "Waste_Vault_P"

    def on_map_loaded(self):
        destroyer_mission_kismet = find_object("Object", "Waste_Vault_Script.TheWorld:PersistentLevel.Main_Sequence.Stage1.WillowSeqEvent_MissionStatusChanged_3")
        destroyer_mission_kismet.OutputLinks[3].Links = [destroyer_mission_kismet.OutputLinks[1].Links[0]]
        
        teleporter_destination = find_object("Object", "Waste_Vault_P.TheWorld:PersistentLevel.Main_Sequence.Transitions.WillowSeqEvent_MissionStatusChanged_0")
        teleporter_destination.bEnabled = True if get_mission_status("Z2_Missions.Missions.M_FindTheVault") != 4 else False


class TetanusWarrens(Map):
    name = "Scrap_TrashCave_P"

    def on_map_loaded(self):
        weewee_mission_kismet =  find_object("Object", "Scrap_TrashCave_P.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionStatusChanged_0")
        weewee_mission_kismet.OutputLinks[3].Links = weewee_mission_kismet.OutputLinks[1].Links
        

class TheMill(Map):
    name = "dlc1_mill_boss_p"

    def on_map_loaded(self):
        ned_den = find_object('PopulationOpportunityDen','dlc1_mill_boss_p.TheWorld:PersistentLevel.PopulationOpportunityDen_5')
        ned_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)
        ned_death = find_object("Object", "dlc1_mill_boss_p.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_Death_1")
        undead_ned_death = find_object("Object", "dlc1_mill_boss_p.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_Death_0")
        if get_mission_status('dlc1_Missions.MainMissions.M_dlc1_KillNed') == 4:
            undead_ned_death.bEnabled = False
            ned_movie = find_object("Object", "dlc1_mill_boss_p.TheWorld:PersistentLevel.Main_Sequence.SeqAct_PlayBinkMovie_2")
            ned_bool = find_object("Object", "dlc1_mill_boss_p.TheWorld:PersistentLevel.Main_Sequence.SeqCond_CompareBool_0")
            
            ned_death.OutputLinks[0].Links = [
                                             ned_movie.OutputLinks[0].Links[0],
                                             ned_bool.OutputLinks[1].Links[0]
                                             ]
        else:
            undead_ned_death.bEnabled = True
            complete_ned_mission = find_object("Object", "dlc1_mill_boss_p.TheWorld:PersistentLevel.Main_Sequence.WillowSeqAct_CompleteMission_1")
            ned_death.OutputLinks[0].Links = [make_new_link(complete_ned_mission)]


class TBoneJunction(Map):
    name = "dlc3_HUB_p"

    def on_map_loaded(self):
        assassin_mission_kismet =  find_object("Object", "dlc3_HUB_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.WillowSeqEvent_MissionStatusChanged_0")
        assassin_matinee =  find_object("Object", "dlc3_HUB_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.SeqAct_Interp_0")
        assassin_mission_kismet.OutputLinks[3].Links = [make_new_link(assassin_matinee)]


class TheRidgeway(Map):
    name = "dlc3_NLanceStrip_p"

    def on_map_loaded(self):
        road_block_kismet = find_object("Object", "dlc3_NLanceStrip_Drive.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionStatusChanged_0")
        bool_check = find_object("Object", "dlc3_NLanceStrip_Drive.TheWorld:PersistentLevel.Main_Sequence.SeqCond_CompareBool_0")
        road_block_kismet.OutputLinks[3].Links = [make_new_link(bool_check)]

        kyros_den = find_object('PopulationOpportunityDen','dlc3_NLanceStrip_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_12')
        kyros_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)

        typhon_den = find_object('PopulationOpportunityDen','dlc3_NLanceStrip_Dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_13')
        typhon_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)

        generic_assassins_den = find_object('PopulationOpportunityDen','dlc3_NLanceStrip_p.TheWorld:PersistentLevel.PopulationOpportunityDen_12')
        generic_assassins_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)


class DeepFathoms(Map):
    name = "dlc3_southlake_p"

    def on_map_loaded(self):
        assassin_mission_mission =  find_object("Object", "dlc3_SOUTHLAKE_dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.WillowSeqEvent_MissionStatusChanged_0")
        assassin_mission_kismet = find_object("Object", "dlc3_SOUTHLAKE_dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.SeqAct_Interp_0")
        assassin_mission_mission.OutputLinks[3].Links = [make_new_link(assassin_mission_kismet)]


class RoadsEnd(Map):
    name = "dlc3_gondola_p"

    def on_map_loaded(self):
        assassin_mission_kismet =  find_object("Object", "dlc3_gondola_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.WillowSeqEvent_MissionObjectiveComplete_0")
        assassin_mission_kismet.bEnabled = get_mission_status('dlc3_SideMissions.SideMissions.M_dlc3_Hitman') != 4
        assassin_trigger_vol =  find_object("Object", "dlc3_gondola_Dynamic.TheWorld:PersistentLevel.Main_Sequence.Assassins.SeqEvent_Touch_0")
        assassin_trigger_vol.bEnabled = get_mission_status('dlc3_SideMissions.SideMissions.M_dlc3_Hitman') == 4
        
        generic_assassins_den = find_object('PopulationOpportunityDen','dlc3_gondola_dynamic.TheWorld:PersistentLevel.PopulationOpportunityDen_0')
        generic_assassins_den.Aspect.MissionReactions.MissionStatusOpportunityReaction = (1,0,1,0)

        
class HyperionDump(Map):
    name = "DLC4_Hyperion_Dump_p"

    def on_map_loaded(self):
        super_badass_mission_kismet = find_object("Object", "DLC4_Hyperion_Dump_p.TheWorld:PersistentLevel.Main_Sequence.WillowSeqEvent_MissionStatusChanged_5")
        super_badass_mission_kismet.OutputLinks[3].Links = super_badass_mission_kismet.OutputLinks[1].Links
        

class SandersGorge(Map):
    name = "DLC4_Sanders_Gorge_p"

    def on_map_loaded(self):
        cluck_trap_mission_kismet = find_object("Object", "DLC4_Sanders_Gorge_p.TheWorld:PersistentLevel.Main_Sequence.Missions.WillowSeqEvent_MissionStatusChanged_5")
        cluck_trap_mission_kismet.OutputLinks[3].Links[0].LinkedOp = find_object("Object", "DLC4_Sanders_Gorge_p.TheWorld:PersistentLevel.Main_Sequence.Missions.SeqAct_Toggle_3")
        cluck_trap_mission_kismet.OutputLinks[3].Links[0].InputLinkIdx = 0

        cutscene_trigger_vol = find_object("Object", "DLC4_Sanders_Gorge_p.TheWorld:PersistentLevel.Main_Sequence.Missions.SeqEvent_Touch_2")
        cutscene_trigger_vol.bEnabled = get_mission_status('DLC4_Sanders_Gorge_Missions.MainMissions.M_dlc4_Finger_Lickin_Bad') != 4


class DividingFaults(Map):
    name = "DLC4_Dividing_Faults_p"

    def on_map_loaded(self):
        level_loaded = find_object("Object", "DLC4_Dividing_Faults_p.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_LevelLoaded_4")
        level_loaded.OutputLinks[0].Links = []
        

class ScorchedSnakeCanyon(Map):
    name = "DLC4_SS_Canyon_p"

    def on_map_loaded(self):
        hive_mission_complete_kismet = find_object("Object", "DLC4_SS_Canyon_p.TheWorld:PersistentLevel.Main_Sequence.RakkHive_Logic.WillowSeqEvent_MissionObjectiveComplete_0")
        hive_mission_complete_kismet.bEnabled = False

        hive_mission_status_kismet = find_object("Object", "DLC4_SS_Canyon_p.TheWorld:PersistentLevel.Main_Sequence.RakkHive_Logic.WillowSeqEvent_MissionStatusChanged_1")
        hive_mission_status_kismet.OutputLinks[3].Links = hive_mission_status_kismet.OutputLinks[1].Links
        

class WaywardPass(Map):
    name = "DLC4_Wayward_Pass_p"

    def on_map_loaded(self):
        if get_mission_status("DLC4_Wayward_Pass_Missions.MainMissions.M_dlc4_OTCT_Reboot") == 4:
            knoxx_door_trigger = find_object("Object", "DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_Touch_0")
            knoxx_exit_matinee = find_object("Object", "DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.Main_Sequence.SeqAct_Interp_4")
            zed_exit_matinee = find_object("Object", "DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.Main_Sequence.SeqAct_Interp_7")
            steele_exit_matinee = find_object("Object", "DLC4_Wayward_Pass_p.TheWorld:PersistentLevel.Main_Sequence.SeqAct_Interp_0")
            knoxx_door_trigger.OutputLinks[0].Links.append(make_new_link(knoxx_exit_matinee))
            knoxx_door_trigger.OutputLinks[0].Links.append(make_new_link(zed_exit_matinee))
            knoxx_door_trigger.OutputLinks[0].Links.append(make_new_link(steele_exit_matinee))
        

class DLC4AridBadlands(Map):
    name = "DLC4_Arid_Badlands_p"

    def on_map_loaded(self):
        if get_mission_status("DLC4_Wayward_Pass_Missions.MainMissions.M_dlc4_OTCT_Reboot") == 4:
            minac_trigger = find_object('WillowTrigger','DLC4_Arid_Badlands_p.TheWorld:PersistentLevel.WillowTrigger_0')
            minac_trigger.CylinderComponent.CollisionHeight = 20000
            minac_trigger.CylinderComponent.CollisionRadius = 20000

            trigger_touch_kismet = find_object("Object", "DLC4_Arid_Badlands_p.TheWorld:PersistentLevel.Main_Sequence.MINAC_Fight.SeqEvent_Touch_35")
            bink_movie_kismet = find_object("Object", "DLC4_Arid_Badlands_p.TheWorld:PersistentLevel.Main_Sequence.MINAC_Fight.SeqAct_PlayBinkMovie_1")
            trigger_touch_kismet.OutputLinks[0].Links[0].LinkedOp = None
            for link in bink_movie_kismet.OutputLinks[0].Links:
                trigger_touch_kismet.OutputLinks[0].Links.append(link)