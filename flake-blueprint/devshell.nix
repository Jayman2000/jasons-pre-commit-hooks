# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{ perSystem, pkgs }:
pkgs.mkShell {
  name = "shell-for-working-on-jasons-pre-commit-hooks";
  packages = with pkgs; [
    gh
    pre-commit
    # Dependencies for pre-commit hooks:
    cabal-install
    ghc
    nodejs
    cargo
    perSystem.nixpkgsUnstable.rustc
    go
  ];
  shellHook = ''
    export PIP_NO_BINARY=ruff
  '';
}
