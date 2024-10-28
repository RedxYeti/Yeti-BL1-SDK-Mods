from pathlib import Path
from mods_base import SETTINGS_DIR
from mods_base import build_mod
from unrealsdk import logging

from .hooks import BloodwingCalled

# Gets populated from `build_mod` below
__version__: str
__version_info__: tuple[int, ...]

build_mod(
    # These are defaulted
    # inject_version_from_pyproject=True, # This is True by default
    # version_info_parser=lambda v: tuple(int(x) for x in v.split(".")),
    # deregister_same_settings=True,      # This is True by default
    keybinds=[],
    hooks=[BloodwingCalled],
    commands=[],
    # Defaults to f"{SETTINGS_DIR}/dir_name.json" i.e., ./Settings/bl1_commander.json
    settings_file=Path(f"{SETTINGS_DIR}/BloodwingReturnFix.json"),
)

logging.info(f"Bloodwing Return Fix: {__version__}, {__version_info__}")
