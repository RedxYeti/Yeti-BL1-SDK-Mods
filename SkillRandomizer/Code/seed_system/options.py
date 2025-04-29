from __future__ import annotations

import math

import mods_base

from typing import Sequence


class BaseSeedOption(mods_base.BaseOption):
    pass


class ValueSeedOption[J: mods_base.JSON](
    BaseSeedOption,
    mods_base.ValueOption[J]
):
    width: int
    """
    How many bits of data the seed option requires, calculated based on its
    possible values.
    """

    def value_to_bits(self, value: J) -> int:
        """
        Override to define how to convert values for the seed option into bits
        to be stored in seeds.
        """
        raise NotImplementedError

    def bits_to_value(self, bits: int) -> J:
        """
        Override to define how to convert the seed option's bits in seeds back
        into their original values.
        """
        raise NotImplementedError


    def __hash__(self) -> int:
        return id(self)

    def __eq__(self, value: object) -> bool:
        return self is value


class BoolSeedOption(ValueSeedOption[bool], mods_base.BoolOption):
    width = 1

    def value_to_bits(self, value: bool) -> int:
        return int(value)

    def bits_to_value(self, bits: int) -> bool:
        return bits != 0


class SliderSeedOption(ValueSeedOption[float], mods_base.SliderOption):
    _range: range

    def __post_init__(self) -> None:
        if not self.is_integer:
            raise ValueError(f"SliderSeedOption only supports is_integer=True")

        if self.min_value % self.step or self.max_value % self.step:
            raise ValueError(
                f"SliderSeedOption min_value and max_value must be multiples"
                " of step"
            )

        self._range = range(
            int(self.min_value),
            int(self.max_value) + 1,
            int(self.step)
        )

        self.width = int(math.ceil(math.log2(len(self._range))))

        super().__post_init__()

    def value_to_bits(self, value: float) -> int:
        return self._range.index(int(value))

    def bits_to_value(self, bits: int) -> int:
        return self._range[bits]


class SpinnerSeedOption(ValueSeedOption[str], mods_base.SpinnerOption):
    def __post_init__(self) -> None:
        self.width = int(math.ceil(math.log2(len(self.choices))))
        super().__post_init__()

    def value_to_bits(self, value: str) -> int:
        return self.choices.index(value)

    def bits_to_value(self, bits: int) -> str:
        return self.choices[bits]


class DropdownSeedOption(ValueSeedOption[str], mods_base.DropdownOption):
    def __post_init__(self) -> None:
        self.width = int(math.ceil(math.log2(len(self.choices))))
        super().__post_init__()

    def value_to_bits(self, value: str) -> int:
        return self.choices.index(value)

    def bits_to_value(self, bits: int) -> str:
        return self.choices[bits]


class GroupedSeedOption(BaseSeedOption, mods_base.GroupedOption):
    children: Sequence[BaseSeedOption]  # pyright: ignore[reportIncompatibleVariableOverride]


class NestedSeedOption(BaseSeedOption, mods_base.NestedOption):
    children: Sequence[BaseSeedOption]  # pyright: ignore[reportIncompatibleVariableOverride]
