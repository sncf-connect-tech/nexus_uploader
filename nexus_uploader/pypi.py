#
# Copyright (C) 2016 VSCT  
#
# Licensed under the Apache License, Version 2.0 (the "License"); 
# you may not use this file except in compliance with the License.  
# You may obtain a copy of the License at 
#
# http://www.apache.org/licenses/LICENSE-2.0  
#
# Unless required by applicable law or agreed to in writing, software  
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
# See the License for the specific language governing permissions and 
# limitations under the License. 
#

"Code to interact with Pypi"

import requests


class PypiQueryError(Exception):
    pass

def get_package_release_from_pypi(pkg_name, version):
    """
    No classifier-based selection of Python packages is currently implemented: for now we don't fetch any .whl or .egg
    Eventually, we should select the best release available, based on the classifier & PEP 425.
    E.g. a wheel when available but NOT for tornado 4.3 for example, where available wheels are only for Windows.
    Note also that some packages don't have .whl distributed, e.g. https://bugs.launchpad.net/lxml/+bug/1176147
    """
    matching_releases = get_package_releases_matching_version(pkg_name, version)
    src_releases = [release for release in matching_releases if release['python_version'] == 'source']
    if not src_releases:
        raise PypiQueryError('No source distribution found for package {} version {}'.format(pkg_name, version))
    for release in src_releases:
        release['classifier'], release['extension'] = extract_classifier_and_extension(pkg_name, release['filename'])
    try:  # we return the release with the most generic classifier if there is one
        return next(release for release in src_releases if release['classifier'] == 'py2.py3-none-any')
    except StopIteration:
        return src_releases[0]

def get_package_releases_matching_version(pkg_name, version):
    releases = get_package_releases(pkg_name)
    if version not in releases:
        raise PypiQueryError('Version {} of package {} not found in Pypi. Available versions: {}', version, pkg_name, ','.join(releases.keys()))
    return releases[version]

def get_package_releases(pkg_name):
    response = requests.get('http://pypi.python.org/pypi/{}/json'.format(pkg_name))
    response.raise_for_status()
    return response.json()['releases']

def extract_classifier_and_extension(pkg_name, filename):
    """
    Returns a PEP425-compliant classifier (or 'py2.py3-none-any' if it cannot be extracted),
    and the file extension
    """
    basename, _, extension = filename.rpartition('.')
    if extension == 'gz' and filename.endswith('.tar.gz'):
        extension = 'tar.gz'
        basename = filename[:-7]
    if basename == pkg_name or basename[len(pkg_name)] != '-':
        return 'py2.py3-none-any', extension
    basename = basename[len(pkg_name)+1:]
    classifier_parts = basename.split('-')
    if len(classifier_parts) < 3:
        return 'py2.py3-none-any', extension
    if len(classifier_parts) == 3:
        _, _, classifier_parts[0] = classifier_parts[0].rpartition('.')
    return '-'.join(classifier_parts[-3:]), extension

