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

import requests
from distutils.command.upload import upload as PypiUploadCmd
from distutils.errors import DistutilsOptionError

# Documentation for this pattern: https://docs.python.org/3/distutils/extending.html
class NexusUploadCmd(PypiUploadCmd):
    user_options = PypiUploadCmd.user_options + [
        ('username=', None, 'HTTP BasicAuth username to upload to your Sonatype Nexus'),
        ('password=', None, 'HTTP BasicAuth password to upload to your Sonatype Nexus'),
    ]

    def upload_file(self, command, pyversion, filename): # pylint: disable=unused-argument
        if not self.username or not self.password:
            raise DistutilsOptionError('--username and --password parameters are both required, either passed as CLI parameters or defined in .pypirc')
        extension = 'tar.gz' if filename.endswith('.tar.gz') else filename.rpartition('.')[-1]
        platforms = self.distribution.get_platforms()
        if platforms == ['UNKNOWN']:
            platforms = ['py2.py3-none-any']
        for platform in platforms:
            artifact_url = '{base_url}/{name}/{version}/{name}-{version}-{classifier}.{extension}'.format(
                    name=self.distribution.get_name(), version=self.distribution.get_version(),
                    base_url=self.repository, classifier=platform, extension=extension)
            print('Uploading to', artifact_url)
            with open(filename, 'rb') as artifact_binary:
                response = requests.post(artifact_url, data=artifact_binary, auth=(self.username, self.password))
                if 400 <= response.status_code < 600:
                    raise requests.HTTPError(str(response.status_code) + '\n' + response.text)
