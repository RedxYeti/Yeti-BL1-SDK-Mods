from unrealsdk import find_object, load_package, make_struct #type: ignore
from unrealsdk.hooks import Type #type: ignore
from unrealsdk.unreal import UObject, WrappedStruct, BoundFunction #type: ignore
from mods_base import build_mod, EInputEvent, keybind, hook, BoolOption #type: ignore
from typing import Any
bLookingAtVendor: bool = False
bCanBuy: bool = False
bCanBuyHealth: bool = False
bFirstTimeSetup: bool = False

MostHealthBack: list = ["", 0]

CurrentPC: UObject = None
CurrentVendor: UObject = None

Grenade: UObject = None
CombatRifle: UObject = None
Repeater: UObject = None
Revolver: UObject = None
Rocket: UObject = None
Shotgun: UObject = None
SMG: UObject = None
Sniper: UObject = None
GrenadeBal: UObject = None
RevolverBal: UObject = None
RocketLauncherBal: UObject = None
ResourcePoolsPT1: dict = {}
ResourcePoolsPT2: dict = {}
HealthVials: dict = {}

def FirstTimeSetup():
    global  Grenade, CombatRifle, Repeater, Revolver, Rocket, Shotgun, SMG, Sniper, GrenadeBal, RevolverBal, RocketLauncherBal, ResourcePoolsPT1, ResourcePoolsPT2, HealthVials
    Grenade = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Grenade_Protean_Pool')
    CombatRifle = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Combat_Rifle_Pool')
    Repeater = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Repeater_Pistol_Pool')
    Revolver = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Revolver_Pistol_Pool')
    Rocket = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Rocket_Launcher_Pool')
    Shotgun = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Combat_Shotgun_Pool')
    SMG = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Patrol_SMG_Pool')
    Sniper = find_object('ResourcePoolDefinition', 'd_resourcepools.AmmoPools.Ammo_Sniper_Rifle_Pool')

    load_package("gd_itemgrades")
    GrenadeBal = find_object('InventoryBalanceDefinition', 'gd_itemgrades.Ammo_Shop.ItemGrade_AmmoShop_Grenade')
    GrenadeBal.ObjectFlags |= 0x4000
    RevolverBal = find_object('InventoryBalanceDefinition', 'gd_itemgrades.Ammo_Shop.ItemGrade_AmmoShop_RevolverPistol')
    RevolverBal.ObjectFlags |= 0x4000
    RocketLauncherBal = find_object('InventoryBalanceDefinition', 'gd_itemgrades.Ammo_Shop.ItemGrade_AmmoShop_RocketLauncher')
    RocketLauncherBal.ObjectFlags |= 0x4000

    for Balance in [GrenadeBal, RevolverBal, RocketLauncherBal]:
        Balance.Manufacturers[0].Grades[0].GameStageRequirement.MinGameStage = 0

    ResourcePoolsPT1 = {
                        Grenade: [3, 9, 0],
                        CombatRifle: [54, 6, 0],
                        Repeater: [54, 35, 0],
                        Revolver: [18, 56, 0],
                        Rocket: [12, 8, 0],
                        Shotgun: [24, 70, 0],
                        SMG: [72, 56, 0],
                        Sniper: [18, 70, 0],
                        }

    ResourcePoolsPT2 = {
                        Grenade: [3, 98, 0],
                        CombatRifle: [108, 63, 0],
                        Repeater: [108, 35, 0], 
                        Revolver: [36, 56, 0], 
                        Rocket: [24, 84, 0],
                        Shotgun: [48, 70, 0], 
                        SMG: [144, 56, 0],
                        Sniper: [36, 70, 0], 
                        }
    HealthVials = {
                    "HealthVial_1": [20, 105, 0],
                    "HealthVial_2": [40, 210, 0],
                    "HealthVial_3": [80, 315, 0],
                    "HealthVial_4": [120, 420, 0],
                    "HealthVial_5": [200, 525, 0],
                    }
    return

