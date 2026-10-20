// SPDX-License-Identifier: CC0-1.0
// SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
//
// TODO: Test on Windows.
use std::env;
use std::ffi::OsString;
use std::fs::OpenOptions;
use std::fs::Permissions;
use std::include_bytes;
use std::io::prelude::Write;
use std::path::PathBuf;
use std::process::ExitCode;

#[cfg(unix)]
use std::os::unix::fs::{OpenOptionsExt, PermissionsExt};

use duct::cmd;
use tempfile::Builder;

#[cfg(unix)]
const PERMISSIONS_MODE: u32 = 0o700;

fn write_cargo_upgrade_executable(path: PathBuf) -> ExitCode {
    let mut open_options = OpenOptions::new();
    open_options.write(true).create_new(true);

    #[cfg(unix)]
    open_options.mode(PERMISSIONS_MODE);

    let mut file = match open_options.open(&path) {
        Ok(new_file) => new_file,
        Err(error) => {
            // TODO: Test this error.
            eprintln!(
                "ERROR: Failed to create new file at {path:#?}. Full \
                error: {error:#?}"
            );
            return ExitCode::FAILURE
        }
    };

    // TODO: Is there anyway to just use ORIGINAL_CARGO_UPGRADE_PATH_STR
    // here?
    println!("TODO: Remove this test line: {path:#?}");
    match file.write_all(include_bytes!(env!("CARGO_BIN_FILE_CARGO_EDIT_cargo-upgrade"))) {
        Ok(_) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!(
                "ERROR: Failed to write to file at {path:#?}. Full \
                error: {error:#?}"
            );
            ExitCode::FAILURE
        }
    }
}

fn main() -> ExitCode {
    #[cfg(windows)]
    const CARGO_UPGRADE_FILE_NAME: &str = "cargo-upgrade.exe";

    #[cfg(not(windows))]
    const CARGO_UPGRADE_FILE_NAME: &str = "cargo-upgrade";

    let mut temp_builder = Builder::new();
    temp_builder.prefix("cargo-upgrade-shim-");

    #[cfg(unix)]
    temp_builder.permissions(Permissions::from_mode(PERMISSIONS_MODE));

    let temporary_directory = match temp_builder.tempdir() {
        Ok(directory) => directory,
        Err(error) => {
            // TODO: Test this error.
            eprintln!("ERROR: Failed to create temporary directory. Full error: {error:#?}");
            return ExitCode::FAILURE
        }
    };

    let new_cargo_upgrade_path = temporary_directory.path().join(CARGO_UPGRADE_FILE_NAME);
    // TODO: Remove the & on the next line.
    if write_cargo_upgrade_executable(new_cargo_upgrade_path) != ExitCode::SUCCESS {
        return ExitCode::FAILURE;
    }

    let original_path = match env::var_os("PATH") {
        Some(value) => value,
        None => OsString::new()
    };
    let mut new_path_list = vec![temporary_directory.path().into()];
    new_path_list.extend(env::split_paths(&original_path));
    let new_path = match env::join_paths(&new_path_list) {
        Ok(value) => value,
        // TODO: Test this error.
        Err(error) => {
            eprintln!(
                "ERROR: Failed to turn new_path_list in a PATH \
                environment variable value. Value of new_path_list: \
                {new_path_list:#?}\nFull error: {error:#?}"
            );
            return ExitCode::FAILURE
        }
    };

    let command = cmd("cargo", env::args_os().skip(1)).env("PATH", new_path);
    let cargo_output = match command.run() {
        Ok(output) => output,
        Err(error) => {
            // TODO: Test this error.
            eprintln!(
                "ERROR: Failed to run to cargo. Full error: {error:#?}"
            );
            return ExitCode::FAILURE
        }
    };

    match cargo_output.status.code() {
        Some(exit_code) => ExitCode::from(exit_code.to_le_bytes()[0]),
        None => {
            // TODO: Test this error?
            eprintln!(
                "ERROR: Cargo finished running, but did not provide an \
                exit code."
            );
            ExitCode::FAILURE
        }
    }
}
