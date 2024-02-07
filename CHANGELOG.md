<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2024 Jason Yundt <jason@jasonyundt.email>
-->

# Changelog

All notable changes to this project will be documented in this file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). See
[`./VERSIONING.md`](./VERSIONING.md) for information about this
project’s version numbers.

## [v0.0.0] — 2024-02-07

### Added

- A pre-commit hook named `repo-style-checker`. It has one option:
`--skip`
- A pre-commit hook named `detect-bad-unicode`
- A pre-commit hook named `unreleased-commit-checker`
- A version numbering scheme.

### Removed

- Support for Python versions less than 3.12.

## [pre-version-0] — 2024-01-10

Initial prerelease. This prerelease was created before I had chosen a
version numbering scheme. That’s why its version number is so weird.

### Added

- A pre-commit hook named `forbid-paths-that-match`

<!--
editorconfig-checker-disable
-->
[v0.0.0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/v0.0.0
[pre-version-0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/pre-version-0
<!--
editorconfig-checker-enable
-->
