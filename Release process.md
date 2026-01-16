<!--
SPDX-License-Identifier: CC0-1.0
SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
-->

# Release process for Jason’s Pre-commit Hooks

Maintainers should do the following in order to create a new release of
Jason’s Pre-commit Hooks:

1. Make sure that it’s actually time to do a release.

    [`VERSIONING.md`] contains information about how to determine
    whether or not it’s time to do a release. You should manually verify
    that it is indeed time to do a release just in case the
    `unreleased-commit-checker` pre-commit hook is producing incorrect
    results.

1. Get ready to work on this repository by doing the following:

    1. Make sure that you have a copy of this repository on your
    computer.

    1. Open a terminal.

    1. Make sure that you have the Nix package manager installed by
    running this command:

        ```bash
        nix-env --version
        ```

        If that command succeeds, then you have the Nix package manager
        installed. If that command fails, then you need to install the
        Nix package manager.

    1. Change directory into the root of this repository.

    1. Check to see if there are any uncommitted changes by running this
    command:

        ```bash
        git status
        ```

    1. If there are any uncommitted changes, then stash them.

    1. Make sure that you’re on the `main` branch by running this
    command:

        ```bash
        git switch main
        ```

    1. Start this repository’s dev shell by running this command:

        ```bash
        nix --extra-experimental-features 'nix-command flakes' develop
        ```

    1. Make sure that you’re logged in to `gh` by running this command:

        ```bash
        gh auth status
        ```

1. Potentially fix pre-commit errors by following these steps:

    1. Run all pre-commit hooks except for `unreleased-commit-checker`
    by running this command:

        ```bash
        SKIP=unreleased-commit-checker pre-commit run --all
        ```

        We’re skipping `unreleased-commit-checker` here because we
        expect it to fail. Doing a new stable release should make it so
        that `unreleased-commit-checker` stops failing.

    1. If there were any pre-commit failures, then take some time to fix
    those failures before continuing.

1. Create a new branch for the release by following these steps:

    1. Create and switch to a new branch named `vTODO-release` by
    running this command:

        ```bash
        git switch --create vTODO-release main
        ```

        In a later step, we’ll replace the “TODO” with the new release’s
        version number.

    1. Add a new section to [`CHANGELOG.md`] named “vTODO” that
    documents the changes from the previous version.

    1. Determine what the new version number should be.

        You should be able to figure out what the new version number
        should be by looking at the newly created “vTODO” section in the
        changelog and by looking at [`VERSIONING.md`].

    1. Rename the `vTODO-release` branch to `v<version number>-release`
    by running this command:

        ```bash
        git branch --move vTODO-release v<version number>-release
        ```

    1. Rename the “vTODO” section of the changelog to “v&lt;version
    number&gt; — &lt;release date&gt;”.

    1. Make sure that your changes to [`CHANGELOG.md`] are committed.

    1. Create a new commit that updates the `version` attribute in
    `flake-blueprint/packages/jasons-pre-commit-hooks.nix`.

1. Create the release by doing the following:

    1. Make sure that you’re on the `main` branch by running this
    command:

        ```bash
        git switch main
        ```

    1. Merge the `v<version number>-release` branch into the `main`
    branch by running this command:

        ```bash
        git merge --no-ff v<version number>-release
        ```

    1. Create a tag for the new version by running this commangd:

        ```bash
        git tag v<version number>
        ```

    1. Push the `main` branch and the newly created tag to GitHub by
    running this command:

        ```bash
        git push --tags <remote> main
        ```

    1. Use the GitHub Web interface in order to make sure that the
    `main` branch and the tag were pushed successfully.

    1. Create a new GitHub release by running this command:

        ```bash
        gh release create
        ```

    1. Switch to the `stable` branch by running this command:

        ```bash
        git switch stable
        ```

    1. Merge the new release into the `stable` branch by running this
    command:

        ```bash
        git merge --ff-only main
        ```

    1. Push the `stable` branch to GitHub by running this command:

        ```bash
        git push <remote> stable
        ```

    1. Use the GitHub Web interface in order to make sure that the
    `stable` branch was pushed successfully.

1. Perform a few post-release tasks by following these instructions:

    1. Make sure that you’re on the `main` branch by running this
    command:

        ```bash
        git switch main
        ```

    1. Delete the local `v<version number>-release` branch by running
    this command:

        ```bash
        git branch --delete v<version number>-release
        ```

    1. If there are any remote `v<version number>-release` branches,
    then delete them by running this command for each remote that has a
    copy of the branch:

        ```bash
        git push --delete <remote> v<version number>-release
        ```

    1. Check for any new pre-commit failures by running this command.

        ```bash
        pre-commit run --all
        ```

    1. If there are any new pre-commit failures, then fix them.

    1. Revert the previously made commit that changed the value of the
    `version` attribute in
    `flake-blueprint/packages/jasons-pre-commit-hooks.nix`.

[`CHANGELOG.md`]: ./CHANGELOG.md
[`VERSIONING.md`]: ./VERSIONING.md
