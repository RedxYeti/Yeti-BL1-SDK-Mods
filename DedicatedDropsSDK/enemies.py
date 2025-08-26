from mods_base import get_pc, SliderOption
from unrealsdk import find_object,find_class,load_package,make_struct
from unrealsdk.unreal import UObject 
from random import randint, Random
import time

oidALSlider = SliderOption(
    "Loot Scale Mult",
    4,
    0.1,
    10,
    0.1,
    False,
    description="Item part quality scales with your player level. If you don't like the quality of your drops at your current level, lower this for worse parts or increase it for better parts.\nThe option slider only shows values that end in 0.5 increments so youll have to count. :)"
)



VERY_LOW:int = 2
LOW:int = 10
MEDIUM_LOW:int = 15
MEDIUM:int = 20
COMMON:int = 33

RANDOM_LEGENDARY:int = 8

item_pool_default = find_class('ItemPool').ClassDefaultObject

def spawn_item(pool_def:UObject,pawn:UObject,awesome_level:int) -> UObject:
    _, new_items = item_pool_default.SpawnBalancedInventoryFromPool(
                    pool_def, pawn.GetGameStage(), int(awesome_level), pawn, []
                    )
    return new_items[0]

rng = Random(time.time())

def roll_for_drop(percent_chance:int) -> bool:
    return rng.randint(1, 100) <= percent_chance


def remove_item(inv_manager:UObject,item_name:str) -> None:
    item_in_inv = inv_manager.InventoryChain
    while item_in_inv:
        if item_name in item_in_inv.GetHumanReadableName():
            inv_manager.RemoveFromInventory(item_in_inv)
            break
        item_in_inv = item_in_inv.Inventory
    return


locational_drops = {
    'gd_VaultBoss_Main.population.Pawn_Balance_VaultBoss_Main': 
    make_struct('Vector',X=-12839,Y=6023,Z=11095),

    'gd_Balance_Enemies_Creatures.Rakk.Pawn_Balance_Rakk_Mothrakk': 
    make_struct('Vector',X=-35821, Y=-19287, Z=234),

    'dlc4_gd_Balance_Enemies.MINAC.Pawn_Balance_MINAC_EyeTurret': 
    make_struct('Vector',X=-4009, Y=48055, Z=257),

    'dlc4_gd_Balance_Enemies.ClapTrap.Named.Pawn_Balance_INAC': 
    make_struct('Vector',X=-4009, Y=48055, Z=257),
}

no_vel = make_struct('Vector')

class Enemy:
    registry = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Enemy.registry[cls.balance_state] = cls#type:ignore
    
    def __init__(self) -> None:
        self.pawn: UObject
        self.items_to_drop: list[str] = []

    def on_enemy_death(self):
        if len(self.items_to_drop):
            load_package('DedicatedDropsWeapons')
            load_package('DedicatedDropsGear')
            load_package('DedicatedDropsPools')
            awesome_level = int(get_pc().Pawn.GetExpLevel() * oidALSlider.value)
            for item in self.items_to_drop:
                pool_def = find_object('ItemPoolDefinition', item)
                spawned_item = spawn_item(pool_def, self.pawn, awesome_level)
                if self.balance_state not in locational_drops.keys():#type:ignore
                    spawned_item.GiveTo(self.pawn, False)
                else:
                    spawned_item.DropFrom(locational_drops[self.balance_state], no_vel)#type:ignore


class NineToes(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_NineToes'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Troll')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.MP.Pool_Stalker')
        return super().on_enemy_death()

    
class Pinky(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Skag_Pinky'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Equalizer')
        return super().on_enemy_death()


class Digit(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Skag_Digit'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Anaconda')
        return super().on_enemy_death()
    

class BoneHead(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Bonehead'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, 'Bone Shredder')
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_BoneShredder_Savior')

        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Savior')
        return super().on_enemy_death()    
    

class RoidRagePsycho(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_RoidRagePsycho'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Redemption')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Undertaker')
        return super().on_enemy_death()
    

class Sledge(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Sledge'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Striker')
        return super().on_enemy_death()
    

class MadMel(Enemy):
    balance_state = 'gd_CheetahsPaw.VehicleArchetype.Mad_Mel'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Mongol')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Serpens')
        return super().on_enemy_death()
    

