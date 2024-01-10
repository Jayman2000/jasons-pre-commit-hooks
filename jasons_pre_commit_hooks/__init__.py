# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import re
import io
import sys
import warnings

from typing import Final


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
