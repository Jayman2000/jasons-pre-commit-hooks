# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{ pkgs, flake }:
let
  pythonPackages = pkgs.python3.pkgs;
in
pythonPackages.buildPythonApplication {
  pname = "jasons-pre-commit-hooks";
  # TODO: This doesn’t match the version number used by the Python
  # distribution package. I don’t know how to make this version number
  # match that version number.
  version = "0.dev${flake.lastModifiedDate}";
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
}
