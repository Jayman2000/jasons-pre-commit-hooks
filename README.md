<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2023–2024 Jason Yundt <jason@jasonyundt.email>
-->

# Jason’s Pre-commit Hooks

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