class Krom(Enemy):
    balance_state = 'gd_banditkromboss.Vehicle.Krom_Turret_Archetype'

    def on_enemy_death(self):
        if roll_for_drop(25):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Unforgiven')
        return super().on_enemy_death()


class JaynisKobb(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Kobb_Jaynis'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Bastard')
        return super().on_enemy_death()
    

class TaylorKobb(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Kobb_Taylor'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, 'The Roaster')
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Rhino_TheRoaster')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Rhino')
        return super().on_enemy_death()    


class RakkHive(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.RakkHive.Pawn_Balance_RakkHive'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, 'Leviathan')
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.RakkHive_Leviathan')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Nidhogg')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Jackal')
        return super().on_enemy_death()


class Hanz(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Hanz'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Violator')
        return super().on_enemy_death()
    

class Franz(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Franz'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Gasher')
        return super().on_enemy_death()
    

class BaronFlynt(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_BaronFlynt'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, 'Boom Stick')
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_FriendlyFire_Boomstick')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_FriendlyFire')
        return super().on_enemy_death()
    

class MasterMcCloud(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.CrimsonLance.Pawn_Balance_MasterMcCloud'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.ECannon.Pool_MegaCannon')
        return super().on_enemy_death()
    

set_destroyer:bool = False
class Destroyer(Enemy):
    balance_state = 'gd_VaultBoss_Main.population.Pawn_Balance_VaultBoss_Main'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CombatRifle.Pool_Destroyer')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_LegendaryEridian')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsGear.Shields.Pools.Pool_IronClad')

        global set_destroyer
        if set_destroyer:
            return super().on_enemy_death()
        
        load_package('DedicatedDropsWeapons')
        load_package('DedicatedDropsGear')
        load_package('DedicatedDropsPools')
        destroyer_death = find_object('BodyClassDeathDefinition','gd_VaultBoss_Main.Character.BodyDeath_VaultBoss_Main')
        destroyer_death.ObjectFlags |= 0x4000
        
        destroyer_pools = [
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_Brick",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_BrickShield",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_Lilith",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_LilithShield",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_Mordecai",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_MordecaiShield",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_Roland",
            "DedicatedDropsPools.Pools.DestroyerGear.BossPool_Destroyer_RolandShield",
        ]

        base_pool = destroyer_death.DeathBehaviors[0].ItemPoolList[0]
        for pool in destroyer_pools:
            new_pool = base_pool
            destroyer_death.DeathBehaviors[0].ItemPoolList.append(new_pool)
            destroyer_death.DeathBehaviors[0].ItemPoolList[-1].ItemPool = find_object('ItemPoolDefinition', pool)

        set_destroyer = True
        return super().on_enemy_death()


