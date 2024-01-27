# -*- coding: utf-8 -*-
# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
import argparse
import datetime
from typing import Any, Final, NamedTuple, Optional, Self

import dateutil.relativedelta
import dulwich.objects
import dulwich.repo
import dulwich.walk
import semver

from . import init, open_cwd_as_repo


# editorconfig-checker-disable
# See
# <https://git-scm.com/docs/gitglossary#Documentation/gitglossary.txt-aiddeftagatag>.
# editorconfig-checker-enable
TAG_REF_PREFIX: Final = b'refs/tags/'


class TagForVersion:
    def __init__(
        self,
        ref: bytes,
        second_arg: bytes | dulwich.repo.Repo
    ) -> None:
        self.name: str = ref_to_tag_name(ref)
        self.target: bytes
        if isinstance(second_arg, bytes):
            self.target = second_arg
        else:
            self.target = second_arg.get_peeled(ref)

        self.version_number: Optional[semver.Version] = None
        if self.name.startswith('v'):
            version_number: str = self.name.removeprefix('v')
            try:
                self.version_number = \
                    semver.Version.parse(version_number)
            except ValueError:
                pass

    def __repr__(self) -> str:
        return (
            'TagForVersion('
                f'{tag_name_to_ref(self.name)!r}, '
                f'{self.target!r}'
            ')'
        )

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, TagForVersion):
            if self.version_number is None:
                if other.version_number is None:
                    return self.name < other.name
                else:
                    return True
            else:
                if other.version_number is None:
                    return False
                else:
                    return self.version_number < other.version_number
        else:
            raise ValueError(f"Can’t compare {self} to {other}.")


    def uses_semver(self) -> bool:
        return self.version_number is not None


age_of_oldest_type = Optional[dateutil.relativedelta.relativedelta]
class UnreleasedCommitStats(NamedTuple):
    amount: int
    age_of_oldest: age_of_oldest_type

    @classmethod
    def from_cwd(cls) -> Self:
        repo: dulwich.repo.Repo
        with open_cwd_as_repo() as repo:
            REFS: Final[dict[bytes, bytes]] = repo.get_refs()
            TAGS: Final = (
                TagForVersion(ref, repo)
                for ref in REFS
                if is_tag(ref)
            )
            LATEST_VERSION: Final[TagForVersion] = max(TAGS)
            MAIN_HEAD: Final[bytes] = REFS[b'refs/heads/main']
            UNRELEASED_COMMIT_WALKER: Final = repo.get_walker(
                include=[MAIN_HEAD],
                exclude=[LATEST_VERSION.target]
            )
            UNRELEASED_COMMIT_LOG: Final = tuple(
                UNRELEASED_COMMIT_WALKER
            )
            AMOUNT: Final = len(UNRELEASED_COMMIT_LOG)
            age_of_oldest: age_of_oldest_type
            try:
                OLDEST_UNRELEASED_COMMIT: Final = \
                    UNRELEASED_COMMIT_LOG[-1].commit
                age_of_oldest = dateutil.relativedelta.relativedelta(
                    datetime.datetime.now(datetime.timezone.utc),
                    commit_date(OLDEST_UNRELEASED_COMMIT)
                )
            except IndexError:
                age_of_oldest = None
        return cls(
            amount=AMOUNT,
            age_of_oldest=age_of_oldest
        )


def is_tag(ref: bytes) -> bool:
    return ref.startswith(TAG_REF_PREFIX)


def ref_to_tag_name(ref: bytes) -> str:
    return ref.removeprefix(TAG_REF_PREFIX).decode(encoding='utf_8')


def tag_name_to_ref(name: str) -> bytes:
    return TAG_REF_PREFIX + name.encode(encoding='utf_8')


def commit_date(commit: dulwich.objects.Commit) -> datetime.datetime:
    OFFSET: Final = datetime.timedelta(seconds=commit.commit_timezone)
    TIME_ZONE: Final = datetime.timezone(OFFSET)
    return datetime.datetime.fromtimestamp(
        commit.commit_time,
        tz=TIME_ZONE
    )


def age_to_str(age: dateutil.relativedelta.relativedelta) -> str:
    if age.years != 0:
        return f"{age.years} years"
    elif age.months != 0:
        return f"{age.months} months"
    elif age.days != 0:
        return f"{age.days} days"
    elif age.hours != 0:
        return f"{age.hours} hours"
    elif age.minutes != 0:
        return f"{age.minutes} minutes"
    elif age.seconds != 0:
        return f"{age.seconds} seconds"
    else:
        return f"{age.microseconds} microseconds"


def is_age_too_big(age: dateutil.relativedelta.relativedelta) -> bool:
    NORMALIZED_AGE: Final = age.normalized()
    return NORMALIZED_AGE.years > 0 or NORMALIZED_AGE.months >= 3


def main() -> int:
    init()
    PARSER: Final = argparse.ArgumentParser(
        description=(
            "Tells you how many unreleased commits there are and gives "
            "an error if a release needs to be made."
        )
    )
    # This command doesn’t take any arguments, so this just makes sure
    # that --help works and that errors are produced if arguments are
    # given.
    PARSER.parse_args()

    STATS: Final = UnreleasedCommitStats.from_cwd()
    print(f"There are {STATS.amount} unreleased commits.")
    release_required: bool
    if STATS.age_of_oldest is None:
        release_required = False
    else:
        print(
            "The oldest unreleased commit is",
            age_to_str(STATS.age_of_oldest),
            "old."
        )
        release_required = \
            STATS.amount >= 30 or is_age_too_big(STATS.age_of_oldest)
    if release_required:
        print("It’s time to do a release.")
    else:
        print("It’s not time to do a release yet.")
    return release_required
