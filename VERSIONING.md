<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
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

## When are new versions released?

In order to figure out when new versions should be released, here’s what
I do:

1. Keep track of the number of unreleased commits. An unreleased commit
is a commit that’s in the main branch’s commit log, but isn’t in any of
the releases’s commit logs.
2. If there’s thirty or more unreleased commits, then do a release.
3. If there’s an unreleased commit that’s over three months old, then do
a release.

If you want a release to come out sooner, then contribute. The sooner we
hit the thirty commit mark, the sooner a release happens.

<!--- editorconfig-checker-disable -->
[1]: https://github.com/Jayman2000/jmvs/releases/tag/v0.0.0
[2]: https://packaging.python.org/en/latest/glossary/#term-Distribution-Package
[3]: https://setuptools.pypa.io/en/stable/userguide/entry_point.html#console-scripts
[4]: https://pre-commit.com/#repos-repo
[5]: https://pre-commit.com/#creating-new-hooks
<!--- editorconfig-checker-enable -->
