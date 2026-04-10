<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2024–2025 Jason Yundt <jason@jasonyundt.email>
-->

# Versioning Information for Jason’s Pre-commit Hooks

This project follows [version 0.0.0 of the JMVS specification][1]. That
specification says that projects must declare a public API. Here is this
project’s public API:

- This repo can be installed as a [Python distribution package][2] by
running `pip install .`
- That distribution package provides multiple [console scripts][3]. Only
console scripts that are listed in `.pre-commit-hooks.yaml` are part of
the public API.
- You can run `<console-script-name> --help` to get a list of options
and arguments that are accepted by that command. Those options and
arguments are a part of the public API.
- This repo can be used as a [pre-commit hooks repo][4].
- The contents of `.pre-commit-hooks.yaml` is a part of the public API.
For more information about the format of `.pre-commit-hooks.yaml`, see
[pre-commit’s documentation][5].

## Version numbers for unstable commits

This project makes no guarantees about the version numbers of unstable
commits. If a commit hasn’t been marked as being an official release,
then there’s no guarantee that it will actually conform to the JMVS
specification.

## The two types of releases

Jason’s Pre-commit Hooks has two different types of releases:

1. Regular releases

2. Backport releases

Regular releases are snapshots of the `main` branch. Backport releases
are snapshots of one of the backport branches. In order for a commit to
make it into a regular release, that commit must make it into the `main`
branch. In order for a commit to make it into a backport release, the
following must happen:

1. The commit must make it into the `main` branch.

2. A backport branch must exist. The name of the backport branch must be
`v<version number>-backports`. The starting point for the branch must be
a `post-v<version number>-release-tasks` merge commit that’s in the
`main` branch.

    For example, if you wanted to use version 0.7.1 as the starting
    point for a backport branch, then you could run this command in
    order to create the branch properly:

    <!-- editorconfig-checker-disable -->

    ```bash
    git switch --create v0.7.1-backports 7cc8a5d8bd4f9fbcc2e1bc12e83a2d9f5b78fb5d
    ```

    <!-- editorconfig-checker-enable -->

    7cc8a5d8bd4f9fbcc2e1bc12e83a2d9f5b78fb5d is a commit from the `main`
    branch. It’s a merge commit for the `post-v0.7.1-release-tasks`
    backport branch:

    ```console
    $ git show 7cc8a5d8bd4f9fbcc2e1bc12e83a2d9f5b78fb5d
    commit 7cc8a5d8bd4f9fbcc2e1bc12e83a2d9f5b78fb5d
    Merge: adaa87e d88d719
    Author: Jason Yundt <jason@jasonyundt.email>
    Date:   Thu Jan 15 08:55:23 2026 -0500

        Merge branch 'post-v0.7.1-release-tasks'

    $
    ```

3. The commit that’s in the `main` branch must be cherry-picked using
`git cherry-pick -x` and put into the `v<version number>-backports`
branch.

    Pretty much every commit added to a `v<version number>-backports`
    branch should be something that was cherry-picked from the `main`
    branch. The only real exceptions to this rule are commits that get
    created as a part of the release process.

Most releases will (hopefully) be regular releases. Backport releases
should generally only be created in order to more quickly release bug
fixes for significant bugs introduced in regular releases.

## Determining the previous version number

[The JMVS specification talks about incrementing version numbers:][6]

> 1. Patch version Z (x.y.Z | x > 0) MUST be incremented if only
> backward compatible bug fixes are introduced. A bug fix is defined as
> an internal change that fixes incorrect behavior.
>
> 1. Minor version Y (x.Y.z | x > 0) MUST be incremented if new,
> backward compatible functionality is introduced to the public API. It
> MUST be incremented if any public API functionality is marked as
> deprecated. It MAY be incremented if non-breaking changes are made. It
> MAY include patch level changes. Patch version MUST be reset to 0 when
> minor version is incremented.
>
> 1. Major version X (X.y.z | X > 0) MUST be incremented if any backward
> incompatible changes are introduced to the public API. It MAY also
> include minor and patch level changes. Patch and minor versions MUST
> be reset to 0 when major version is incremented.

This then begs the question: increment from what? What version number do
you start from when incrementing?

For regular releases, look at all of the releases that have been made so
far and find the highest version number. See the JMVS specification for
information about how to determine if one version number is higher than
another.

For backport releases, start from the version number that’s in the
backport branch’s name. For example, if the backport branch is named
`v0.7.1-backports`, then start with “0.7.1” as the version number.

## When are new versions released?

### Regular releases

In order to figure out when a new regular release should be created,
here’s what I do:

1. Keep track of the number of unreleased commits. An unreleased commit
is a commit that’s in the main branch’s commit log, but isn’t in any of
the releases’s commit logs.
2. If there’s thirty or more unreleased commits, then it’s time to do a
regular release.
3. If there’s an unreleased commit that’s over three months old, then
it’s time to do a regular release.

If you want a release to come out sooner, then contribute. The sooner we
hit the thirty commit mark, the sooner a release happens.

### Backport releases

Backport releases can be created at anytime.

## How releases are created

Once it’s time to do a release, a release will be created by following
the instructions in [`Release process.md`](./Release%20process.md).

<!--- editorconfig-checker-disable -->
[1]: https://github.com/Jayman2000/jmvs/releases/tag/v0.0.0
[2]: https://packaging.python.org/en/latest/glossary/#term-Distribution-Package
[3]: https://setuptools.pypa.io/en/stable/userguide/entry_point.html#console-scripts
[4]: https://pre-commit.com/#repos-repo
[5]: https://pre-commit.com/#creating-new-hooks
[6]: https://github.com/Jayman2000/jmvs/blob/v0.0.0/semver.md#semantic-versioning-specification-semver
<!--- editorconfig-checker-enable -->
