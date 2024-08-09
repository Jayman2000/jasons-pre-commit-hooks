<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2023–2024 Jason Yundt <jason@jasonyundt.email>
-->

# Jason’s Pre-commit Hooks

This repo contains [pre-commit][1] hooks that
[Jason](https://github.com/Jayman2000) uses for his personal projects.
If you aren’t Jason and you also aren’t contributing to one of Jason’s
projects, then this repo probably won’t be helpful to you.

If you want to know more about what the hooks in this repo do, then take
a look at [`VERSIONING.md`]. Specifically, [`VERSIONING.md`] will tell
you what you need to to in order to find the API docs for the scripts in
this repo.

[`VERSIONING.md`]: ./VERSIONING.md

## Hints for Contributors

- You can use [pre-commit][1] to automatically check your contributions.
Follow [these instructions][2] to get started. Skip [the part about
creating a pre-commit configuration][3].
- This repo uses an [EditorConfig](https://editorconfig.org) file.
- Try to keep lines shorter than seventy-three characters.
- Use [CommonMark](https://commonmark.org) for
[Markdown](https://daringfireball.net/projects/markdown) files.
- If you’re using [NixOS](https://nixos.org), then the
[ruff](https://docs.astral.sh/ruff/) pre-commit hook probably won’t
work. Here’s how you fix it:

    1. Set the `PIP_NO_BINARY` environment variable to “ruff”.
    2. Run `pre-commit clean`
    3. Run `pre-commit install-hooks`

[1]: https://pre-commit.com
[2]: https://pre-commit.com/#quick-start
[3]: https://pre-commit.com/#2-add-a-pre-commit-configuration

## Copying

See [`copying.md`](./copying.md).
