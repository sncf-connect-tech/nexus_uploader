#!/bin/bash

# Wrapper around pyRequirements2nexus to be used in a Jenkins build job.
# Consume requirements.txt in the current directory.

# USAGE:
#   source python_packaging_nexus_credentials.sh
#   ./jenkins-install-python-requirements.sh anaconda3-2.4.1_included_packages.txt

set -o pipefail -o errexit -o nounset -o xtrace

SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")

export no_proxy=nexus

DEFAULTS_PKGS_FILE=${1?'Missing required parameter'}

echo VIRTUAL_ENV=${VIRTUAL_ENV:-}

if ! [ -s requirements.txt ]; then
    echo 'Empty or missing requirements.txt'
    exit 1
fi

pip install --upgrade nexus_uploader

pyRequirements2nexus --debug --nexus-url=http://nexus --artifact-group 'com.vsct.pip' --default-packages "$DEFAULTS_PKGS_FILE" --in-reqfile requirements.txt --out-reqfile nexus-requirements.txt
