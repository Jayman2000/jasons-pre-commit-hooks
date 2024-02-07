# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import os
import importlib.resources
import pathlib
import sys
import textwrap
from collections.abc import Iterable
from typing import Any, Final, NamedTuple, Optional

import dulwich.repo
import yaml

from . import init, open_cwd_as_repo


COPYING_PATH: Final = importlib.resources.files().joinpath("copying.md")
COPYING_TEMPLATE: Final = (
    COPYING_PATH
    .read_text(encoding='utf_8')
    .replace("Jason’s Pre-commit Hooks", "{}")
)
COPYING_LINK: Final = \
"""## Copying

See [`copying.md`](./copying.md).
"""


PYTHON_GLOBS: Final = ('**.py', '**.pyi')
YAML_GLOBS: Final = ('**.yml', '**.yaml')


HINTS_FOR_CONTRIBUTORS_HEADING: Final = "## Hints for Contributors\n"
HFC_LINE_LENGTH: Final = \
    "- Try to keep lines shorter than seventy-three characters."
HFC_PRE_COMMIT: Final = \
"""
- You can use [pre-commit][1] to automatically check your contributions.
Follow [these instructions][2] to get started. Skip [the part about
creating a pre-commit configuration][3].
"""
HFC_PRE_COMMIT_LINKS: Final = \
"""
[1]: https://pre-commit.com
[2]: https://pre-commit.com/#quick-start
[3]: https://pre-commit.com/#2-add-a-pre-commit-configuration
"""
HFC_EDITOR_CONFIG: Final = \
    "- This repo uses an [EditorConfig](https://editorconfig.org) file."
HFC_MARKDOWN: Final = \
"""
- Use [CommonMark](https://commonmark.org) for
[Markdown](https://daringfireball.net/projects/markdown) files.
"""
HFC_RUFF: Final = \
"""
- If you’re using [NixOS](https://nixos.org), then the
[ruff](https://docs.astral.sh/ruff/) pre-commit hook probably won’t
work. Here’s how you fix it:

    1. Set the `PIP_NO_BINARY` environment variable to “ruff”.
    2. Run `pre-commit clean`
    3. Run `pre-commit install-hooks`
"""
HINTS_FOR_CONTRIBUTORS_BY_PATH: Final = (
    (('**',), HFC_LINE_LENGTH),
    (('.pre-commit-config.yaml',), HFC_PRE_COMMIT),
    (('.pre-commit-config.yaml',), HFC_PRE_COMMIT_LINKS),
    (('.editorconfig',), HFC_EDITOR_CONFIG),
    (('**.md',), HFC_MARKDOWN),
    (PYTHON_GLOBS, HFC_RUFF)
)


EXPECTED_EDITOR_CONFIG: Final = (
    importlib.resources.files()
    .joinpath("editor_config.ini")
    .read_text(encoding='utf_8')
)


# Pre-commit hooks shouldn’t mess with the files in the LICENSES/
# directory. See 4f1e797 (Don’t run most pre-commit hooks on LICENSES/,
# 2023-12-25) for details.
PRE_COMMIT_STANDARD_EXCLUDE: Final = '^LICENSES/'
class PreCommitRepoInfo(NamedTuple):
    url: str
    hook_ids: Iterable[str]
    exclude: Optional[str] = PRE_COMMIT_STANDARD_EXCLUDE
    args: Optional[Iterable[str]] = None