class Scar(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Skag_Scar'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, "T.K's Wave")
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Bulldog_TKsWave')
        else:
            self.items_to_drop.append("DedicatedDropsWeapons.Pools.CShotgun.Pool_TKsWave")

        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Bulldog')
        return super().on_enemy_death()
    

class Moe(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Alpha_Moe'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, 'Lady Finger')
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.Moe_LadiesFinger')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Volcano')
        return super().on_enemy_death()    
    

class Marley(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Alpha_Marley'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, 'Rider')
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.SecretChest_Sniper_Rider')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_Orion')
        return super().on_enemy_death()
    

class Skagzilla(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Alpha_Skagzilla'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, "Whitting's Elephant Gun")
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.SkagZilla_ElephantGun')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Skullmasher')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Bessie')
        return super().on_enemy_death()
    

class Mothrakk(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Rakk.Pawn_Balance_Rakk_Mothrakk'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, 'The Blister')
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.MothRakk_Blister')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.AShotgun.Pool_CruxCorro')
        return super().on_enemy_death()
    

class KingWeeWee(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_KingWeeWee'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, 'The Spy')
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.KingWeeWee_TheSpy')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Bitch')        
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsGear.Shields.Pools.Pool_Rose')
        return super().on_enemy_death()    


class Reaver(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_Reaver'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, "Reaver's Edge")
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_Penetrator_ReaversEdge')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_Penetrator')
        return super().on_enemy_death()


class Slither(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Scythids.Pawn_Balance_Scythid_Slither'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, "The Dove")
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsPools.CustomPools.Slither_TheDove')
        else:
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_TheDove')

        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Hornet')
        return super().on_enemy_death()

set_rakkinishu:bool = False
class Rakkinishu(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Rakk.Pawn_Balance_Rakk_Rakkinishu'

    def on_enemy_death(self):
        global set_rakkinishu
        if not set_rakkinishu:
            ai_def = find_object("AIPawnBalanceDefinition", self.balance_state)
            for item in ai_def.DefaultItemPoolList:
                if item.ItemPool._path_name() == 'gd_itempools.BOSSPools.Pool_Rakkinishu_Shield':
                    item.ItemPool.BalancedItems[0].Probability.BaseValueConstant = 1 
                    item.ItemPool.BalancedItems[0].Probability.InitializationDefinition = None
                    item.ObjectFlags |= 0x4000
                    break
            set_rakkinishu = True
        remove_item(self.pawn.InvManager, "The Sentinel")
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.Rakkinishu_TheSentinel')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Draco')
        return super().on_enemy_death()
        

class OneEyedJack(Enemy):
    balance_state = 'gd_Balance_Enemies_Humans.Bandits.Named.Pawn_Balance_OneEyeJack'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Defiler')
        return super().on_enemy_death()
            

class Helob(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Spiderants.Pawn_Balance_Spiderant_Helob'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_InvaderSniper')
        return super().on_enemy_death()
    

class Widowmaker(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Spiderants.Pawn_Balance_Spiderant_Widowmaker'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_Cobra')
        return super().on_enemy_death()    
    

class Skrappy(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Skags.Pawn_Balance_Skag_Skrappygrownup'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Bulldog')
        return super().on_enemy_death()
    

class Bleeder(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Scythids.Pawn_Balance_Scythid_Bleeder'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, "Nailer")
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.Bleeder_Nailer')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Surkov')
        return super().on_enemy_death()
    

class KingAracobb(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Spiderants.Pawn_Balance_Spiderant_KingAracobb'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Rebel')
        return super().on_enemy_death()


class QueenTarantella(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Spiderants.Pawn_Balance_Spiderant_QueenTarantella'

    def on_enemy_death(self):
        remove_item(self.pawn.InvManager, "Patton")
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.Queen_Patton')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Chimera')
        return super().on_enemy_death()    


class HankReiss(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.WereSkag.Pawn_Balance_HankReiss'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Firehawk')
        return super().on_enemy_death()


class DrNed(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.Ned.Pawn_Balance_NedEnemy'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Wildcat')
        return super().on_enemy_death()
    

class UndeadNed(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.Ned.Pawn_Balance_UndeadNed'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Defiler')
        return super().on_enemy_death()
        

class PumpkinHead(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.Golem.Pawn_Balance_Pumpkinhead'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Hellfire')
        return super().on_enemy_death()
            

class WhiskeyWesley(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.WereSkag.Pawn_Balance_WhiskeyWesley'

    def on_enemy_death(self):
        com_chance = randint(1,100)
        if com_chance >= 66:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Roland.Pool_Atlas_Champion')
        elif com_chance >= 33:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Roland.Pool_SnS_Gunman')
        else:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Roland.Pool_Vladoff_Patriot')
        return super().on_enemy_death()
    

class Bigfoot(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.WereSkag.Pawn_Balance_BigFoot'

    def on_enemy_death(self):
        com_chance = randint(1,100)
        if com_chance >= 66:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Mordecai.Pool_Anshin_PeaceKeeper')
        elif com_chance >= 33:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Mordecai.Pool_Hyperion_Sharpshooter')
        else:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Mordecai.Pool_Jakobs_Gunfighter')
        return super().on_enemy_death()    
    

class Redjack(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.WereSkag.Pawn_Balance_RedJack'

    def on_enemy_death(self):
        com_chance = randint(1,100)
        if com_chance >= 66:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Lilith.Pool_Dahl_Professional')
        elif com_chance >= 33:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Lilith.Pool_Eridian_Warrior')
        else:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Lilith.Pool_Maliwan_Specialist')
        return super().on_enemy_death()
        

class JackieOCallahan(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.WereSkag.Pawn_Balance_FatherOCallahan'

    def on_enemy_death(self):
        com_chance = randint(1,100)
        if com_chance >= 66:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Brick.Pool_CommonMan_Tediore')
        elif com_chance >= 33:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Brick.Pool_Pangolin_Tank')
        else:
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.Loyalty.Brick.Pool_Torgue_Badass')
        return super().on_enemy_death()
    

class FrankenBill(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.Franken.Pawn_Balance_FrankenBill'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SemiSniper.Pool_Orion')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsGear.Shields.Pools.Pool_Omega')
        return super().on_enemy_death()    


class Vulcana(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_CLAssassinNamed1'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Protector_ChiquitoAmigo')
        else:
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_ChiquitoAmigo')

        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Protector')
        return super().on_enemy_death()
    

class MrShank(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Prisoners.Named.Pawn_Balance_Shank'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.MP.Pool_Reaper')
        return super().on_enemy_death()       


class Knoxx(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_Knoxx'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_InvaderPistol')
        if roll_for_drop(VERY_LOW):
            hybrid_chance = randint(1,100)
            if hybrid_chance >= 25:
                self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Nemesis')
            else:
                self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Nemesis_Invader')
        return super().on_enemy_death()    
   

class Hera(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_CLAssassinNamed2'

    def on_enemy_death(self):
        self.items_to_drop.append('DedicatedDropsPools.CustomPools.Hera_AthenasWisdom')
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Spectre')
        return super().on_enemy_death()
    

class Minerva(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_CLAssassinNamed3'

    def on_enemy_death(self):
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Orge')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.ERifle.Pool_Firebomb')
        return super().on_enemy_death()    
    

class Chaz(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Prisoners.Named.Pawn_Balance_Chaz'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, 'Bone Shredder')
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_BoneShredder_Savior')

        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Savior')
        return super().on_enemy_death()    
    

class Kyros(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_Kyros'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn.InvManager, "Kyros' Power")
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Cyclops_KyrosPower')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.BoltSniper.Pool_Cyclops')
        return super().on_enemy_death()    
    

class Typhon(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_Typhon'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.MP.Pool_Vengeance')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.SMG.Pool_Tsunami')
        return super().on_enemy_death()    
        

class Motorhead(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Bandits.Named.Pawn_Balance_MotorHead'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsPools.CustomPools.Weapons_Unique_MotorHead')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.AShotgun.Pool_Hammer')
        return super().on_enemy_death()    
            

class Skyscraper(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Drifters.Named.Pawn_Balance_Named1'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.ERifle.Pool_SplatterGun')
        return super().on_enemy_death()    
    

class Ajax(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_Ajax'

    def on_enemy_death(self):
        if roll_for_drop(VERY_LOW):
            remove_item(self.pawn, "Ajax's Spear")
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Ogre_AjaxSpear')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Ogre')
        return super().on_enemy_death()    
        

class Ceresia(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_CLAssassinNamed4'

    def on_enemy_death(self):
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Truxican')
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Defender')
        return super().on_enemy_death()    
    

class Helicon(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Named.Pawn_Balance_CLAssassinNamed5'

    def on_enemy_death(self):
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Marine')
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Troll')
        return super().on_enemy_death()    
        

class SteeleTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.SteeleTrap.Pawn_Balance_SteeleTrap'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.MP.Pool_Thanatos')
        return super().on_enemy_death()    
class SteeleTrap2(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.SteeleTrap.Pawn_Balance_SteeleTrap2'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.MP.Pool_Thanatos')
        return super().on_enemy_death()            


class NedTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.NedTrap.Pawn_Balance_NedTrap'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CombatRifle.Pool_Raven')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Revolver.Pool_Aries')
        return super().on_enemy_death()    


class KnoxxTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.KnoxxTrap.Pawn_Balance_KnoxxTrap'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Gemini')
        return super().on_enemy_death()   
class KnoxxTrap2(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.KnoxxTrap.Pawn_Balance_KnoxxTrap2'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Repeaters.Pool_Gemini')
        return super().on_enemy_death()     


class UndeadNedTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.NedTrap.Pawn_Balance_UndeadNedTrap'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.AShotgun.Pool_CruxExplo')
        return super().on_enemy_death()    


class MINAC(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.MINAC.Pawn_Balance_MINAC_EyeTurret'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Nidhogg')
        return super().on_enemy_death()
    

class INAC(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.ClapTrap.Named.Pawn_Balance_INAC'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.LMG.Pool_Revolution')
        if roll_for_drop(VERY_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CombatRifle.Pool_Avenger')
        return super().on_enemy_death()    
    

class SuperBadSoldier(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.Hyperion.Named.Pawn_Balance_SuperbadSoldier'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM_LOW):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.AShotgun.Pool_Butcher')
        return super().on_enemy_death()    


class CluckTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.ClapTrap.Named.Pawn_Balance_DLC4_Clucktrap'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CombatRifle.Pool_Guardian')
        return super().on_enemy_death()


class DFault(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.Bandits.Named.Pawn_Balance_D-Fault'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.CShotgun.Pool_Hydra')
        return super().on_enemy_death()


class RakkTrapHive(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.RakkTrapHive.Pawn_Balance_RakkTrapHive'

    def on_enemy_death(self):
        if roll_for_drop(MEDIUM):
            self.items_to_drop.append('DedicatedDropsWeapons.Pools.Launchers.Pool_Mongol')
        return super().on_enemy_death()


class BadassDevastator(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.CrimsonLance.Pawn_Balance_BadassDevastator'

    def on_enemy_death(self):
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Marine')
        return super().on_enemy_death()


class TruxicanWrestler(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Midgets.Named.Pawn_Balance_TWrestler'

    def on_enemy_death(self):
        if roll_for_drop(COMMON):
            self.items_to_drop.append('DedicatedDropsGear.Coms.Pools.NonLoyalty.Pool_Truxican')
        if roll_for_drop(RANDOM_LEGENDARY):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class MeatPopsicle(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Midgets.Named.Pawn_Balance_MeatPop'

    def on_enemy_death(self):
        if roll_for_drop(RANDOM_LEGENDARY):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class MiniSteve(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Midgets.Named.Pawn_Balance_MiniSteve'

    def on_enemy_death(self):
        if roll_for_drop(RANDOM_LEGENDARY):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class DumpsterDiver(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Midgets.Named.Pawn_Balance_DumpsterDiver'

    def on_enemy_death(self):
        if roll_for_drop(RANDOM_LEGENDARY):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class CrimsonShorty(Enemy):
    balance_state = 'dlc3_gd_balance_enemies.Midgets.Named.Pawn_Balance_MidgetLance'

    def on_enemy_death(self):
        if roll_for_drop(RANDOM_LEGENDARY):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class LootGoon(Enemy):
    balance_state = 'dlc1_gd_balance_enemies.Franken.Pawn_Balance_LootGoon'

    def on_enemy_death(self):
        if roll_for_drop(LOW):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()


class BloatedRakk(Enemy):
    balance_state = 'gd_Balance_Enemies_Creatures.Rakk.Pawn_Balance_Rakk_Bloated'

    def on_enemy_death(self):
        if roll_for_drop(3):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()
class BloatedRakkTrap(Enemy):
    balance_state = 'dlc4_gd_Balance_Enemies.Rakk.Pawn_Balance_Rakk-trap_Bloated'

    def on_enemy_death(self):
        if roll_for_drop(3):
            self.items_to_drop.append('DedicatedDropsPools.Pools.Legendary.Pool_Legendary_All')
        return super().on_enemy_death()