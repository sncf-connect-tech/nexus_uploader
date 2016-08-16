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

"Code to interact with Sonatype Nexus"

import logging, re, requests

from .pypi import get_package_release_from_pypi
from .utils import aslist


logger = logging.getLogger(__name__)


class NexusRepositoryClient:
    """
    Heavily inspired by stardust85/repositorytools repository.NexusRepositoryClient._upload_artifact
    API details: https://repository.sonatype.org/nexus-restlet1x-plugin/default/docs/rest.html
    """
    def __init__(self, base_url, repo_id, artifact_group, auth):
        self.base_url = base_url
        self.repo_id = repo_id
        self.artifact_group = artifact_group
        self.auth = auth
        self._session = requests.session()

    def upload_from_pypi_if_need_be(self, pkg_name, pkg_version):
        logger.debug('Checking for Python package %s version %s in Nexus', pkg_name, pkg_version)
        matching_artifacts = self.find_artifacts(pkg_name, pkg_version)
        if matching_artifacts:
            logger.info('Skipping Python package %s version %s - the following artifacts are already in Nexus : %s',
                pkg_name, pkg_version, ','.join(url.split('/')[-1] for url in matching_artifacts))
            if len(matching_artifacts) > 1:
                raise NotImplementedError('Classifier-based selection of Python packages is not implemented yet.\n'
                                          'Several matching artifacts found in Nexus: {}'.format(matching_artifacts))
            return matching_artifacts[0]
        else:
            logger.debug('Retrieving release for Python package %s version %s from Pypi', pkg_name, pkg_version)
            pkg_release = get_package_release_from_pypi(pkg_name, pkg_version)

            response = requests.get(pkg_release['url'])
            response.raise_for_status()
            pkg_binary = response.content

            logger.debug('Uploading Python package %s version %s to Nexus', pkg_name, pkg_version)
            artifact_url = self.get_artifact_url(pkg_name, pkg_version, pkg_release['classifier'], pkg_release['extension'])
            self.upload_artifact(artifact_url, pkg_binary)
            return artifact_url

    @staticmethod
    def get_artifact_filename(name, version, classifier, extension):
        return '{name}-{version}-{classifier}.{extension}'.format(name=name, version=version, classifier=classifier, extension=extension)

    def get_artifact_url_dir(self, name, version):
        return '{hostname}/content/repositories/{repo_id}/{group}/{name}/{version}'.format(
            hostname=self.base_url, repo_id=self.repo_id, group=self.artifact_group, name=name, version=version)

    def get_artifact_url(self, pkg_name, version, classifier, extension):
        artifact_nexus_filename = self.get_artifact_filename(pkg_name, version, classifier, extension)
        return '{}/{}'.format(self.get_artifact_url_dir(pkg_name, version), artifact_nexus_filename)

    def find_artifacts(self, name, version):
        url = self.get_artifact_url_dir(name, version)
        response = self._session.get(url)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        return self._extract_artifacts_url(url, response.text)

    @staticmethod
    def pkg_name_version_from_artifact_url(artifact_url):
        "Returns a (pkg_name, pkg_version) tuple"
        return artifact_url.split('/')[-3:-1]

    def append_egg_hash_if_nexus_url(self, url):
        if url.startswith(self.base_url) and '#egg=' not in url:
            return url + '#egg={}=={}'.format(*self.pkg_name_version_from_artifact_url(url))
        return None

    @staticmethod
    @aslist
    def _extract_artifacts_url(base_url, nexus_html_listing):
        # OK, regex-parsing HTML is uglyyy, but there is no need to introduce an external dependency to beautifulsoup4 just for this
        for url in re.findall(r' href="(' + base_url + r'/[^"]+)"', nexus_html_listing):
            if not (url.endswith('.pom') or url.endswith('.md5') or url.endswith('.sha1')):
                yield url

    def upload_artifact(self, artifact_url, artifact_binary):
        self._session.post(artifact_url, data=artifact_binary, auth=self.auth).raise_for_status()
