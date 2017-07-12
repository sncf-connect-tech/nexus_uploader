# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [1.0.14] - 2017-12-07
### Fixed
- Tuple unpacking issue on py3.5 for fixed-version requirements

## [1.0.13] - 2017-07-03
### Fixed
- The resolver now handles properly uppercase versions (like X.Y-SNAPSHOT)

## [1.0.12] - 2017-07-03
### Fixed
- `Changelog.md` wasn't included in tarball (due to `MANIFEST.in`)

## [1.0.10] - 2017-07-03
### Fixed
- a bug introduced in v1.0.9: `piptools.exceptions.UnsupportedConstraint: pip-compile does not support URLs as packages, unless they are editable`
- changelog rendering in Pypi rst description

## [1.0.9] - 2017-06-30
### Fixed
- Upgrading pip-tools dependency to 1.9.0 to include commit b8043be (support for pip 8.1.2) -> https://github.com/voyages-sncf-technologies/nexus_uploader/commit/38f031b
- Fixing support for classifiers to be able to only retrieve Python2-compatible pkgs -> https://github.com/voyages-sncf-technologies/nexus_uploader/commit/35e78fc
- Fixing repository files permissions -> https://github.com/voyages-sncf-technologies/nexus_uploader/commit/38f031b

### Added
- Made the lib compatible for Python 2.7 -> https://github.com/voyages-sncf-technologies/nexus_uploader/commit/5833c5f
- More tests

## [1.0.8] - 2016-12-13
### Added
- `--pypi-json-api-url` parameter : source of Python packages to feed the Nexus with
- `--allowed-pkg-classifiers` parameter : when no `source` release is available for a given `package==version`,
  select a package matching on of those classifiers as a 2nd choice
  (introduced to handle `docutils==0.13.1` that only exist as a wheel).

### Changed
- The `--allowed-pkg-classifiers` comes with a default value of `py3-none-any` changing the existing behaviour.
  To keep the previous behaviour you'll need to pass an empty value to this parameter.
  An `PypiQueryError` will then be raised if no `source` package is available.
