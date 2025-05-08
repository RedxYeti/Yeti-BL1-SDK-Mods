from __future__ import annotations

from weakref import ReferenceType

import mods_base

try:
    from console_mod_menu.screens import screen_stack as console_screens
except ImportError:
    console_screens = ()

from .formats import SeedFormat
from .options import ValueSeedOption

from typing import Any, Callable, Self


type GenerateSeedCallback = Callable[
    [SeedFormat, dict[ValueSeedOption[Any], Any]], None
]
type EditSeedsCallback = Callable[[], None]
type LoadSeedsCallback = Callable[[], list[str]]
type ApplySeedCallback = Callable[[str], None]


def show_message(title: str, message: str) -> None:
    if console_screens:
        print(f"\n[ {title} ]\n{message}\n")

    elif mods_base.Game.get_tree() == mods_base.Game.Willow2:
        from ui_utils.training_box import TrainingBox

        TrainingBox(title=title, message=message).show()

    elif mods_base.Game.get_tree() == mods_base.Game.Oak:
        from ui_utils.tutorial_message import show_modal_tutorial_message  # type: ignore

        show_modal_tutorial_message(
            title=title, msg=message, image_name="TrueVaultHunter"
        )


class NewSeedNested(mods_base.NestedOption):
    _seedsystem_seed_format: SeedFormat
    _seedsystem_on_generate: GenerateSeedCallback
    _seedsystem_generate_button: mods_base.ButtonOption

    @property
    def generate_seed_display_name(self) -> str:
        return self._seedsystem_generate_button.display_name

    @generate_seed_display_name.setter
    def generate_seed_display_name(self, value: str) -> None:
        self._seedsystem_generate_button.display_name = value

    @property
    def generate_seed_description(self) -> str:
        return self._seedsystem_generate_button.description

    @generate_seed_description.setter
    def generate_seed_description(self, value: str) -> None:
        self._seedsystem_generate_button.description = value

    @property
    def generate_seed_description_title(self) -> str:
        return self._seedsystem_generate_button.description_title

    @generate_seed_description_title.setter
    def generate_seed_description_title(self, value: str) -> None:
        self._seedsystem_generate_button.description_title = value

    def __init__(
        self,
        seed_format: SeedFormat,
        on_generate: GenerateSeedCallback,
    ) -> None:
        self._seedsystem_seed_format = seed_format
        self._seedsystem_on_generate = on_generate

        def on_press(
            button: mods_base.ButtonOption,
            menu_ref: ReferenceType[Self] = ReferenceType(self),
        ):
            if menu := menu_ref():
                menu.generate_pressed()

        self._seedsystem_generate_button = mods_base.ButtonOption(
            identifier="GENERATE SEED",
            description="Confirm selections and generate the new seed.",
            on_press=on_press,
        )

        super().__init__(
            identifier="New Seed",
            description="Create a new seed.",
            children=(
                *seed_format.seed_options,
                self._seedsystem_generate_button,
            ),
        )

    def generate_pressed(self) -> None:
        options: dict[ValueSeedOption[Any], Any] = dict()
        for seed_option in self._seedsystem_seed_format.value_seed_options:
            options[seed_option] = seed_option.value

        self._seedsystem_on_generate(self._seedsystem_seed_format, options)


class EditSeedsButton(mods_base.ButtonOption):
    def __init__(self, on_edit: EditSeedsCallback) -> None:
        super().__init__(
            identifier="Edit Seeds",
            description=(
                "Open your list of seeds in a text editor so that you may add"
                " or remove seeds."
            ),
            on_press=lambda _: on_edit(),
        )


