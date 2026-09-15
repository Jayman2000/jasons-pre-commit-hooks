# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
import argparse
import io
import shlex
import sys
from typing import Final

import dulwich.graph
import dulwich.objects
import dulwich.porcelain
import dulwich.refs
import dulwich.repo

from . import init, open_cwd_as_repo


def str_to_object_id(s: str) -> dulwich.objects.ObjectID:
    return dulwich.objects.ObjectID(s.encode(encoding="utf_8"))


def most_recent_commit_for_path(
    path: str,
    since: str | None = None
) -> dulwich.objects.ObjectID:
    outstream: io.StringIO
    with io.StringIO() as outstream:
        dulwich.porcelain.log(
            paths=(path,),
            outstream=outstream,
            max_entries=1,
            since=since,
        )
        LOG: Final = outstream.getvalue()
    if len(LOG) == 0:
        raise ValueError(
            f"There are no commits for {path!r} that are earlier than "
            f"{since!r}."
        )
    else:
        return str_to_object_id(LOG.splitlines()[1].partition(" ")[2])


def is_most_recent_commit_too_old(path: str, since: str) -> bool:
    try:
        most_recent_commit_for_path(path, since)
    except ValueError:
        return True
    return False


def remote_ref_to_commit(
    remote_url: str,
    remote_ref: str
) -> dulwich.objects.ObjectID:
    RESULT: Final = dulwich.porcelain.ls_remote(remote=remote_url)
    if RESULT is None:
        raise TypeError("RESULT was None. Was the remote_url valid?")
    else:
        RETURN_VALUE: Final = RESULT[
            dulwich.refs.Ref(remote_ref.encode(encoding="utf_8"))
        ]
        if RETURN_VALUE is None:
            raise TypeError(
                "RETURN_VALUE was None. Was the remote_ref valid?"
            )
        else:
            return RETURN_VALUE


def are_commits_related(
    local_commit: dulwich.objects.ObjectID,
    remote_commit: dulwich.objects.ObjectID
) -> bool:
    repo: dulwich.repo.Repo
    with open_cwd_as_repo() as repo:
        try:
            repo.get_object(remote_commit)
        except KeyError:
            # In this case, remote_commit doesn’t even exist in the
            # local Git repository so there’s no way that the two
            # commits are related.
            return False
        INDEPENDENT_COMMITS: Final = dulwich.graph.independent(
            repo,
            (local_commit, remote_commit)
        )
    return len(INDEPENDENT_COMMITS) == 0


def is_subtree_outdated(
    prefix: str,
    date: str,
    remote_url: str,
    remote_ref: str
) -> bool:
    if is_most_recent_commit_too_old(prefix, date):
        return True
    try:
        MOST_RECENT_COMMIT_FOR_PATH: Final = (
            most_recent_commit_for_path(prefix)
        )
    except ValueError:
        return True
    return not are_commits_related(
        MOST_RECENT_COMMIT_FOR_PATH,
        remote_ref_to_commit(remote_url, remote_ref)
    )


def main() -> int:
    init()
    ARGUMENT_PARSER: Final = argparse.ArgumentParser(
        description="""
            Old Subtree Alert is a tool that will give you an error if
            you haven’t updated a Git subtree in a while.
        """
    )
    ARGUMENT_PARSER.add_argument(
        "prefix",
        help="""
            Path to the subtree relative to the root of the repository
        """,
        metavar="PREFIX"
    )
    ARGUMENT_PARSER.add_argument(
        "url",
        help="""
            Web address of the remote repository that’s been stored in
            the subtree
        """,
        metavar="URL"
    )
    ARGUMENT_PARSER.add_argument(
        "remote_ref",
        help="""
            The Git remote ref that’s been stored in the subtree
        """,
        metavar="REMOTE_REF"
    )
    ARGUMENT_PARSER.add_argument(
        "date",
        help="""
            Give an error if the given subtree hasn’t been updated since
            DATE. DATE can be any date string that’s accepted by
            git-log’s --since option.
        """,
        metavar="DATE"
    )
    ARGS: Final = ARGUMENT_PARSER.parse_args()

    if is_subtree_outdated(
        ARGS.prefix,
        ARGS.date,
        ARGS.url,
        ARGS.remote_ref
    ):
        MESSAGE: Final = (
            f"The {ARGS.prefix!r} subtree is old. Its last update was "
            f"earlier than {ARGS.date!r}. At some point, someone "
            "should update it by running this command:\n"
            "\n"
            f"    git subtree --prefix={shlex.quote(ARGS.prefix)} pull "
            f"{shlex.join((ARGS.url, ARGS.remote_ref))}"
        )
        print(MESSAGE, file=sys.stderr)
        # This is EX_DATAERR from <man:sysexits.h(3head)>.
        return 65
    else:
        print(f"The {ARGS.prefix!r} subtree is up to date.")
        return 0
