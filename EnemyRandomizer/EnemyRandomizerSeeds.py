from os.path import exists
from random import Random
from mods_base import SETTINGS_DIR
from . import seed_system

from .EnemyRandomizerLists import BossNames, SmallBosses, MediumBosses, LargeBosses

CharacterBosses: dict = {}

version0 = seed_system.SeedFormat(
    version=0, format_string="xxxxx-xxxxx", seed_options=()
)

class StaticBossesSeed(seed_system.Seed):
    seeds_file = SETTINGS_DIR / "EnemyRandomizer" / "Bosses" / "Boss Seeds.txt"
    seed_formats = (version0,)

    random: Random

    def enable(self) -> None:
        self.random = Random(self.data)
    
        global SmallBosses, MediumBosses, LargeBosses, BossNames, CharacterBosses, RandomizedBosses
        BackupSmall = SmallBosses.copy()
        BackupMedium =  MediumBosses.copy()
        BackupLarge = LargeBosses.copy()
        for name in BossNames:
            if name in SmallBosses:
                CharacterBosses[name] = self.FindUnusedBoss(BackupSmall, SmallBosses)
            elif name in MediumBosses:
                CharacterBosses[name] = self.FindUnusedBoss(BackupMedium, MediumBosses)
            elif name in LargeBosses:
                CharacterBosses[name] = self.FindUnusedBoss(BackupLarge, LargeBosses)

        SeedPath = SETTINGS_DIR / "EnemyRandomizer" / "Bosses" / f"{self}.txt"
        if not exists(SeedPath):
            for key, value in CharacterBosses.items():
                with open(SeedPath, "a") as file:
                    file.write(f"{key}:\n    {value}\n\n")

        return
    

    def FindUnusedBoss(self, ListToUse, BackupList) -> str:
        if len(ListToUse) > 0:
            ReturnName = self.random.choice(ListToUse)
            ListToUse.remove(ReturnName)
            return ReturnName
        else:
            return self.random.choice(BackupList)


StaticBossesSeedMenu = StaticBossesSeed.new_seed_menu()
StaticBossesSeedMenu.display_name = "New Static Bosses Seed"

EditStaticBossesSeed = StaticBossesSeed.edit_seeds_button()
EditStaticBossesSeed.display_name = "Edit Static Bosses Seeds"

SelectStaticBossesSeed = StaticBossesSeed.select_seed_menu()
SelectStaticBossesSeed.display_name = "Select Static Bosses Seed"

