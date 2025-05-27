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
        git add .
        git commit --message='Initial commit'
        git clean -dx --force
      '';
  pre-commitConfig = builtins.readFile ../../.pre-commit-config.yaml;
  hashType = "sha256";
  hashedStorePath = builtins.hashString hashType "${devShell}";
  # Normally, I would just use a store path here rather than a hashed
  # store path. I’m using a hashed store path here in order to obfuscate
  # the contents of the store path. Normally, Nix doesn’t allow the
  # outputs of fixed-output derivations to reference store paths [1].
  # There is a way to override that default [2], but I don’t really need
  # to override it. Instead, I can just avoid having any direct
  # references to store paths. I don’t really need any direct references
  # to any store paths in the output anyway.
  #
  # editorconfig-checker-disable
  # [1]: <https://github.com/NixOS/nix/issues/11673>
  # [2]: <https://nix.dev/manual/nix/2.28/language/advanced-attributes#adv-attr-unsafeDiscardReferences>
  # editorconfig-checker-enable
  dataToHash = pre-commitConfig + "# ${hashedStorePath}\n";
in
pkgs.runCommandWith
  {
    inherit (devShell) stdenv;
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
      # The fixed-output of this fixed-output derivation is just
      # dataToHash. dataToHash is derived from this repository’s
      # pre-commit config and its default dev shell. I chose that value
      # for dataToHash in order to make sure that this fixed-output
      # derivation has to be rebuilt every time either the pre-commit
      # config or the default dev shell is updated.
      #
      # editorconfig-checker-disable
      # [1]: <https://nix.dev/manual/nix/2.28/glossary.html#gloss-fixed-output-derivation>
      # editorconfig-checker-enable
      outputHash = builtins.hashString hashType dataToHash;
      outputHashAlgo = hashType;
    };
  }
  ''
    ${createHomeDirectory}
    cp \
      --no-preserve=mode \
      --recursive \
      ${pkgs.lib.strings.escapeShellArg repoThatContainsThisFlake} \
      repo
    cd repo

    ${devShell.shellHook}
    pre-commit install-hooks

    printf '%s' ${pkgs.lib.strings.escapeShellArg dataToHash} > "$out"
  ''
