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
      identify
      python-dateutil
      pyyaml
      semver
      wcwidth
    ];
    # pythonPackages.identity depends on pythonPackages.pytestCheckHook [1]. As a
    # result, anything which depends on pythonPackages.identity also depends on
    # pythonPackages.pytestCheckHook. When a Python package depends on
    # pythonPackages.pytestCheckHook, Nixpkgs will automatically use pytest to
    # run the package’s tests during the package’s build process [2]. Jason’s
    # Pre-commit Hooks doesn’t have any tests so pytest will fail if we try to
    # run it here. We set dontUsePytestCheck to true here in order to prevent
    # that from happening.
    #
    # editorconfig-checker-disable
    # [1]: <https://github.com/NixOS/nixpkgs/blob/93108a538f079596c9a16c72cf03e9322782b6dd/pkgs/development/python-modules/identify/default.nix#L27>
    # [2]: <https://github.com/NixOS/nixpkgs/blob/93108a538f079596c9a16c72cf03e9322782b6dd/doc/languages-frameworks/python.section.md#using-pytestcheckhook-using-pytestcheckhook>
    # editorconfig-checker-enable
    dontUsePytestCheck = true;
  }
)