PCR_REUSE: Final = PreCommitRepoInfo(
    url='https://github.com/fsfe/reuse-tool',
    hook_ids=('reuse',),
    exclude=None,
    args=None
)
PCR_PRE_COMMIT_UPDATE: Final = PreCommitRepoInfo(
    url='https://gitlab.com/vojko.pribudic/pre-commit-update',
    hook_ids=('pre-commit-update',)
)
PCR_EDITORCONFIG_CHECKER: Final = PreCommitRepoInfo(
    # editorconfig-checker-disable
    url='https://github.com/editorconfig-checker/editorconfig-checker.python',
    # editorconfig-checker-enable
    hook_ids=('editorconfig-checker',),
    args=('-ignore-defaults',)
)
PCR_OFFICIAL_HOOKS: Final = PreCommitRepoInfo(
    url='https://github.com/pre-commit/pre-commit-hooks',
    hook_ids=(
        'check-case-conflict',
        'check-merge-conflict',
        'check-symlinks',
        'check-vcs-permalinks',
        'destroyed-symlinks'
    )
)
PCR_OFFICIAL_HOOKS_PYTHON: Final = PreCommitRepoInfo(
    url='https://github.com/pre-commit/pre-commit-hooks',
    hook_ids=(
        'debug-statements',
        'fix-encoding-pragma'
    )
)
PCR_PYGREP_HOOKS: Final = PreCommitRepoInfo(
    url='https://github.com/pre-commit/pygrep-hooks',
    hook_ids=('text-unicode-replacement-char',)
)
PCR_GITLEAKS: Final = PreCommitRepoInfo(
    url='https://github.com/zricethezav/gitleaks',
    hook_ids=('gitleaks',)
)
PCR_JASONS_PRE_COMMIT_HOOKS: Final = PreCommitRepoInfo(
    url='https://github.com/Jayman2000/jasons-pre-commit-hooks',
    hook_ids=('detect-bad-unicode',)
)
# I’m only enabling this hook to work around this problem:
# <https://github.com/fsfe/reuse-tool/issues/881>.
PCR_FORBID_PATHS_THAT_MATCH: Final = PreCommitRepoInfo(
    url='https://github.com/Jayman2000/jasons-pre-commit-hooks',
    hook_ids=('forbid-paths-that-match',),
    args=('--pattern', '^LICENSE', '--pattern', '^COPYING')
)
PCR_LANGUAGE_FORMATTERS: Final = PreCommitRepoInfo(
    # editorconfig-checker-disable
    url='https://github.com/macisamuele/language-formatters-pre-commit-hooks',
    # editorconfig-checker-enable
    hook_ids=('pretty-format-toml',),
    args=('--autofix', '--indent', '4')
)
# This is the version of yamllint from this PR:
# <https://github.com/adrienverge/yamllint/pull/630>.
#
# Normally, I would just use a stable release of yamllint, but
# stable releases are likely to not work properly on Windows,
# and being platform neutral is very important to me.
PCR_YAMLLINT: Final = PreCommitRepoInfo(
    url='https://github.com/Jayman2000/yamllint-pr',
    hook_ids=('yamllint',)
)
PCR_MARKDOWNLINT_CLI: Final = PreCommitRepoInfo(
    url='https://github.com/igorshubovych/markdownlint-cli',
    hook_ids=('markdownlint',)
)
PCR_MYPY: Final = PreCommitRepoInfo(
    url='https://github.com/pre-commit/mirrors-mypy',
    hook_ids=('mypy',),
    args=('--strict',)
)
PCR_RUFF: Final = PreCommitRepoInfo(
    url='https://github.com/astral-sh/ruff-pre-commit',
    hook_ids=('ruff',)
)
PCR_PRE_COMMIT_ITSELF: Final = PreCommitRepoInfo(
    url='https://github.com/pre-commit/pre-commit',
    hook_ids=('validate_manifest',)
)
PRE_COMMIT_REPOS_BY_PATH: Final = (
    (('**',), PCR_REUSE),
    (('.pre-commit-hooks.yaml',), PCR_PRE_COMMIT_UPDATE),
    (('.editorconfig',), PCR_EDITORCONFIG_CHECKER),
    (('**',), PCR_OFFICIAL_HOOKS),
    (PYTHON_GLOBS, PCR_OFFICIAL_HOOKS_PYTHON),
    (('**',), PCR_PYGREP_HOOKS),
    (('**',), PCR_GITLEAKS),
    (('**',), PCR_JASONS_PRE_COMMIT_HOOKS),
    (('**',), PCR_FORBID_PATHS_THAT_MATCH),
    (('**.toml',), PCR_LANGUAGE_FORMATTERS),
    (YAML_GLOBS, PCR_YAMLLINT),
    (('**.md',), PCR_MARKDOWNLINT_CLI),
    (PYTHON_GLOBS, PCR_MYPY),
    (PYTHON_GLOBS, PCR_RUFF),
    (('.pre-commit-hooks.yaml',), PCR_PRE_COMMIT_ITSELF),
)


