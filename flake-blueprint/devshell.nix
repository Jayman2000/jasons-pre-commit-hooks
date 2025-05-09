# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{ pkgs }:
pkgs.mkShellNoCC {
  name = "shell-for-working-on-jasons-pre-commit-hooks";
  packages = with pkgs; [
    pre-commit
    # Dependencies for pre-commit hooks:
    cabal-install
    ghc
  ];
  shellHook = ''
    export PIP_NO_BINARY=ruff
  '';
}
