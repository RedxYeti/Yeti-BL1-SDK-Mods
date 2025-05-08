from base64 import b32encode, b32decode
import os
from pathlib import Path
from random import getrandbits
from weakref import ReferenceType, WeakValueDictionary

import mods_base

from .formats import SeedFormat, VERSION_WIDTH, DIGIT_PLACEHOLDERS
from .options import ValueSeedOption
from . import ui

from typing import Any, ClassVar, IO, Self, Sequence, overload


class SeedVersionError(Exception):
    version: int

    def __init__(self, version: int, *args: object) -> None:
        self.version = version
        super().__init__(*args)


class seed_type(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[type],
        namespace: dict[str, Any],
        **kwds: Any,
    ):
        if not bases:
            return super().__new__(cls, name, bases, namespace, **kwds)

        if not isinstance(namespace.get("seeds_file"), Path):
            raise NotImplementedError(
                f"{name} must override `seeds_file` to define a Path object to"
                " the seeds directory"
            )

        seed_formats: Sequence[SeedFormat] | None = namespace.get(
            "seed_formats"
        )
        if not seed_formats:
            raise NotImplementedError(
                f"{name} must override `seed_formats` to provide a sequence of"
                " at least one SeedFormat"
            )

        versions: set[int] = set()
        for seed_format in seed_formats:
            if seed_format.version in versions:
                raise ValueError(
                    f"{name} defines version {seed_format.version} multiple"
                    " times"
                )
            versions.add(seed_format.version)

        namespace.setdefault("default_version", seed_formats[-1])

        namespace["_new_seed_menus"] = WeakValueDictionary()
        namespace["_edit_seed_button"] = lambda: None
        namespace["_select_seed_menu"] = lambda: None

        return super().__new__(cls, name, bases, namespace, **kwds)


