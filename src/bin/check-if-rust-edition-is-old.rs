// SPDX-License-Identifier: CC0-1.0
// SPDX-FileCopyrightText: 2026 Jason Yundt <jason@jasonyundt.email>
use std::fs::canonicalize;
use std::option::Option;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

use cargo::core::SourceId;
use cargo::core::features::Edition;
use cargo::core::manifest::EitherManifest;
use cargo::util::context::GlobalContext;
use cargo::util::toml::read_manifest;
use clap::Parser;

#[derive(Parser)]
#[command(about)]
/// Emits an error for Cargo.toml files that don’t use the latest Rust
/// edition.
struct Cli {
    /// Path to a Cargo.toml file. Can be specified multiple times.
    path: Vec<PathBuf>,
}

fn paths() -> Vec<PathBuf> {
    let cli = Cli::parse();
    if cli.path.is_empty() {
        vec!["Cargo.toml".into()]
    } else {
        cli.path
    }
}

fn has_at_least_one_problem(
    global_context: &GlobalContext,
    path: &Path,
) -> bool {
    println!("Processing {path:#?}…");
    let absolute_path = match canonicalize(&path) {
        Ok(absolute_path) => absolute_path,
        Err(error) => {
            eprintln!(
                "ERROR: Failed to turn path {path:#?} into an absolute \
                path. Full error: {error:#?}"
            );
            return true;
        }
    };
    let source_id = match SourceId::for_manifest_path(&absolute_path) {
        Ok(source_id) => source_id,
        Err(error) => {
            eprintln!(
                "ERROR: Failed to create SourceId for \
                {absolute_path:#?}. Full error: {error:#?}"
            );
            return true;
        }
    };
    match read_manifest(&absolute_path, source_id, global_context) {
        Ok(either_manifest) => match either_manifest {
            EitherManifest::Real(manifest) => {
                let edition = manifest.edition();
                if edition != Edition::LATEST_STABLE {
                    eprintln!(
                        "{:#?} uses Rust {} edition. The latest stable \
                        Rust edition is Rust {}.",
                        absolute_path,
                        edition,
                        Edition::LATEST_STABLE
                    );
                    return true;
                }
            }
            EitherManifest::Virtual(_) => {
                eprintln!(
                    "ERROR: check-if-rust-edition-is-old does not \
                    support virtual manifests yet."
                );
                return true;
            }
        },
        Err(error) => {
            eprintln!(
                "ERROR: Failed to process {absolute_path:#?} as a \
                Cargo manifest. Full error: {error:#?}"
            );
            return true;
        }
    };
    println!("{path:#?} uses the latest Rust edition.");
    false
}

fn main() -> ExitCode {
    let global_context = match GlobalContext::default() {
        Ok(global_context) => global_context,
        Err(error) => {
            eprintln!(
                "ERROR: Failed to create a Cargo GlobalContext. Full \
                error: {error:#?}"
            );
            return ExitCode::FAILURE;
        }
    };
    let mut any_problems = false;
    for path in paths() {
        any_problems = has_at_least_one_problem(&global_context, &path)
            || any_problems
    }
    if any_problems {
        return ExitCode::FAILURE;
    };
    println!(
        "All of the specified Cargo.toml files use the latest Rust \
        edition."
    );
    ExitCode::SUCCESS
}
