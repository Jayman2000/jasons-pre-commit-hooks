# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{
  description = "Pre-commit hooks that I use for my projects";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    blueprint = {
      url = "github:numtide/blueprint";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        systems.follows = "jasons-nix-flake-style-guide/systems";
      };
    };
    jasons-nix-flake-style-guide = {
      # editorconfig-checker-disable
      url = "git+https://codeberg.org/JasonYundt/jasons-nix-flake-style-guide.git";
      # editorconfig-checker-enable
      inputs = {
        nixpkgs.follows = "nixpkgs";
        blueprint.follows = "blueprint";
      };
    };
  };
  outputs =
    inputs:
    inputs.blueprint {
      inherit inputs;
      prefix = "flake-blueprint";
    };
}
