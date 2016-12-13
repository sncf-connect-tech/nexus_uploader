# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/) 
and this project adheres to [Semantic Versioning](http://semver.org/).

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
