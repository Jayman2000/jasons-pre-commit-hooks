# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025–2026 Jason Yundt <jason@jasonyundt.email>
{
  pname,
  pkgs,
  flake,
}:
let
  pythonPackages = pkgs.python3.pkgs;
in
pythonPackages.buildPythonApplication (finalAttrs: {
  inherit pname;
  version =
    let
      pyprojectData = pkgs.lib.trivial.importTOML "${finalAttrs.src}/pyproject.toml";
    in
    pyprojectData.project.version;

  src = flake;
  pyproject = true;

  build-system = with pythonPackages; [
    setuptools
    setuptools-scm
  ];
  dependencies = with pythonPackages; [
    dulwich
    python-dateutil
    pyyaml
    semver
    wcwidth
  ];
})
