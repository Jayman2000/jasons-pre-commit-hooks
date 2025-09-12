# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import collections.abc
import contextlib
import io
import locale
import os
import pathlib
import re
import sys
import warnings
from typing import Final

import dulwich.repo


# editorconfig-checker-disable
def init() -> None:
    """
    Perform initialization common to all commands.

    Every function that gets used as a console script [1] should start
    by calling this function.

    [1]: <https://setuptools.pypa.io/en/stable/userguide/entry_point.html#console-scripts>
    """
    # editorconfig-checker-enable
    locale.setlocale(locale.LC_ALL, '')
    make_stdout_stderr_handle_errors_better()


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


def open_cwd_as_repo() -> contextlib.closing[dulwich.repo.Repo]:
    CWD: Final = str(pathlib.Path.cwd())
    return contextlib.closing(dulwich.repo.Repo(CWD))


def paths_in_repo(
    ignore_patterns: collections.abc.Iterable[re.Pattern[str]] = ()
) -> collections.abc.Iterable[pathlib.Path]:
    # I would have used dulwich.porcelain.ls_files(), but that function
    # isn’t typed.
    repo: dulwich.repo.Repo
    with open_cwd_as_repo() as repo:
        for byte_path in repo.open_index():
            path = pathlib.Path(os.fsdecode(byte_path))
            path_string = str(path)
            for ignore_pattern in ignore_patterns:
                if ignore_pattern.fullmatch(path_string):
                    break
            else:
                yield pathlib.Path(os.fsdecode(byte_path))