#stolen from ry :)
def display_hud_message(pc, title: str, msg: str, msg_type: int = 0, duration: float = 1.5):
    if not oidShowMessage.value:
        return
    white = make_struct("Core.Object.Color", B=255, G=255, R=255, A=255)

    hud = pc.myHUD
    if hud is None:
        return

    hud_movie = hud.GetHUDMovie()
    if hud_movie is None:
        return

    scaled_duration = max(0.005, duration)

    hud_movie.AddTrainingText(
        0, msg, title, scaled_duration, white, "", False, 0.0, None, True
    )

def GetCost(PC):
    for pool in ResourcePoolsPT1:
        if pool not in PC.ResourcePoolManager.ResourcePools:
            PC.ResourcePoolManager.CreatePool(pool)

    CurrentPT = ResourcePoolsPT1 if PC.GetCurrentPlaythrough() == 0 else ResourcePoolsPT2
    TotalCost = 0
    for pool in PC.ResourcePoolManager.ResourcePools:
        if pool and str(pool.Definition.Name).startswith("Ammo"):
            NeededAmount = 0
            if pool.CurrentValue < pool.MaxValue:
                CurrentValue = pool.CurrentValue 
                MaxValue = pool.MaxValue
                AmmoPer = CurrentPT[pool.Definition][0]
                NeededAmount = (MaxValue - CurrentValue + AmmoPer - 1) // AmmoPer
                TotalCost += (NeededAmount * CurrentPT[pool.Definition][1])
            CurrentPT[pool.Definition][2] = NeededAmount
                
    return TotalCost


def GetCostHealth(PC, VendingMachine):
    global HealthVials, MostHealthBack
    for item in VendingMachine.ShopInventory:
        try:
            if str(item.DefinitionData.ItemDefinition.Name).startswith("HealthVial"):
                AmountHealed = item.DefinitionData.ItemDefinition.Behaviors.OnUsed[0].AttributeEffect.SkillEffectDefinitions[0].BaseModifierValue.BaseValueConstant * 2
                if AmountHealed > MostHealthBack[1]:
                    MostHealthBack = [item.DefinitionData.ItemDefinition.Name, AmountHealed]
        except:
            continue

    Cost = 0
    for pool in PC.ResourcePoolManager.ResourcePools:
        if pool.Definition.Name == "HealthPool":
            NeededAmount = 0
            if pool.CurrentValue < pool.MaxValue:
                CurrentValue = pool.CurrentValue 
                MaxValue = pool.MaxValue
                AmmoPer = HealthVials[MostHealthBack[0]][0]
                NeededAmount = (MaxValue - CurrentValue + AmmoPer - 1) // AmmoPer
                Cost = (NeededAmount * HealthVials[MostHealthBack[0]][1])
            HealthVials[MostHealthBack[0]][2] = NeededAmount
        
    return Cost


