# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{
  flake,
  pkgs,
  pname,
  system,
  ...
}:
let
  devShell = flake.devShells."${system}".default;
  # The default home directory in the sandbox isn’t writable. Having an
  # unwritable home directory will make Git and pre-commit not work in
  # certain situations.
  createHomeDirectory = ''
    mkdir home
    declare -rx HOME="$(readlink --canonicalize ./home)"
  '';
  # Normally, I would just use the flake parameter, but unfortunately
  # "${flake}" evaluates to a path that doesn’t contain a .git
  # directory. The pre-commit command will fail if there isn’t a .git
  # directory.
  repoThatContainsThisFlake =
    pkgs.runCommandWith
      {
        name = "repo-that-contains-this-flake";
        derivationArgs.nativeBuildInputs = [ pkgs.git ];
      }
      ''
        ${createHomeDirectory}
        git config --global user.name 'Connor Sample'
        git config --global user.email 'connor@example.com'

        cp \
          --no-preserve=mode \
          --recursive ${pkgs.lib.strings.escapeShellArg flake} "$out"
        cd "$out"
        git init
        # By default, Git will put some sample hooks in .git/hooks.
        # Those sample hooks reference the Nix store paths. The output
        # of fixed-output derivations is not allowed to reference Nix
        # store paths [1] so we remove the sample hooks here.
        #
        # To be clear: repo-that-contains-this-flake is not actually a
        # fixed-output derivation. The output from
        # repo-that-contains-this-flake gets copied into the output of
        # the dev-shell-dependencies-for-pre-commit derivation. The
        # dev-shell-dependencies-for-pre-commit derivation is a
        # fixed-output derivation.
        #
        # [1]: <https://github.com/NixOS/nix/issues/11673>
        rm --recursive .git/hooks/*
        git add .
        git commit --message='Initial commit'
        git clean -dx --force
      '';
  hashOfRepoThatContainsThisFlake =
    pkgs.runCommandWith
      {
        name = "hash-of-repo-that-contains-this-flake";
        derivationArgs.nativeBuildInputs = [ pkgs.nix ];
      }
      ''
        nix-hash \
          --type sha256 \
          --sri \
          ${pkgs.lib.strings.escapeShellArg repoThatContainsThisFlake} \
          | tr --delete '\n' > "$out"
      '';
in
pkgs.runCommandWith
  {
    name = pname;
    derivationArgs = {
      # The cacert thing is needed to work around this limitation [1].
      #
      # [1]: <https://github.com/NixOS/nixpkgs/issues/406157>
      nativeBuildInputs = devShell.nativeBuildInputs ++ [ pkgs.cacert ];
      # Adding outputHash here turns this derivation into a fixed-output
      # derivation. Unlike regular derivations, the builder for
      # fixed-output derivations is allowed to access the network [1].
      # The builder for this derivation needs to be able to access the
      # network because it tests a pre-commit command that needs to
      # access the Internet.
      #
      # The fixed-output of this fixed-output derivation is just a copy
      # of a Git repo that contains this flake. I chose to do that to
      # make sure that the fixed-output derivation has to be rebuilt
      # every time the flake is updated.
      #
      # editorconfig-checker-disable
      # [1]: <https://nix.dev/manual/nix/2.28/glossary.html#gloss-fixed-output-derivation>
      # editorconfig-checker-enable
      outputHash = builtins.readFile hashOfRepoThatContainsThisFlake;
      outputHashMode = "nar";
    };
  }
  ''
    ${createHomeDirectory}
    cp \
      --no-preserve=mode \
      --recursive \
      ${pkgs.lib.strings.escapeShellArg repoThatContainsThisFlake} \
      "$out"
    cd "$out"

    ${devShell.shellHook}
    pre-commit install-hooks
  ''
