# Borderlands Seed System

A modding library for implementing seeds in randomizer mods for Borderlands series games.

With minimal boilerplate, Seed System provides the following features:
- Customizable and user-friendly UI for players to create seeds, switch between seeds, and copy and paste seeds.
- Seeds can incorporate options that you designate the user should choose from. When a user generates a seed with specific options, those are retained when the seed is copy and pasted.
- Seeds incorporate version numbers, so that your mod can continue to support previous seeds even as you release updates with new features.
- Fully functional out of the box with default behavior for generating seeds, loading seeds, and selecting seeds, but also highly customizable if desired.
- MIT license allows you to bundle Seed System in your mod so that players do not need to install additional requirements.
- Works under the latest SDK for every game.

## Getting Started

It is recommended that you embed the repository for Seed System into your project:
```
git submodule add https://github.com/mopioid/Borderlands-Seed-System seed_system
git submodule update --init
```
You may then begin using it in your code:
```python
from .seed_system import (
    Seed,
    SeedVersionError,
    SeedFormat,
    SeedFormatError,
    BaseSeedOption,
    ValueSeedOption,
    SliderSeedOption,
    SpinnerSeedOption,
    BoolSeedOption,
    DropdownSeedOption,
    GroupedSeedOption,
    NestedSeedOption,
)
```

### Creating Seed Options

If you would like your mod's seeds to encode options that customize how the seed should behave, the first step is to define them.

Seed options are derived from the options found in `mod_base`, and as such are
constructed in an identical manner:
```python
include_missions = BoolSeedOption(
    identifier="Include Missions",
    description="Assign items to missions in this seed",
    value=True,
)
duplicate_count = SliderSeedOption(
    identifier="Item Duplicates",
    description="The maximum number of sources each item can be assigned",
    min_value=1, max_value=10, value=1,
)
allow_hints = SpinnerSeedOption(
    identifier="Allow Hints",
    description="What level of hints should be allowed when playing this seed",
    choices=["None", "Vague", "Spoiler"], value="Spoiler",
)
```
It is important to maintain references to individual seed options, as you will be using them for other purposes later, such as retrieving values from players' seeds.

### Creating Seed Formats

Seed Formats define how your seed looks, as well as what information it encodes, including options and randomness bits. They also allows you to differentiate how seeds of specific versions should behave.
```python
version0 = SeedFormat(
    version=0,
    format_string="xxxxx-xxxxx-xxxxx",
    seed_options=[include_missions, allow_hints]
)
```
The `format_string` you choose determines how your seed will look, as well has how many bits of data it can represent, which in turn determines how many bits of randomness it can store on top of the options it encodes.

In future versions of your mod, you may wish to add additional options, and you may do so without impacting the functionality of existing seeds by creating new seed formats:
```python
version1 = SeedFormat(
    version=1,
    format_string="xxxxx-xxxxx-xxxxx",
    seed_options=[include_missions, duplicate_count, allow_hints]
)
```

### Creating Your Seed Class

Your subclass of `Seed` defines the properties of your seed system, as well as how instances of seeds should behave, such as when enabled or disabled:
```python
class LootSeed(Seed):
    seeds_file = mods_base.SETTINGS_DIR / "Loot Randomizer" / "Seeds.txt"
    seed_formats = version0, version1
    default_version = version1

    def enable(self) -> None:
        randomization = random.Random(self.data)

        if self[include_missions]:
            ...
        if self.seed_format is version1 and self[duplicate_count] == 1:
            ...

    def disable(self) -> None:
        ...
```
Note how your `Seed` subclass instances provide access to its data (including randomness) for seeding random number generators, its format for providing different behavior based on version, as well as the options encoded into it as selected by the player.

### Incorporating Into Your Mod

Your `Seed` subclass also provides the UI elements and other functionality to be inserted into your mod's configuration:
```python
new_seed_menu = LootSeed.new_seed_menu()
new_seed_menu.display_name = "New Loot Randomizer Seed"
new_seed_menu.generate_seed_description = "Create the Loot Randomizer seed."

edit_seeds_button = LootSeed.edit_seeds_button()

select_seed_menu = LootSeed.select_seed_menu()

mod = mods_base.build_mod(
    options=[new_seed_menu, edit_seeds_button, select_seed_menu],
    settings_file=mods_base.SETTINGS_DIR / "Loot Randomizer" / "settings.json",
    on_enable=LootSeed.enable_seed,
    on_disable=LootSeed.disable_seed
)
```
