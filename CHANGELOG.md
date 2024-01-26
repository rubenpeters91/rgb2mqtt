# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2024-01-26

### Fixed
- Added a separate `rgb2mqtt-gui-run` gui-script, so using the normal `rgb2mqtt-run` script now functions as a console script. This makes it easier to debug the run script, since stdout in a gui-script is lost.
The gui-script is only used for auto-start, which prevents a terminal popup on Windows.

## [1.0.1] - 2024-01-25

### Fixed
- Fixed an error where the config would not be written to disk when there was no config present

### Added
- Added unit tests for device class
- Added linting and unit tests pipelines for GitHub
- Added verbose option to run script, which prints the logging to stdout

### Changed
- Using `ruff` as linter instead of flake8

## [1.0.0]

- Initial release

