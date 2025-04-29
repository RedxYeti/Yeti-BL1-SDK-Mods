import math

from .options import (
    BaseSeedOption,
    ValueSeedOption,
    GroupedSeedOption,
    NestedSeedOption
)

from typing import Any, Generator, Sequence


VERSION_WIDTH = 5
VERSION_MAX = 2**VERSION_WIDTH - 1
BYTE_WIDTH = 8
DIGIT_WIDTH = 5
DIGIT_MODULO_BLACKLIST = (1, 3, 6)
DIGIT_PLACEHOLDERS = 'Xx'


class SeedFormatError(Exception):
    pass


def _flatten_seed_options(
    seed_options: Sequence[BaseSeedOption]
) -> Generator[ValueSeedOption[Any], None, None]:
    for child in seed_options:
        match child:
            case ValueSeedOption():
                yield child
            case GroupedSeedOption() | NestedSeedOption():
                yield from _flatten_seed_options(child.children)
            case _:
                pass


class SeedFormat:
    """
    Seed format objects define the appearance and functionality of seeds. They
    dictate what seeds will look like when users create, manage, and share
    them, as well as what information is encoded into and decoded from seeds
    during generation and loading.

    Args:
        version:
            The version number this seed format represents. This is encoded
            into seed strings, and is ultimately used to match users' seed
            strings back to this this seed format.

        format_string:
            The final appearance of seeds of this format, as the user will see
            them.
            
            When specifying the format string, instances of the character 'X'
            are used to designate where the actual data representing each seed
            should be inserted. Any non-alphanumeric character can be used for
            decoration. 
            
            For example, the format string 'XXXXX-XXXXX-XXXXX` will result in
            seeds with the appearance 'qadle-ta377-777ry'.

            The number of 'X' characters in the format string determines how
            many bits of data it can represent. Available bits are consumed by
            the 5 bit version number, followed by the seed format's options,
            and then any remaining are dedicated to randomness.
            
            Thus, when designing a format string, a sufficent quantity of X's
            are required to reach your desired level of randomess. To assist in
            this while designing a format, you may check the SeedFormat's
            `variant_count`.

            Finally, as per the base32 specification, 'X' quantities whose
            modulos of 8 equal 1, 3, or 6 cannot be used. for these,
            SeedFormatError is raised, containing a suggestion of an alternate
            quantity.

        seed_options:
            The options that can be represented by the seed format.

            These options will also determine how the options are presented to
            the user in the seed generation menu. You may include any
            `BaseSeedOption` in this sequence, including `GroupedSeedOption`
            and `NestedSeedOption`, however these will only appear in the
            seed generation menu.
    """
    version: int
    format_string: str
    seed_options: Sequence[BaseSeedOption]

    value_seed_options: Sequence[ValueSeedOption[Any]]
    """
    The ValueSeedOption's that are encoded into seeds of this format.
    """

    byte_count: int
    """
    The quantity of bytes represented in each seed of this seed format,
    determined by the 'X' count in its `format_string`.
    """
    random_width: int
    """
    The number of bits this seed format dedicates to randomness. This is
    determined by the remaining space in its `byte_count` after its version
    number and options' required storage.
    """
    @property
    def variant_count(self) -> int:
        """
        The number of different seeds this version can generate. Equal to
        2 ** `random_width`.

        The variant count is determined by the available bits remaining in the
        seed format, after the necessary amount consumed by the seed version's
        options. Thus, increasing the number of X's in the `format_string`
        increases the number of possible seeds.
        """
        return 2**self.random_width


    def __init__(
        self,
        version: int,
        format_string: str,
        seed_options: Sequence[BaseSeedOption],
    ) -> None:
        if version > VERSION_MAX:
            raise SeedFormatError(
                f"Seed Formats cannot exceed version {VERSION_MAX}."
            )

        self.version = version
        self.format_string = format_string
        self.seed_options = seed_options
        self.value_seed_options = tuple(_flatten_seed_options(seed_options))

        min_width = VERSION_WIDTH + sum(
            option.width for option in self.value_seed_options
        )
        min_bytes = int(math.ceil(min_width / BYTE_WIDTH))
        min_digits = int(math.ceil(min_bytes * BYTE_WIDTH / DIGIT_WIDTH))

        digits = 0
        invalid = ''
        for char in format_string:
            if char in DIGIT_PLACEHOLDERS:
                digits += 1
            elif char.isalnum() and not char in invalid:
                invalid += char

        if invalid != '':
            raise SeedFormatError(
                f"Invalid characters '{invalid}' in seed format '{format_string}'"
            )

        if digits < min_digits:
            if min_digits % 8 in DIGIT_MODULO_BLACKLIST:
                min_digits += 1
            raise SeedFormatError(
                f"An 'X' quantity of {digits} is insufficent to store the"
                f" specified options, at least {min_digits} are required."
            )

        if (digits % 8) in DIGIT_MODULO_BLACKLIST:
            raise SeedFormatError(
                f"An 'X' quantity of {digits} cannot be used,"
                f" use {digits - 1} or {digits + 1} instead"
            )

        self.byte_count = int(math.floor(digits * DIGIT_WIDTH / BYTE_WIDTH))
        self.random_width = self.byte_count * BYTE_WIDTH - min_width


    def __repr__(self) -> str:
        return f'{type(self).__name__}({self.version}, {self.format_string})'