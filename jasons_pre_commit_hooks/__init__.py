# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import contextlib
import io
import os
import pathlib
import re
import sys
import textwrap
import warnings

from collections.abc import Iterable
from typing import Final, Optional

import dulwich.repo


# REUSE-IgnoreStart
COPYING_TEMPLATE: Final = \
"""<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2023–2024 Jason Yundt <jason@jasonyundt.email>
REUSE-IgnoreStart
-->

# Copying Information for {}

This repo complies with [this specific version of the REUSE
Specification][1].

Please note that some items on [the SPDX License List][2] aren’t
necessarily licenses. For example, [`GPL-2.0-only` can act as a
contract][3] and [`CCO-1.0` is a public domain dedication][4]. If a file
contains `SPDX-License-Identifier: CC0-1.0` that doesn’t necessarily
mean that the file is licensed in anyway. You’ll need to look at
`CC0-1.0` to figure out the legal status of that file. Additionally, if
that file contains an `SPDX-FileCopyrightText` tag, that doesn’t
necessarily mean that the file is copyrighted. Again, you’ll need to
look at `CC0-1.0` for details.

All of this repo’s Git metadata (commit messages, annotated tags, hashes
etc.) is dedicated to the public domain using [🅭🄍1.0][5].

<!-- editorconfig-checker-disable -->

[1]: https://github.com/fsfe/reuse-docs/blob/0913b0a83b36c161966be1c5e70c81bdadfb8a69/spec.md
[2]: https://spdx.org/licenses/
[3]: https://sfconservancy.org/news/2022/may/16/vizio-remand-win/
[4]: https://wiki.spdx.org/view/Legal_Team/Decisions/Dealing_with_Public_Domain_within_SPDX_Files
[5]: https://creativecommons.org/publicdomain/zero/1.0/

<!--
editorconfig-checker-enable
REUSE-IgnoreEnd
-->
"""
# REUSE-IgnoreEnd
COPYING_LINK: Final = \
"""## Copying

See [`copying.md`](./copying.md).
"""


# editorconfig-checker-disable
def make_stdout_stderr_handle_errors_better() -> None:
    """
    Make this program work better on non-Unicode locales.

    By default, stdout uses the 'strict' error handler, and stderr uses
    the 'backslashescape' error handler [1][2].

    [1]: <https://docs.python.org/3.12/library/sys.html#sys.stdout>
    [2]: <https://docs.python.org/3.12/c-api/init_config.html#c.PyConfig.stdio_errors>
    """
    # editorconfig-checker-enable
    for name in ('stdout', 'stderr'):
        file = getattr(sys, name)
        if isinstance(file, io.TextIOWrapper):
            file.reconfigure(errors='namereplace')
        else:
            warnings.warn(
                f"sys.{name} was replaced, so we can’t override its "
                "error handler."
            )


def forbid_paths() -> int:
    make_stdout_stderr_handle_errors_better()
    PARSER: Final = argparse.ArgumentParser(
        description=(
            "Causes an error if paths match certain regex patterns."
        ),
    )
    PARSER.add_argument(
        '-p',
        '--pattern',
        action='extend',
        nargs=1,
        type=re.compile,
        required=True,
        help=(
            "A regular expression. Uses the same syntax that Python’s"
            "re module uses. See <https://docs.python.org/3/library/"
            "re.html#regular-expression-syntax> for details."
        ),
        metavar="PATTERN",
        dest='patterns',
    )
    PARSER.add_argument(
        'paths',
        nargs='+',
        metavar="PATH"
    )
    ARGS: Final = PARSER.parse_args()

    exit_status: int = 0
    for path in ARGS.paths:
        for pattern in ARGS.patterns:
            if pattern.match(path) is not None:
                print(
                    f"ERROR: Path “{path}” matches this pattern:",
                    pattern.pattern,
                    file=sys.stderr
                )
                exit_status = 1
    return exit_status


def paths_in_repo() -> Iterable[pathlib.Path]:
    # I would have used dulwich.porcelain.ls_files(), but that function
    # isn’t typed.
    ROOT: Final = str(pathlib.Path.cwd())
    with contextlib.closing(dulwich.repo.Repo(ROOT)) as repo:
        for byte_path in repo.open_index():
            yield pathlib.Path(os.fsdecode(byte_path))