def paths_in_repo() -> Iterable[pathlib.Path]:
    # I would have used dulwich.porcelain.ls_files(), but that function
    # isn’t typed.
    repo: dulwich.repo.Repo
    with open_cwd_as_repo() as repo:
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


def check_pc_config_hooks(
    pre_commit_config: dict[Any, Any],
    repo_info: PreCommitRepoInfo,
    glob: str
) -> bool:
    ACTUAL_VALUE: Final = "Its actual value was {}"
    REPOS: Final = pre_commit_config.get('repos')
    if not isinstance(REPOS, Iterable):
        print(
            "ERROR: The pre-commit config did not contain a key named",
            "repos, or the repos key’s value wasn’t a list.",
            ACTUAL_VALUE.format(REPOS),
            file=sys.stderr
        )
        return False

    hooks_found: dict[str, bool] = {}
    for hook_id in repo_info.hook_ids:
        hooks_found[hook_id] = False
    excludes_respected: bool = True
    args_respected: bool = True
    no_errors: bool = True
    repo: Any
    for repo in REPOS:
        if not isinstance(repo, dict):
            print(
                "ERROR: One of the items on the pre-commit config’s",
                "repos list was not a YAML mapping.",
                ACTUAL_VALUE.format(repo),
                file=sys.stderr
            )
            no_errors = False
            continue
        url: Any = repo.get('repo')
        if not isinstance(url, str):
            print(
                "ERROR: In the pre-commit config, the URL for one of",
                "the items on the repos list either wasn’t specified",
                "wasn’t a string.",
                ACTUAL_VALUE.format(url),
            )
            no_errors = False
            continue
        if url != repo_info.url:
            continue
        hooks: Any = repo.get('hooks')
        if not isinstance(hooks, Iterable):
            print(
                "ERROR: In the pre-commit config, the hooks list for",
                f"<{url}> either wasn’t specified or wasn’t a string.",
                ACTUAL_VALUE.format(hooks),
                file=sys.stderr
            )
            no_errors = False
            continue
        hook: Any
        for hook in hooks:
            if not isinstance(hook, dict):
                print(
                    "ERROR: In the pre-commit config, one of the hooks",
                    f"for <{url}> was not a YAML mapping.",
                    ACTUAL_VALUE.format(hook),
                    file=sys.stderr
                )
                no_errors = False
                continue
            id: Any = hook.get('id')
            if id not in repo_info.hook_ids:
                # This is a hook that we don’t care about, so we can
                # just ignore it.
                continue
            hooks_found[id] = True
            if repo_info.exclude is not None:
                exclude: Any = hook.get('exclude')
                if not isinstance(exclude, str):
                    print(
                        f"ERROR: In the pre-commit config, <{url}>’s",
                        f"{id} hook either did not specify an exclude",
                        "pattern or specified an exclude pattern that",
                        "wasn’t a string.",
                        ACTUAL_VALUE.format(exclude),
                        file=sys.stderr
                    )
                    no_errors = False
                    continue
                if exclude != repo_info.exclude:
                    print(
                        f"ERROR: In the pre-commit config, <{url}>’s",
                        f"{id} hook didn’t use the right value for its",
                        "exclude pattern. It should have been",
                        f"{repo_info.exclude}.",
                        ACTUAL_VALUE.format(exclude),
                        file=sys.stderr
                    )
                    excludes_respected = False
            if repo_info.args is not None:
                args: Any = hook.get('args')
                if not isinstance(args, Iterable):
                    print(
                        f"ERROR: In the pre-commit config, <{url}>’s",
                        f"{id} hook either did not specify an args",
                        "list or set args to something other than a",
                        "list.",
                        ACTUAL_VALUE.format(args),
                        file=sys.stderr
                    )
                    no_errors = False
                    continue
                args_as_a_tuple: tuple[Any] = tuple(args)
                expected_arg: str
                for expected_arg in repo_info.args:
                    if expected_arg not in args_as_a_tuple:
                        print(
                            "ERROR: In the pre-commit config,",
                            f"<{url}>’s {id} hook did not specify",
                            f"this argument: {expected_arg}",
                            file=sys.stderr
                        )
                        args_respected = False

    all_hooks_found: bool = True
    for hook_found in hooks_found.values():
        all_hooks_found = all_hooks_found and hook_found
    if not all_hooks_found:
        print(
            "ERROR: All of the standard pre-commit hooks for files",
            f"that match “{glob}” weren’t found. Here’s the hooks that",
            f"should have been found: {repo_info}",
            file=sys.stderr
        )
    return (
        no_errors
        and excludes_respected
        and args_respected
        and all_hooks_found
    )


