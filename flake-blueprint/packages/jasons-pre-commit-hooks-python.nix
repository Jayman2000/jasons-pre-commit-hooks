# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2025–2026 Jason Yundt <jason@jasonyundt.email>
{ pname, pkgs }:
let
  pythonPackages = pkgs.python3.pkgs;
in
pythonPackages.buildPythonApplication (
  finalAttrs:
  let
    inherit (pkgs.lib.strings) escapeNixString;
    pyprojectData = pkgs.lib.trivial.importTOML "${finalAttrs.src}/pyproject.toml";
  in
  {
    pname =
      assert pkgs.lib.asserts.assertMsg (pname == pyprojectData.project.name)
        "pname (${escapeNixString pname}) and Python distribution package name (${escapeNixString pyprojectData.project.name}) don’t match";
      pname;
    inherit (pyprojectData.project) version;

    src =
      let
        root = ../..;
      in
      pkgs.lib.fileset.toSource {
        inherit root;
        fileset = pkgs.lib.fileset.union (root + /pyproject.toml) (root + /jasons_pre_commit_hooks_python);
      };
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
)
