# Changelog

All notable changes of the ECOA XML Validation Tool (`EXVT`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

NA

## [1.1.0] - 2023-10-02

### Added

- Cyclic references between libraries detected in an ECOA project.
- The tool checks that the event associated with a trigger instance does not have any parameters.

### Changed

- The tool can now accepts an ECOA project file which contains backslaches.

### Fixed

- Typos fixed in some error messages.
- The tool no longer crashed when certain mandatory field are not filled. The project is now considered to have errors instead.
