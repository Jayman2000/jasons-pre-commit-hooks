# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import collections.abc
import datetime
import json
import pathlib
import subprocess
import sys
from typing import Final

from . import init, paths_in_repo


exit_status: int
# See <man:sysexits.h(3head)>.
EX_DATAERR: Final = 65


yield_type = collections.abc.Iterable[datetime.datetime]
def all_last_modified_values(
    lock_file_path: pathlib.Path,
    json_value: dict[object, object]
) -> yield_type:
    global exit_status
    for key, value in json_value.items():
        if isinstance(value, dict):
            generator: yield_type = all_last_modified_values(
                    lock_file_path,
                    value
            )
            for last_modified_value in generator:
                yield last_modified_value
        elif key == "lastModified":
            if isinstance(value, int):
                yield datetime.datetime.fromtimestamp(
                    value,
                    tz=datetime.timezone.utc
                )
            else:
                error_message: str = (
                    f'ERROR: {lock_file_path} contains an invalid'
                    f' "lastModified" value: {repr(value)}'
                )
                print(error_message, file=sys.stderr)
                exit_status = EX_DATAERR


def try_to_update_lock_file(lock_file_path: pathlib.Path) -> None:
    print(f"Attempting to update “{lock_file_path}”…")
    COMMAND: Final[tuple[str, ...]] = (
        "nix",
        "--extra-experimental-features",
        "nix-command flakes",
        "flake",
        "update"
    )
    subprocess.run(COMMAND, check=True, cwd=lock_file_path.parent)
    print(f"Successfully updated “{lock_file_path}”.")


def all_flake_lock_files() -> collections.abc.Iterable[pathlib.Path]:
    path: pathlib.Path
    for path in paths_in_repo():
        if path.name == "flake.lock":
            yield path


def main() -> int:
    init()
    global exit_status
    exit_status = 0

    PARSER: Final = argparse.ArgumentParser(
        description=(
            "Updates a flake.lock file if it hasn’t been updated in "
            "over a week."
        )
    )
    PARSER.add_argument(
        "paths",
        nargs="*",
        type=pathlib.Path,
        help=(
            "The path to a flake.lock file. If no paths are specified "
            "on the command-line, then flake-lock-updater will assume "
            "that the current working directory is somewhere inside a "
            "Git repository. It will then scan that Git repository for "
            "files named flake.lock."
        ),
        metavar="PATH"
    )
    ARGS: Final = PARSER.parse_args()

    LOCK_FILE_PATHS: Final[collections.abc.Iterable[pathlib.Path]] = (
        ARGS.paths if len(ARGS.paths) > 0 else all_flake_lock_files()
    )
    for lock_file_path in LOCK_FILE_PATHS:
        # Lock files are guaranteed to be UTF-8 JSON files [1].
        #
        # editorconfig-checker-disable
        # [1]: <https://hydra.nixos.org/build/273946807/download/1/manual/command-ref/new-cli/nix3-flake.html#lock-files>
        # editorconfig-checker-enable
        with lock_file_path.open(encoding="utf-8") as lock_file:
            lock_file_data: object = json.load(lock_file)

        if isinstance(lock_file_data, dict):
            latest_last_modified_value: datetime.datetime = max(
                all_last_modified_values(lock_file_path, lock_file_data)
            )
            smallest_input_age = (
                datetime.datetime.now(datetime.timezone.utc)
                - latest_last_modified_value
            )
            if smallest_input_age.days > 7:
                try_to_update_lock_file(lock_file_path)
                break
            else:
                print(f"“{lock_file_path}” doesn’t need to be updated.")
        else:
            error_message: str = (
                f"ERROR: “{lock_file_path}” does not appear to be a "
                "valid flake.lock file."
            )
            print(error_message, file=sys.stderr)
            exit_status = EX_DATAERR

    return exit_status
