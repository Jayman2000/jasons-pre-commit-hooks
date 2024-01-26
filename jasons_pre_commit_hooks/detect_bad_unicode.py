# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import pathlib
import sys
import unicodedata
from typing import Final, Iterable

import wcwidth

from . import init


def line_and_maybe_column_number(
    line: str,
    line_index: int,
    character_index: int
) -> str:
    return_value: str = f"line {line_index + 1:n}"
    # When calculating the width, we purposely don’t include the
    # character that we’re trying to find the position of. For whatever
    # reason, U+34544 has East_Asian_Width set to “Wide” even though
    # U+34544 isn’t assigned to any character [1]. In situations like
    # that, it makes sense for the column number to point to the start
    # of the character. Purposefully not including the character that
    # we’re looking for while doing the width calculation allows us to
    # point to the beginning of the character in that situation.
    #
    # [1]: <https://util.unicode.org/UnicodeJsps/character.jsp?a=34544>
    width: int = wcwidth.wcswidth(line[:character_index])
    if width >= 0:
        return_value += f" column {width + 1:n}"

    return return_value


def main() -> int:
    init()
    PARSER: Final = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Checks to see if UTF-8 files contain “bad” code points.\n"
            "\n"
            "For the purposes of this command, a “bad” code point is a "
            "surrogate code point, a private-use code point, a "
            "noncharacter code point or a reserved code point. See "
            "the Unicode Standard for details: <https://"
            "www.unicode.org/versions/Unicode15.0.0/ch02.pdf#G14527>."
        )
    )
    PARSER.add_argument(
        'paths',
        nargs='+',
        type=pathlib.Path,
        metavar="FILE"
    )
    ARGS: Final = PARSER.parse_args()

    any_errors: bool = False
    path: pathlib.Path
    for path in ARGS.paths:
        text: str = path.read_text(
            encoding='utf_8',
            errors='surrogatepass'
        )

        line_index: int
        line: str
        lines: Iterable[str] = text.splitlines(keepends=True)
        for line_index, line in enumerate(lines):
            character_index: int
            character: str
            for character_index, character in enumerate(line):
                category: str = unicodedata.category(character)
                if category in ('Cs', 'Co', 'Cn'):
                    any_errors = True
                    position: str = line_and_maybe_column_number(
                        line,
                        line_index,
                        character_index
                    )
                    print(
                        f"ERROR: {path}: {position}:",
                        f"U+{ord(character):04X} is in a bad",
                        f"Unicode general category: {category}",
                        file=sys.stderr
                    )
    return any_errors
