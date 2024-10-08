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

## [v0.3.0] — 2024-10-04

### Added

- `repo-style-checker` now requires that you use
[`nixfmt`](https://github.com/NixOS/nixfmt) if you have `.nix` files in
your repo.
- `repo-style-checker` now requires that you use [`pre-commit-update`].
- This repo now has a new pre-commit hook named `flake-lock-updater`.
- `repo-style-checker` now requires that you use `flake-lock-updater` if
you have a `flake.lock` file in your repo.

### Changed

- `repo-style-checker`’s standard EditorConfig now uses two spaces for
the indentation of `.nix` files.
- The comments in `repo-style-checker`’s standard EditorConfig have been
improved.
- `repo-style-checker`’s standard `coping.md` file now uses a stable
version of the REUSE Specification.
- `repo-style-checker`’s standard `coping.md` file now does a better job
at explaining how some items on the SPDX License List aren’t necessarily
licenses.

## [v0.2.0] — 2024-08-09

### Added

- `repo-style-checker` now has a `--disable-hook` option.

### Changed

- The text for one of `repo-style-checker`’s standard Hints for
Contributors was changed so that it doesn’t link to the original
Markdown site. It now only links to the CommonMark site.
- Multiple small improvements to the comments in `repo-style-checker`’s
standard EditorConfig file were made.

### Fixed

- `repo-style-checker` used to use the old URL for `pre-commit-update`’s
repo. That old URL now 404s. `repo-style-checker` now uses
`pre-commit-update`’s new URL.
- A grammar mistake in one of `repo-style-checker`’s error messages was
fixed.
- A grammar mistake in `repo-style-checker`’s standard EditorConfig file
was fixed.

## [v0.1.0] — 2024-07-05

### Added

- A pre-commit hook named `unreleased-commit-checker`. It has no options
at the moment (other than `--help`).

### Changed

- `repo-style-checker` now requires that `unreleased-commit-checker` is
enabled if repos contain `/VERSIONING.md`.

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
[v0.3.0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/v0.3.0
[v0.2.0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/v0.2.0
[v0.1.0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/v0.1.0
[v0.0.0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/v0.0.0
[pre-version-0]: https://github.com/Jayman2000/jasons-pre-commit-hooks/releases/tag/pre-version-0

[`pre-commit-update`]: https://gitlab.com/vojko.pribudic.foss/pre-commit-update
<!--
editorconfig-checker-enable
-->
