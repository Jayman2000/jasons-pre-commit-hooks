# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
{
  perSystem,
  pkgs,
  pname,
}:
pkgs.symlinkJoin (finalAttrs: {
  inherit pname;
  # Assert that the version number for all packages is the same.
  version =
    let
      versionNumbers = pkgs.lib.lists.map (package: package.version) finalAttrs.packages;
      firstVersionNumber = pkgs.lib.lists.head versionNumbers;
    in
    assert pkgs.lib.asserts.assertEachOneOf "versionNumbers" versionNumbers [ firstVersionNumber ];
    firstVersionNumber;

  # Normally, when you use synlinkJoin, you create a paths attribute. In this
  # situation, we create both a packages and a paths attribute. Any derivation
  # that gets added to the paths list will be converted into a string when you
  # access finalAttrs.paths. That doesn’t work for the above code which asserts
  # that all of the package version numbers are the same. Therefore, we need to
  # create another attribute other than paths which won’t turn all of our
  # derivations into strings.
  packages = [
    perSystem.self.jasons-pre-commit-hooks-python
    perSystem.self.jasons-pre-commit-hooks-rust
  ];
  paths = finalAttrs.packages;
})
