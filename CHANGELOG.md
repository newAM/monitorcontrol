# Changelog
All notable changes to this project will be documented in this file, as of
2.1.1 when I started keeping a changelog in the first place (sorry).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html),
as of version 2.1.1.

## [Unreleased]
### Added
- Added support for python 3.10.

### Changed
- Updated pyudev from 0.22 to 0.23.
- Changed `get_vcp_capabilities()["inputs"]` from `List[str]` to `Union[InputSource, int]`.

### Removed
- Removed support for python 3.6 and 3.7.

### Fixed
- Increased the length limit for the capabilities string on Linux.
  - This fixes some occurrences of the "Capabilities string incomplete or too long" error.

## [2.5.1] - 2021-08-25
### Fixed
- Fixed a bug in capabilities parsing.

## [2.5.0] - 2021-06-26
### Added
- Added support for selecting input sources outside of the MCCS specification.

### Changed
- Changed the changelog format to keep a changelog.

## [2.4.2] - 2021-04-27
### Fixed
- Fixed an exception that occurred when getting the input source from a
  powered off monitor.

## [2.4.1] - 2021-04-10
### Fixed
- Fixed `get_input_source` failing for monitors that set the reserved byte.
- Fixed `get_input_source` returning a `str` instead of a `InputSource` as
  the type hint indicated.

## [2.4.0] - 2021-03-14
### Added
- Added `--monitor` optional argument to select a specific monitor for the command
- Added `--set-input-source` and `--get-input-source` to change monitor input source

## [2.3.0] - 2020-10-07
### Added
- Added `-v` / `--verbose` argument to the CLI.

### Fixed
- Fixed `AttributeError: 'LinuxVCP' object has no attribute 'logger'`

## [2.2.0] - 2020-10-04
### Added
- Added python 3.9 support.

### Fixed
- Disabled `VCPIOErrors` by default on Linux.

## [2.1.1] - 2020-09-12
### Fixed
- Fixed the `--version` command in the CLI.

### Added
- Added a changelog.


[Unreleased]: https://github.com/newAM/monitorcontrol/compare/2.5.1...HEAD
[2.5.1]: https://github.com/newAM/monitorcontrol/compare/2.5.0...2.5.1
[2.5.0]: https://github.com/newAM/monitorcontrol/compare/2.4.2...2.5.0
[2.4.2]: https://github.com/newAM/monitorcontrol/compare/2.4.1...2.4.2
[2.4.1]: https://github.com/newAM/monitorcontrol/compare/2.4.0...2.4.1
[2.4.0]: https://github.com/newAM/monitorcontrol/compare/2.3.0...2.4.0
[2.3.0]: https://github.com/newAM/monitorcontrol/compare/2.2.0...2.3.0
[2.2.0]: https://github.com/newAM/monitorcontrol/compare/2.1.1...2.2.0
[2.1.1]: https://github.com/newAM/monitorcontrol/releases/tag/2.1.1
