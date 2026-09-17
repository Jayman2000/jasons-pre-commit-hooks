# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025–2026 Jason Yundt <jason@jasonyundt.email>
{
  pname,
  pkgs,
  flake,
}:
pkgs.rustPlatform.buildRustPackage (
  finalAttrs:
  let
    inherit (pkgs.lib.strings) escapeNixString;
    cargoTOMLData = pkgs.lib.trivial.importTOML "${finalAttrs.src}/Cargo.toml";
  in
  {
    pname =
      assert pkgs.lib.asserts.assertMsg (pname == cargoTOMLData.package.name)
        "pname (${escapeNixString pname}) and Rust package name (${escapeNixString cargoTOMLData.package.name}) don’t match";
      pname;
    inherit (cargoTOMLData.package) version;

    src = flake;
    cargoHash = "sha256-KocDrgowBfXNFxDBteAtiWHo/cd1KpP2mpPfmmuj4gg=";

    nativeBuildInputs = [ pkgs.perl ];
  }
)