@keybind(identifier="Purchase Ammo", key=None, event_filter=EInputEvent.IE_Pressed)
def KeyBindHit():
    global bCanBuy, CurrentPC, bLookingAtVendor, CurrentVendor, bCanBuyHealth, MostHealthBack

    if not bLookingAtVendor or not CurrentPC or not CurrentVendor:
        return

    if bCanBuy:
        CurrentPT = ResourcePoolsPT1 if CurrentPC.GetCurrentPlaythrough() == 0 else ResourcePoolsPT2
        CurrentPC.myHUD.HUDMovie.PlayUISound('ChaChing')
        CurrentPC.PlayerReplicationInfo.AddCurrencyOnHand(-(int(GetCost(CurrentPC))))
        GrenadeIndex = 0
        for i in range(30):
            try:
                item = CurrentVendor.ShopInventory[i]
                if item.DefinitionData.ItemDefinition.Name.startswith("AmmoShop"):
                    GrenadeIndex = i
                    break
            except:
                continue
        
        for key, value in CurrentPT.items():
            if value[2] > 0:
                for i in range(int(value[2])):
                    CurrentVendor.PlayerBuyItem(CurrentVendor.ShopInventory[GrenadeIndex], CurrentPC)
            GrenadeIndex += 1

        CurrentPC.myHUD.HUDMovie.ClearTrainingText(0)
        bLookingAtVendor = False
        bCanBuy = False
        bCanBuyHealth = False
        CurrentPC = None
        CurrentVendor = None

    elif bCanBuyHealth:
        CurrentPC.myHUD.HUDMovie.PlayUISound('ChaChing')
        CurrentPC.PlayerReplicationInfo.AddCurrencyOnHand(-(int(GetCostHealth(CurrentPC, CurrentVendor))))
        VialIndex = 0
        for i in range(30):
            try:
                item = CurrentVendor.ShopInventory[i]
                if item.DefinitionData.ItemDefinition.Name == MostHealthBack[0]:
                    VialIndex = i

            except:
                continue

        for i in range(int(HealthVials[MostHealthBack[0]][2])):
            CurrentVendor.PlayerBuyItem(CurrentVendor.ShopInventory[VialIndex], CurrentPC)

        CurrentPC.myHUD.HUDMovie.ClearTrainingText(0)
        bLookingAtVendor = False
        bCanBuy = False
        bCanBuyHealth = False
        CurrentPC = None
        CurrentVendor = None
    
    bLookingAtVendor = False
    bCanBuyHealth = False
    bCanBuy = False
    CurrentPC = None
    CurrentVendor = None
    return


@hook("WillowGame.WillowHUDGFxMovie:ShowToolTip", Type.POST)
def ShowToolTip(obj: UObject, args: WrappedStruct, ret: Any, func: BoundFunction):
    global bLookingAtVendor, bCanBuy, CurrentPC, CurrentVendor, bCanBuyHealth, bFirstTimeSetup
    if not bFirstTimeSetup:
        FirstTimeSetup()
        bFirstTimeSetup = True

    if args.HUDIcon == 4:
        PC = obj.WPlayerOwner[0]
        VendingMachine = PC.CurrentUsableObject

        if not VendingMachine or VendingMachine.ShopType == 0:
            return
        
        PlayerCash = PC.PlayerReplicationInfo.GetCurrencyOnHand() 
        DisplayedPlayerCash = PlayerCash if PlayerCash < 9999999 else 9999999
        if VendingMachine.ShopType == 1:
            Title = "Ammo Vendor"
            bLookingAtVendor = True
            AmmoCost = GetCost(PC)
            if AmmoCost > 0:
                if PlayerCash > AmmoCost:
                    Message = (f"Max Out Ammo? \n\n"
                                f"Total Cost ${int(AmmoCost)}\n\n"
                                f"Available Cash ${DisplayedPlayerCash}\n"
                                )
                    bCanBuy = True
                    CurrentPC = PC
                    CurrentVendor = VendingMachine
                else:
                    Message =  "Not enough money!"
            else:
                Message = "Already at max ammo!"

        elif VendingMachine.ShopType == 2:
            Title = "Health Vendor"
            bLookingAtVendor = True
            HealthCost = GetCostHealth(PC, VendingMachine)
            if HealthCost > 0:
                if PlayerCash > HealthCost:
                    Message = (f"Max Out Health? \n\n"
                                f"Total Cost ${int(HealthCost)}\n\n"
                                f"Available Cash ${DisplayedPlayerCash}\n"
                                )
                    bCanBuyHealth = True
                    CurrentPC = PC
                    CurrentVendor = VendingMachine
                else:
                    Message =  "Not enough money!"
            else:
                Message = "Already at max health!"

        display_hud_message(PC, Title, Message, 0, 999999)

    elif args.HUDIcon == 0 and bLookingAtVendor:
        bCanBuy = False
        bCanBuyHealth = False
        CurrentPC = None
        CurrentVendor = None
        bLookingAtVendor = False
        PC = obj.WPlayerOwner[0]
        obj.ClearTrainingText(0)


oidShowMessage = BoolOption(
    "Show Message",
    True,
    "On",
    "Off",
    description="Enable or disable the hud message that shows when you look at the vendors."
)


build_mod()