class Seed(metaclass=seed_type):
    """
    An abstract class that is at the center of your seed system. To utilize the
    seed system, you begin by creating a subclass of Seed and overriding the
    necessary parameters. Your subclass then provides the functionality you can
    use to begin working with seeds in your mod.
    """

    seed_formats: ClassVar[Sequence[SeedFormat]]
    """
    Override to define the versions of this seed that you implement, each one
    described by a SeedFormat object; see: `SeedFormat`.
    
    In maintaining your mod, you will likely want to be able to make changes in
    the future, and ones that affect how seeds function (e.g. adding additional
    options or otherwise altering the algorithm by which seeds' randomness
    affects the final gameplay changes). However, you will likely also still
    want users to be able to continue using older seeds that they created in
    previous versions of your mod, even after they have updated.

    To accomplish this, the contents of `seed_formats` can be ammended with
    additional SeedFormats at any time, while also leaving the previous ones in
    place unmodified. Users seeds will automatically be matched with the
    correct SeedFormat object when loaded, and thus behave as expected,
    provided your mod continues to handle the same SeedFormat objects in the
    same manner as it always has.
    """
    default_version: ClassVar[SeedFormat]
    """
    Optionally override to specify the SeedFormat (and thus version) that
    should be used when users create new seeds. If not specified, the last
    entry in `versions` will be used.
    """

    seeds_file: ClassVar[Path]
    """
    Override to specify a Path object specifying where the file containing the
    user's list of seeds should be stored. It is recommended to store this file
    in a directory where your mod also stores its settings file, for example.
    """

    @classmethod
    def open_seeds_file(
        cls, mode: str = "r", show_error: bool = True
    ) -> IO[str]:
        """
        Attempt to open the file located at `seeds_file`, creating its parent
        directories if they do not exist. Raises OSError if either fails.

        Args:
            mode:
                The file mode; see builtin `open()`.
            show_error:
                If an error occurs attempting to open the file, should it be
                presented to the user in a dialog box.
        Returns:
            The IO object for the seeds file.
        """
        try:
            os.makedirs(cls.seeds_file.parent, exist_ok=True)
            if not os.path.exists(cls.seeds_file):
                with open(cls.seeds_file, "w"):
                    pass
            return open(cls.seeds_file, mode, encoding="utf-8")
        except OSError as error:
            if show_error:
                ui.show_message(
                    f"Failed to Open Seeds File",
                    f"Could not open the seeds file at {cls.seeds_file}:\n\n"
                    f"{error}",
                )
            raise error

    @classmethod
    def seed_format_for_version(
        cls, version: int | SeedFormat | None = None
    ) -> SeedFormat:
        """
        Obtain the seed format object for the given version. Raises
        `SeedVersionError` if no format exists for the version.

        Args:
            version:
                If None, returns the seed format at `default_version`.

                If a version number, returns the seed format with the matching
                `version` in `seed_formats`.

                If a SeedFormat object, the same SeedFormat is returned after
                asserting that it does exist in `seed_formats`.

        Returns:
            The `SeedFormat` instance representing the seed format for the
            given version.
        """
        match version:
            case None:
                return cls.default_version
            case int():
                for seed_format in cls.seed_formats:
                    if version == seed_format.version:
                        return seed_format
            case SeedFormat():
                if version in cls.seed_formats:
                    return version
                version = version.version

        raise SeedVersionError(
            version, f"{cls.__name__} does not define seed version {version}"
        )

    _new_seed_menus: ClassVar[WeakValueDictionary[int, ui.NewSeedNested]]

    @classmethod
    def new_seed_menu(
        cls, version: SeedFormat | int | None = None
    ) -> ui.NewSeedNested:
        """
        Obtain a Mod Menu NestedOption representing a "New Seed" menu for the
        given seed format. You may insert this object anywhere in your mod's
        options.

        Args:
            version:
                The specific seed format object (or integer representing a seed
                format object's version) the new seed menu should generate. If
                not specified, `default_version` will be used.
        Returns:
            The Mod Menu NestedOption representing a "New Seed" menu.
        """
        seed_format = cls.seed_format_for_version(version)

        if not (menu := cls._new_seed_menus.get(seed_format.version)):
            menu = ui.NewSeedNested(seed_format, cls._new_seed_generated)
            cls._new_seed_menus[seed_format.version] = menu
        return menu

    _edit_seed_button: ClassVar[ReferenceType[ui.EditSeedsButton]]

    @classmethod
    def edit_seeds_button(cls) -> ui.EditSeedsButton:
        """
        Obtain a Mod Menu ButtonOption for opening the user's `Seed List.txt`
        in their default text editor. You may insert this object anywhere in
        your mod's options.
        """
        if not (button := cls._edit_seed_button()):
            button = ui.EditSeedsButton(cls.edit_seeds)
            cls._edit_seed_button = ReferenceType(button)
        return button

    _select_seed_menu: ClassVar[ReferenceType[ui.SelectSeedNested]]

    @classmethod
    def select_seed_menu(cls) -> ui.SelectSeedNested:
        """
        Obtain a Mod Menu NestedOption containing the seed selection menu. You
        may insert this object anywhere in your mod's options - doing so also
        stores the user's last selected seed in your mod's options.
        """
        if not (menu := cls._select_seed_menu()):
            menu = ui.SelectSeedNested(cls.load_seeds, cls._seed_selected)
            cls._select_seed_menu = ReferenceType(menu)
        return menu

    @classmethod
    def _new_seed_generated(
        cls, seed_format: SeedFormat, options: dict[ValueSeedOption[Any], Any]
    ) -> None:
        seed = cls.new_seed_generated(seed_format, options)

        with cls.open_seeds_file("a+") as file:
            file.seek(0, 0)
            seeds = file.read()

            if len(seeds) > 0 and seeds[-1] not in "\n\r":
                file.write("\n")

            if seed.string not in seeds:
                file.write(seed.string + "\n")

        if menu := cls._select_seed_menu():
            menu._seedsystem_dropdown.seedsystem_commit_staged(seed.string)

        cls.enable_seed(seed)

        ui.show_message(
            "Seed Generated and Applied",
            "You will now see the seed's randomization in your game.",
        )

    @classmethod
    def new_seed_generated(
        cls, seed_format: SeedFormat, options: dict[ValueSeedOption[Any], Any]
    ) -> Self:
        """
        Called when the user confirms generation of a new seed in the seed
        generation menu. You may override this if you would like provide custom
        behavior at such a time, or to customize the generated seed instance.

        Args:
            seed_format:
                The SeedFormat of the new seed.
            options:
                A dict containing the options in the SeedFormat paired with the
                values the user selected.
        Returns:
            A new seed instance with the specified format and options.
        """
        return cls(version=seed_format, options=options)

    @classmethod
    def edit_seeds(cls) -> None:
        """
        Called when the user clicks the edit seeds button. Override to provide
        custom behavior at such a time.
        """
        with cls.open_seeds_file("a+"):
            pass
        os.startfile(cls.seeds_file)

    @classmethod
    def load_seeds(cls) -> list[str]:
        """
        Called when the list of seeds is loaded from the seeds file to be shown
        in the seed selection menu. The seeds file is simply parsed into lines
        stripped of whitespace, and therefor entries are not guaranteed to be
        valid seeds (validation is performed when the user ultimately selects
        an entry).

        You may override this method if you would like to customize the list
        of items presented to the user in the seed selection menu.

        Returns:
            The list of strings representing the entries in the seeds file.
        """
        with cls.open_seeds_file() as file:
            return [line.strip() for line in file]

    @classmethod
    def _seed_selected(cls, string: str) -> None:
        try:
            seed = cls.seed_selected(string)
        except SeedVersionError as error:
            ui.show_message(
                "Incorrect Version",
                f"Seed {string} is incompatible with this version. To use it,"
                " install a version of that supports seeds of version"
                f" {error.version}",
            )
            raise error
        except Exception as error:
            ui.show_message("Invalid Seed", f"Seed '{string}' is not valid.")
            raise error

        cls.enable_seed(seed)

        ui.show_message(
            "Seed Applied",
            f"Seed {string} has been applied. You will now see the changes in"
            " your game.",
        )

    @classmethod
    def seed_selected(cls, string: str) -> Self:
        """
        Called when the user selects an entry in the seed selection menu. You
        may override this method to provide custom behavior at such a time, or
        to customize the seed that is produced from the selected entry.

        Args:
            string:
                The entry selected by the user in the seed selection menu.
        Returns:
            The seed instance represented by the selected entry.
        """
        return cls(string)

    current_seed: ClassVar[Self | None] = None
    """
    The seed currently enabled via `enable_seed()`, if any.
    """

    @classmethod
    def enable_seed(cls, seed: Self | None = None) -> None:
        """
        Enable the specified seed, or the last enabled seed as per the setting
        saved via `select_seed_menu()`.

        `enable()` is invoked on the newly enabled seed, and the value of
        `current_seed` is updated to reference it.

        If any seed was already enabled as per `current_seed`, `disable()` is
        first invoked on it.

        If the specified seed equals the seed in `current_seed`, then this
        method does nothing.

        Args:
            seed:
                If provided, the specified seed will be enabled.

                Alternatively, invoking this method with no arguments can be
                used to load the last enabled seed, as saved to your mod's
                settings via `select_seed_menu()`.
        """
        if not seed:
            if not (menu := cls._select_seed_menu()):
                raise RuntimeError(
                    "Invoking enable_seed() with no arguments to enable the"
                    " seed stored in settings requires select_seed_menu() be"
                    " in the mod's options, and should be invoked once the"
                    " mod has been enabled."
                )

            seed_string = menu._seedsystem_dropdown.value
            if not seed_string:
                return

            try:
                seed = cls(seed_string)
            except Exception as error:
                print(
                    f"Could not enable last used seed '{seed_string}':"
                    f"\n{error}"
                )
                return

        if cls.current_seed:
            if seed == cls.current_seed:
                return

            cls.current_seed.disable()
            cls.current_seed = None

        seed.enable()
        cls.current_seed = seed

    @classmethod
    def disable_seed(cls) -> None:
        """
        Disable the currently enabled seed in `current_seed`, if any.
        """
        if cls.current_seed:
            cls.current_seed.disable()
            cls.current_seed = None

    string: str
    """
    The string representation of this seed, as the user sees it.
    """
    data: bytes
    """
    The culmulated data that represents this seed, including the 'random'
    segment, version, and options. This may be used for setting the state of
    randomness algorithms, such as with `random.Random()`
    """
    seed_format: SeedFormat
    """
    The seed format that describes the version of this seed.
    """
    options: dict[ValueSeedOption[Any], Any]
    """
    The option/value pairs for this seed.
    """

    def enable(self) -> None:
        """
        Override to provide behavior when a seed instance is enabled.
        """
        pass

    def disable(self) -> None:
        """
        Override to provide behavior when a seed instance is disabled.
        """
        pass

    @overload
    def __init__(self, string: str) -> None: ...

    """
    Attempt to decode a seed's string representation into a seed instance,
    complete with its seed format, encoded options, and data encompassing its
    randomness.

    Seeds should generally not need to be instantiated manually in this way, as
    the seed system handles seed management and selection, however this method
    is available if you would like to provide custom behavior.

    Args:
        string:
            The string representation to decode.
    """

    @overload
    def __init__(
        self,
        *,
        version: SeedFormat | int | None = None,
        random: int | None = None,
        options: dict[ValueSeedOption[Any], Any] = dict(),
    ) -> None: ...

    """
    Generate a seed of the given format, option values, and optionally a
    predetermined 'random' value.

    Seeds should generally not need to be generated manually in this way, as
    the seed system handles seed generation, however this method is available
    if you would like to provide custom behavior.

    Args:
        version:
            Optionally, the specific seed format object (or integer for a
            representing a seed format object's version) for this seed. If not
            specified, the `default_version` will be used.
        random:
            Optionally, the 'random' segment for the seed. If provided, its
            value will be truncated to fit in the seed format, as per the
            format's `random_width` property.
        options:
            Optionally, the option/value pairs for the new seed. Any options
            in the seed format are filled in with their default values if not
            provided. Any options provided that are not present in the seed
            format are ignored.

    """

    def __init__(
        self,
        string: str | None = None,
        *,
        version: SeedFormat | int | None = None,
        random: int | None = None,
        options: dict[ValueSeedOption[Any], Any] = dict(),
    ) -> None:
        """
        Create a seed instance, complete with its seed format, encoded options,
        and raw data encompassing its randomness.

        Seeds should generally not need to be instantiated manually, as the
        seed system handles seed generation and importing, however this method
        is available if you would like to provide custom behavior.

        Args:
            string:
                A string representation of a seed that the instance should
                attempt to be decoded from. If this is specified, the remaining
                arguments are ignored. If not specified, a new seed will be
                generated based on the remaining arguments.
            version:
                The specific seed format object (or integer representing a seed
                format object's version) for this seed. If not specified when
                generating a new seed, the seed system's `default_version`
                will be used.
            random:
                The 'random' segment for the seed. If provided when generating
                a seed, its value will be truncated to fit in the seed format,
                as per the format's `random_width` property. If not specified,
                a random number will be used instead.
            options:
                The option/value pairs for the new seed. Any options in the
                seed format are filled in with their default values if not
                provided. `ValueError` is raised for Any options provided that
                are not present in the seed format.
        """
        self.options = dict()

        if string is not None:
            b32 = "".join(char.upper() for char in string if char.isalnum())
            if len(b32) % 8:
                b32 += "=" * (8 - len(b32) % 8)

            self.data = b32decode(b32)
            bits = int.from_bytes(self.data, "big")

            version = bits & (2**VERSION_WIDTH - 1)
            bits >>= VERSION_WIDTH

            self.seed_format = type(self).seed_format_for_version(version)
            for option in reversed(self.seed_format.value_seed_options):
                value_bits = bits & (2**option.width - 1)
                self.options[option] = option.bits_to_value(value_bits)
                bits >>= option.width

        else:
            self.seed_format = type(self).seed_format_for_version(version)

            if random is None:
                bits = getrandbits(self.seed_format.random_width)
            else:
                bits = random & (self.seed_format.random_width**2 - 1)

            for option in self.seed_format.value_seed_options:
                value = options.get(option, option.default_value)
                self.options[option] = value
                bits = (bits << option.width) | option.value_to_bits(value)

            invalid = options.keys() - self.options.keys()
            if len(invalid):
                raise ValueError(
                    f"{self.seed_format} does not support options {invalid}"
                )

            bits = (bits << VERSION_WIDTH) | self.seed_format.version

            self.data = bits.to_bytes(self.seed_format.byte_count, "big")

        b32 = b32encode(self.data).decode("ascii").strip("=")
        b32_index = 0

        self.string = ""
        for char in self.seed_format.format_string:
            if char in DIGIT_PLACEHOLDERS:
                self.string += b32[b32_index].lower()
                b32_index += 1
            else:
                self.string += char

    def __hash__(self) -> int:
        return hash(self.data)

    def __eq__(self, value: object) -> bool:
        return type(value) == type(self) and self.data == value.data

    def __getitem__[T: mods_base.JSON](self, option: ValueSeedOption[T]) -> T:
        try:
            return self.options[option]
        except KeyError:
            raise KeyError(
                f"Version {self.seed_format} seed '{self.string}'"
                f" does not contain option {option}"
            )

    @overload
    def get[T: mods_base.JSON](
        self, option: ValueSeedOption[T]
    ) -> T | None: ...

    @overload
    def get[T: mods_base.JSON, D](
        self, option: ValueSeedOption[T], default: D
    ) -> T | D: ...

    def get(self, option: ValueSeedOption[Any], default: Any = None) -> Any:
        return self.options.get(option, default)

    def __repr__(self) -> str:
        return f'{type(self).__name__}("{self.string}")'

    def __str__(self) -> str:
        return self.string
