from mods_base import SliderOption, BoolOption, SpinnerOption


oidWanderingBosses: SliderOption = SliderOption(
    "Wandering Bosses",
    1,
    0,
    100,
    1,
    display_name="Wandering Bosses",
    description="The percent change bosses randomly spawn between 1 and 100, set to 0 to turn this off. 100 means every* enemy will be a boss."
)

oidStaticBosses: BoolOption = BoolOption(
    "Static Bosses",
    False,
    "On",
    "Off",
    display_name="Static Bosses",
    description="With this on, vanilla boss spawns will be set to specific bosses per save. Check the settings folder in sdk mods for your saves bosses after generating them."
)

oidEnemyAllegiance: BoolOption = BoolOption(
    "Enemy Allegiance",
    True,
    "Everyone hates the player",
    "Everyone keeps their vanilla allegiance",
    display_name="Enemy Allegiance",
    description="Everyone hates the player will set all the enemies to the same allegiance"
                "\nEveryone keeps their vanilla allegiance means enemies will fight each other." 
                "\nThis changing option requires a restart if you've already loaded in once."
)

oidStrictness: SpinnerOption = SpinnerOption(
                            "Randomizer Strictness",
                            value="Strict",
                            choices=["Strict", "Chaos Light", "Full Chaos"],
                            wrap_enabled = True,
                            description="Choose how strict the randomizer is."
                            "\nStrict means normal enemies replace normal enemies, and badasses replace badasses. (recommended)"
                            "\nChaos Light means normal and badasses are mixed, bosses still only spawn bosses."
                            "\nFull Chaos means normal, badasses and bosses have no restrictions."
                            )



"""
TODO
"Spike", enemy

no weapons, fix min gamestage

"""