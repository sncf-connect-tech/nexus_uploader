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

'Code to interact with Pypi'

import requests

from .utils import aslist


class PypiQueryError(Exception):
    pass

def get_package_release_from_pypi(pkg_name, version, pypi_json_api_url, allowed_classifiers):
    """
    No classifier-based selection of Python packages is currently implemented: for now we don't fetch any .whl or .egg
    Eventually, we should select the best release available, based on the classifier & PEP 425: https://www.python.org/dev/peps/pep-0425/
    E.g. a wheel when available but NOT for tornado 4.3 for example, where available wheels are only for Windows.
    Note also that some packages don't have .whl distributed, e.g. https://bugs.launchpad.net/lxml/+bug/1176147
    """
    matching_releases = get_package_releases_matching_version(pkg_name, version, pypi_json_api_url)
    src_releases = [release for release in matching_releases if release['python_version'] == 'source']
    if src_releases:
        return select_src_release(src_releases, pkg_name, target_classifiers=('py2.py3-none-any',), select_arbitrary_version_if_none_match=True)
    if allowed_classifiers:
        return select_src_release(matching_releases, pkg_name, target_classifiers=allowed_classifiers)
    raise PypiQueryError('No source supported found for package {} version {}'.format(pkg_name, version))

def select_src_release(src_releases, pkg_name, target_classifiers, select_arbitrary_version_if_none_match=False):
    for release in src_releases:
        release['classifier'], release['extension'] = extract_classifier_and_extension(pkg_name, release['filename'])
    try:  # we return the release with the most generic classifier if there is one
        return next(release for release in src_releases if release['classifier'] in target_classifiers)
    except StopIteration:
        if select_arbitrary_version_if_none_match:
            return src_releases[0]

def get_package_releases_matching_version(pkg_name, version, pypi_json_api_url):
    releases = get_package_releases(pkg_name, pypi_json_api_url)
    if version not in releases:
        raise PypiQueryError('Version {} of package {} not found in Pypi. Available versions: {}', version, pkg_name, ','.join(releases.keys()))
    return releases[version]

def get_package_releases(pkg_name, pypi_json_api_url):
    response = requests.get(pypi_json_api_url.format(pkg_name))
    response.raise_for_status()
    return response.json()['releases']

def extract_classifier_and_extension(pkg_name, filename):
    """
    Returns a PEP425-compliant classifier (or 'py2.py3-none-any' if it cannot be extracted),
    and the file extension
    TODO: return a classifier 3-members namedtuple instead of a single string
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

@aslist
def filter_allowed_pkg_urls_for_classifiers(pkg_urls, allowed_pkg_classifiers):
    for pkg_url in pkg_urls:
        pkg_name, pkg_filename = pkg_url.split('/')[-3], pkg_url.split('/')[-1]
        classifier, _ = extract_classifier_and_extension(pkg_name, pkg_filename)
        if classifier in allowed_pkg_classifiers:
            yield pkg_url
