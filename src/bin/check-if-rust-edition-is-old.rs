// SPDX-License-Identifier: CC0-1.0
// SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
// TODO: Test on Windows.
use std::fs::{canonicalize, read_to_string};
use std::option::Option;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use cargo::core::features::Edition;
use cargo_util_schemas::manifest::{InheritableString, TomlManifest};
use clap::Parser;

#[derive(Parser)]
#[command(about)]
/// Emits an error for Cargo.toml files that don’t use the latest Rust
/// edition.
struct Cli {
    /// Path to a Cargo.toml file. Can be specified multiple times.
    path: Vec<PathBuf>,
}

fn raw_paths() -> Vec<PathBuf> {
    let cli = Cli::parse();
    if cli.path.is_empty() {
        vec!["Cargo.toml".into()]
    } else {
        cli.path
    }
}

fn has_problems(path: &Path) -> bool {
    let file_contents = match read_to_string(path) {
        Ok(contents) => contents,
        Err(error) => {
            eprintln!(
                "Failed to read file {path:#?}. Full error: {error:#?}"
            );
            return true;
        }
    };
    let manifest: TomlManifest = match toml::from_str(&file_contents) {
        Ok(manifest) => manifest,
        Err(error) => {
            eprintln!(
                "{path:#?} does not appear to be a valid Cargo.toml \
                file. Full Error: {error:#?}"
            );
            return true;
        }
    };
    let package = match manifest.package {
        Some(package) => package,
        None => {
            eprintln!("{path:#?} has no package table.");
            return true;
        }
    };
    let edition = match package.edition {
        Some(inheritable_string) => match inheritable_string {
            InheritableString::Value(edition) => edition,
            InheritableString::Inherit(_) => {
                println!(
                    "{path:#?} inherits its edition from the \
                    workspace. This is OK as long as you included \
                    workspace’s Cargo.toml file in the list of paths \
                    to process (command-line arguments)."
                );
                return false;
            }
        },
        None => {
            eprintln!("{path:#?} does not have a package.edition key.");
            return true;
        }
    };
    let latest_stable_edition = Edition::LATEST_STABLE.to_string();
    if edition == latest_stable_edition {
        false
    } else {
        eprintln!(
            "{path:#?} uses edition {edition}. The latest stable \
            edition is {latest_stable_edition}."
        );
        true
    }
}

fn main() -> ExitCode {
    let mut any_problems = false;
    for raw_path in raw_paths() {
        println!("Processing {raw_path:#?}…");
        // We call canonicalize here in order to avoid Windows’s
        // MAX_PATH limitations [1].
        //
        // editorconfig-checker-disable
        // [1]: <https://doc.rust-lang.org/1.95.0/std/fs/fn.canonicalize.html>
        // editorconfig-checker-enable
        let path = if cfg!(windows) {
            match canonicalize(&raw_path) {
                Ok(absolute_path) => absolute_path,
                Err(error) => {
                    eprintln!(
                        "Failed to turn path {raw_path:#?} into an \
                        absolute path. Full error: {error:#?}"
                    );
                    any_problems = true;
                    raw_path
                }
            }
        } else {
            raw_path
        };
        // TODO: has_problems() only gets called once because of or
        // short-circuting. We should probably switch back to using
        // read_manifest.
        any_problems = any_problems || has_problems(&path)
    }
    if any_problems {
        ExitCode::FAILURE
    } else {
        println!(
            "All of your Cargo.toml files are using the latest Rust \
            edition."
        );
        ExitCode::SUCCESS
    }
}
