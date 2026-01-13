# SPDX-License-Identifier: CC0-1.0
# SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
{
  flake,
  inputs,
  pkgs,
  pname,
}:
let
  nixosModule =
    {
      config,
      lib,
      pkgs,
      ...
    }:
    {
      nix.settings = {
        experimental-features = [
          "nix-command"
          "flakes"
        ];
        # The Nix package manager should never have to access the Internet
        # while this test is running (other parts of this test do need to
        # access the Internet, though). Disabling substitution makes it less
        # likely that the Nix package manager will try to access the Internet.
        substitute = false;
      };
      environment.etc =
        let
          defaultDevShell = flake.devShells."${config.nixpkgs.hostPlatform.system}".default;
        in
        {
          thisFlake.source = flake;
          # This next part makes it so that we can run “nix develop” without
          # having to access the Internet.
          evaluationDependency1.source = inputs.blueprint;
          evaluationDependency2.source = inputs.nixpkgs;
          evaluationDependency3.source = inputs.jasons-nix-flake-style-guide;
          evaluationDependency4.source = inputs.nixpkgsUnstable;
          prebuiltDerivation1.source = defaultDevShell;
          prebuiltDerivation2.source = defaultDevShell.inputDerivation;
        };
      users.users.testUser = {
        isNormalUser = true;
        extraGroups = [ "networkmanager" ];
      };
      # We enable NetworkManager so that we can use nmcli.
      networking.networkmanager.enable = true;
      # We’re putting the bulk of the test code inside a systemd service so
      # that we can make the test code depend on network-online.target. If the
      # test script is run in an environment that does not have access to the
      # Internet, then the test script will not work properly.
      systemd.services.test-dev-shell-pre-commit-dependencies = {
        wants = [ "network-online.target" ];
        after = [ "network-online.target" ];
        wantedBy = [ "default.target" ];
        serviceConfig = {
          RemainAfterExit = true;
          TimeoutStartSec = "infinity";
          User = "testUser";
          # Originally, this systemd service only used ExecStart. Now, it uses
          # both ExecStartPre and ExecStart. The problem with using ExecStart
          # is that the service will become active while the ExecStart command
          # is still running. I don’t want that to happen. Instead, I want the
          # service to not be considered active until after the test script has
          # finished running. That way, I can detect if the script finished
          # successfully or not using the wait_for_unit() method.
          ExecStartPre =
            let
              nix = config.nix.package;
            in
            pkgs.resholve.writeScript "test-dev-shell-pre-commit-dependencies-script"
              {
                interpreter = lib.meta.getExe pkgs.bash;
                inputs = [
                  nix
                  pkgs.coreutils
                  pkgs.curl
                  pkgs.git
                  pkgs.networkmanager
                ];
                execer = [
                  "cannot:${lib.meta.getExe nix}"
                  # TODO: Try to get this one fixed upstream in resholve,
                  # binlore or Nixpkgs.
                  "cannot:${lib.meta.getExe pkgs.git}"
                  # TODO: Try to get this one fixed upstream in resholve,
                  # binlore or Nixpkgs.
                  "cannot:${pkgs.networkmanager}/bin/nmcli"
                ];
              }
              ''
                set -o errexit -o nounset -o pipefail

                # We should be able to activate the dev shell without having to
                # access the Internet. This next command disables Internet
                # access so that we can make sure that it’s possible to
                # activate the dev shell without Internet access.
                nmcli networking off
                # Normally, the trailing slash in “/etc/thisFlake/” would be
                # unnecessary. In this case though, /etc/thisFlake is a
                # symlink. Adding the trailing slash makes sure that we copy
                # the actual directory instead of the symlink.
                cp --no-preserve=mode --recursive /etc/thisFlake/ ~
                cd ~/thisFlake

                # pre-commit won’t work unless we do the following:
                git init --initial-branch=main
                git config user.name 'Connor Sample'
                git config user.email connor@example.edu
                git add .
                git commit --message 'Test commit'

                nix \
                  --offline \
                  develop \
                    --command \
                      echo \
                      '“nix develop” successfully ran without Internet access.'

                # Unfortunately, I don’t know how to get “pre-commit
                # install-hooks” to work without Internet access, so we have to
                # turn Internet access back on here.
                nmcli networking on
                nix --offline develop --command pre-commit install-hooks
              '';
          ExecStart = "${pkgs.coreutils}/bin/true";
        };
      };
      # This is required or else the machine will run out of resources.
      virtualisation = {
        memorySize = 8 * 1024;
        diskSize = 4 * 1024;
      };
    };
  nixosIntegrationTestModule = {
    name = pname;
    nodes.main = nixosModule;
    globalTimeout = 2 * 60 * 60;
    testScript = ''
      main.wait_for_unit("test-dev-shell-pre-commit-dependencies.service", None, 2 * 60 * 60)
    '';
  };
  nixosIntegrationTest = pkgs.testers.runNixOSTest nixosIntegrationTestModule;
in
# Normally, you would write “nixosIntegrationTest” here instead of
# “nixosIntegrationTest.driver”.
#
# If I were to write “nixosIntegrationTest” here, then you would run this test
# by building the derivation. While the test is running, the virtual machine
# would not be able to access the Internet.
#
# If I were to write “nixosIntegrationTest.driver” here, then you would run
# this test by building the derivation and then running
# "${lib.meta.getExe nixosIntegrationTest.driver}". While the test is running,
# the virtual machine would be able to access the Internet.
#
# I chose to write “nixosIntegrationTest.driver” here because this test needs
# an Internet connection.
nixosIntegrationTest.driver