class SelectSeedNested(mods_base.NestedOption):
    _seedsystem_on_load: LoadSeedsCallback
    _seedsystem_on_apply: ApplySeedCallback

    _seedsystem_dropdown: SeedDropdown
    _seedsystem_apply_button: mods_base.ButtonOption

    _seedsystem_children: list[mods_base.BaseOption]

    @property
    def apply_button_display_name(self) -> str:
        return self._seedsystem_apply_button.display_name

    @apply_button_display_name.setter
    def apply_button_display_name(self, value: str) -> None:
        self._seedsystem_apply_button.display_name = value

    @property
    def apply_button_description(self) -> str:
        return self._seedsystem_apply_button.description

    @apply_button_description.setter
    def apply_button_description(self, value: str) -> None:
        self._seedsystem_apply_button.description = value

    @property
    def apply_button_description_title(self) -> str:
        return self._seedsystem_apply_button.description_title

    @apply_button_description_title.setter
    def apply_button_description_title(self, value: str) -> None:
        self._seedsystem_apply_button.description_title = value

    @property
    def seed_dropdown_display_name(self) -> str:
        return self._seedsystem_dropdown.display_name

    @seed_dropdown_display_name.setter
    def seed_dropdown_display_name(self, value: str) -> None:
        self._seedsystem_dropdown.display_name = value

    @property
    def seed_dropdown_description(self) -> str:
        return self._seedsystem_dropdown.description

    @seed_dropdown_description.setter
    def seed_dropdown_description(self, value: str) -> None:
        self._seedsystem_dropdown.description = value

    @property
    def seed_dropdown_description_title(self) -> str:
        return self._seedsystem_dropdown.description_title

    @seed_dropdown_description_title.setter
    def seed_dropdown_description_title(self, value: str) -> None:
        self._seedsystem_dropdown.description_title = value

    def __init__(
        self,
        on_load: LoadSeedsCallback,
        on_apply: ApplySeedCallback,
    ) -> None:
        self._seedsystem_on_load = on_load
        self._seedsystem_on_apply = on_apply
        self._seedsystem_dropdown = SeedDropdown(on_load(), on_apply)

        def on_press(
            button: mods_base.ButtonOption,
            menu_ref: ReferenceType[Self] = ReferenceType(self),
        ) -> None:
            if menu := menu_ref():
                menu.apply_pressed()

        self._seedsystem_apply_button = mods_base.ButtonOption(
            identifier="APPLY SEED",
            description=(
                "Confirm selection of the above seed and apply it to your"
                " game."
            ),
            on_press=on_press,
        )

        super().__init__(
            identifier="Select Seed",
            description="Select a seed from your list of saved seeds.",
            children=(
                self._seedsystem_dropdown,
                self._seedsystem_apply_button,
            ),
        )

    @property
    def children(self) -> list[mods_base.BaseOption]:
        seeds = self._seedsystem_on_load()

        if self._seedsystem_dropdown.value in seeds:
            self._seedsystem_dropdown.choices = seeds
        else:
            self._seedsystem_dropdown.choices = [""] + seeds

        self._seedsystem_apply_button.is_hidden = bool(console_screens)

        return self._seedsystem_children

    @children.setter
    def children(  # pyright: ignore[reportIncompatibleVariableOverride]
        self, children: list[mods_base.BaseOption]
    ) -> None:
        self._seedsystem_children = children

    def apply_pressed(self) -> None:
        try:
            self._seedsystem_on_apply(
                self._seedsystem_dropdown._seedsystem_staged  # pyright: ignore[reportPrivateUsage]
            )
            self._seedsystem_dropdown.seedsystem_commit_staged()
        except Exception:
            pass


class SeedDropdown(mods_base.DropdownOption):
    _seedsystem_value: str | None = None
    _seedsystem_staged: str
    _seedsystem_on_apply: ApplySeedCallback

    def __init__(
        self, choices: list[str], on_apply: ApplySeedCallback
    ) -> None:
        self._seedsystem_on_apply = on_apply
        super().__init__(
            identifier="Seed",
            value="",
            choices=[""] + choices,
        )

    @property
    def value(self) -> str:
        if self._seedsystem_value in self.choices:
            return self._seedsystem_value
        return self.choices[0]

    @value.setter
    def value(  # pyright: ignore[reportIncompatibleVariableOverride]
        self, value: str
    ) -> None:
        self._seedsystem_staged = value

        if console_screens:
            try:
                self._seedsystem_on_apply(value)
                self._seedsystem_value = value
            except Exception:
                pass

        elif self._seedsystem_value is None and value != "":
            self._seedsystem_value = value

    def seedsystem_commit_staged(self, value: str | None = None) -> None:
        if value is None:
            self._seedsystem_value = self._seedsystem_staged
        else:
            self._seedsystem_value = value
            self._seedsystem_staged = value
        if self.mod:
            self.mod.save_settings()
