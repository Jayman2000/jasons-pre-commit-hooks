# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import re
import sys
from typing import Final

from . import init


def main() -> int:
    init()
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
