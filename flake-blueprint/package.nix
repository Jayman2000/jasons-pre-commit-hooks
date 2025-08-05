# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025 Jason Yundt <jason@jasonyundt.email>
{ pkgs, flake }:
let
  pythonPackages = pkgs.python3.pkgs;
in
pythonPackages.buildPythonApplication {
  pname = "jasons-pre-commit-hooks";
  version = "0.6.0";
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