def print_no_file_error(path: pathlib.Path) -> None:
    print(f"ERROR: There’s no {path} file.", file=sys.stderr)


def extract_str_from_line_that_starts_with(
    text: str,
    to_look_for: str
) -> Optional[str]:
    for line in text.splitlines():
        if line.startswith(to_look_for):
            extraction_start_point: int = len(to_look_for)
            return line[extraction_start_point:]
    return None


def repo_style_checker() -> int:
    make_stdout_stderr_handle_errors_better()
    PARSER: Final = argparse.ArgumentParser(
        description=(
            "Makes sure that repos follow Jason’s style for repos."
        )
    )
    # This command doesn’t take any arguments, so this just makes sure
    # that --help works and that errors are produced if arguments are
    # given.
    PARSER.parse_args()

    # Does copying.md exist?
    PATHS: Final = set(path for path in paths_in_repo())
    COPYING_PATH: Final = pathlib.Path('copying.md')
    if COPYING_PATH not in PATHS:
        print_no_file_error(COPYING_PATH)
        return 1
    # Can we determine the project’s name by looking at copying.md?
    TO_LOOK_FOR: Final = "# Copying Information for "
    COPYING_CONTENTS: Final = COPYING_PATH.read_text(encoding='utf_8')
    PROJECT_NAME: Final = extract_str_from_line_that_starts_with(
        COPYING_CONTENTS,
        TO_LOOK_FOR
    )
    if PROJECT_NAME is None:
        print(
            "ERROR: Couldn’t automatically detect the project’s name",
            f"by looking at {COPYING_PATH}. In order for",
            f"autodetection to work, {COPYING_PATH} should contain a",
            "line that looks like",
            f"this:\n\n\t{TO_LOOK_FOR}<project-name>\n",
            file=sys.stderr
        )
        return 1
    # Does copying.md contain the correct text?
    EXPECTED_COPYING_INFO: Final = COPYING_TEMPLATE.format(PROJECT_NAME)
    if EXPECTED_COPYING_INFO.format(PROJECT_NAME) != COPYING_CONTENTS:
        print(
            f"ERROR: {COPYING_PATH} doesn’t match the standard copying",
            "info template. Fixing…",
            file=sys.stderr
        )
        COPYING_PATH.write_text(EXPECTED_COPYING_INFO, encoding='utf_8')
        return 1
    # Does README.md exist?
    README_PATH: Final = pathlib.Path('README.md')
    if README_PATH not in PATHS:
        print_no_file_error(README_PATH)
        return 1
    # Does README.md contain an <h1>?
    H1_MARKER: Final = "# "
    README_CONTENTS: Final = README_PATH.read_text(encoding='utf_8')
    README_H1_CONTENTS: Final = extract_str_from_line_that_starts_with(
        README_CONTENTS,
        H1_MARKER
    )
    README_H1_ERROR: Final = (
        "Make sure that there’s a line that looks like"
        f"this:\n\n\t{H1_MARKER}{PROJECT_NAME}\n"
    )
    if README_H1_CONTENTS is None:
        print(
            f"ERROR: There’s no <h1> in {README_PATH}.",
            README_H1_ERROR,
            file=sys.stderr
        )
        return 1
    # Does the <h1> match the project’s name?
    if README_H1_CONTENTS != PROJECT_NAME:
        print(
            f"ERROR: The project’s name in {README_PATH} does not",
            f"match its name in {COPYING_PATH}.",
            README_H1_ERROR,
            file=sys.stderr
        )
        return 1
    # Does the README link to copying.md?
    if COPYING_LINK not in README_CONTENTS:
        COPYING_LINK_INDENTED: Final = textwrap.indent(
            COPYING_LINK,
            "\t"
        )
        print(
            f"ERROR: {README_PATH} is missing a link to",
            f"{COPYING_PATH}. Make sure that {README_PATH} contains",
            f"the following:\n\n{COPYING_LINK_INDENTED}",
            file=sys.stderr
        )
        return 1
    # Is pre-commit set up?
    PC_CONFIG_PATH: Final = pathlib.Path(".pre-commit-config.yaml")
    if PC_CONFIG_PATH not in PATHS:
        print_no_file_error(PC_CONFIG_PATH)
        return 1
    return 0