def main() -> int:
    init()
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
    if EXPECTED_COPYING_INFO != COPYING_CONTENTS:
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
    # Does .editorconfig exist?
    EDITOR_CONFIG_PATH: Final = pathlib.Path('.editorconfig')
    if EDITOR_CONFIG_PATH not in PATHS:
        print_no_file_error(EDITOR_CONFIG_PATH)
        return 1
    # Does .editorconfig contain the correct text?
    EDITOR_CONFIG_CONTENTS: Final = \
        EDITOR_CONFIG_PATH.read_text(encoding='utf_8')
    if EDITOR_CONFIG_CONTENTS != EXPECTED_EDITOR_CONFIG:
        print(
            f"ERROR: {EDITOR_CONFIG_PATH} doesn’t the standard",
            f"{EDITOR_CONFIG_PATH} file. Fixing…",
            file=sys.stderr
        )
        EDITOR_CONFIG_PATH.write_text(
            EXPECTED_EDITOR_CONFIG,
            encoding='utf_8'
        )
        return 1
    # Is pre-commit set up?
    PC_CONFIG_PATH: Final = pathlib.Path(".pre-commit-config.yaml")
    if PC_CONFIG_PATH not in PATHS:
        print_no_file_error(PC_CONFIG_PATH)
        return 1
    # Does README.md have a “Hints for Contributors” section?
    if HINTS_FOR_CONTRIBUTORS_HEADING not in README_CONTENTS:
        print(
            f"ERROR: {README_PATH} doesn’t have a “Hints for",
            f"Contributors” section. Make sure that {README_PATH}",
            f"contains this:\n\n\t{HINTS_FOR_CONTRIBUTORS_HEADING}",
            file=sys.stderr
        )
        return 1
    # Do the Hints for Contributors contain some standard hints for
    # certain files?
    globs: Iterable[str]
    hint: str
    any_errors: bool = False
    for globs, hint in HINTS_FOR_CONTRIBUTORS_BY_PATH:
        path: pathlib.Path
        for path in PATHS:
            glob: str
            for glob in globs:
                if path.match(glob, case_sensitive=False):
                    if hint not in README_CONTENTS:
                        hint_indented: str = textwrap.indent(hint, "\t")
                        print(
                            f"ERROR: {README_PATH} doesn’t contain",
                            "this hint for",
                            f"contributors:\n\n{hint_indented}\n",
                            file=sys.stderr
                        )
                        print(
                            f"(glob {glob} matched by file {path})",
                            file=sys.stderr
                        )
                        any_errors = True
                        break
    if any_errors:
        return 1
    # Does the pre-commit config contain some standard hooks for certain
    # files?
    missing_hooks: bool = False
    PC_CONFIG: Final = yaml.safe_load(
        PC_CONFIG_PATH.read_text(encoding='utf_8')
    )
    repo_info: PreCommitRepoInfo
    for globs, repo_info in PRE_COMMIT_REPOS_BY_PATH:
        for path in PATHS:
            for glob in globs:
                if path.match(glob, case_sensitive=False):
                    hooks_found: bool = check_pc_config_hooks(
                        PC_CONFIG,
                        repo_info,
                        glob
                    )
                    if not hooks_found:
                        missing_hooks = True
                    break
    if missing_hooks:
        return 1

    return 0
