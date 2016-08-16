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

"Code to parse, write & filter the *requirements.txt files"

import logging, re
from .utils import aslist


logger = logging.getLogger(__name__)


class RequirementError(Exception):
    pass

@aslist
def read_requirements(reqfile_lines):
    for line in reqfile_lines:
        line = line.strip()
        if line and not line.startswith('#'):
            requirement, _, comment = line.partition(' #')
            requirement, comment = requirement.strip(), comment.strip()
            if re.search('^https?://', requirement):
                yield 'url', (requirement, comment)
            elif requirement.startswith('-e '):
                yield 'editable', (requirement[3:], comment.partition(' #')[0].strip())
            elif '==' in requirement:
                pkg_name, pkg_version = requirement.split('==')
                yield 'version-locked', (pkg_name.strip(), pkg_version.strip(), comment)
            else:
                raise RequirementError('Unsupported requirement format: {}'.format(line))

@aslist
def requirements2reqfile_lines(requirements):
    for req_type, req_info in requirements:
        if req_type == 'url':
            url, comment = req_info
            yield url + ' # ' + comment
        elif req_type == 'editable':
            local_path, comment = req_info
            yield '-e ' + local_path + ' # ' + comment
        elif req_type == 'version-locked':
            pkg_name, pkg_version, comment = req_info
            yield pkg_name + '==' + pkg_version + ' # ' + comment

def subst_editable_pkg_fallback(requirement):
    req_type, req_info = requirement
    if req_type != 'editable':
        return requirement
    local_path, comment = req_info
    if comment:
        if comment.startswith('http'):
            return 'url', (comment, '')
        if '==' in comment:
            pkg_name, pkg_version = comment.split('==')
            return 'version-locked', (pkg_name.strip(), pkg_version.strip(), '')
    raise RequirementError('Dependencies in editable mode must have a fallback: {}'.format(local_path))

@aslist
def filter_out_provided_requirements(requirements, provided_requirements):
    provided_requirements = {name: version for req_type, (name, version, comment) in provided_requirements if req_type == 'version-locked'}
    for req_type, req_info in requirements:
        if req_type != 'version-locked':
            yield req_type, req_info
            continue
        pkg_name, pkg_version, comment = req_info
        default_package_version = provided_requirements.get(pkg_name, None)
        if default_package_version:
            if default_package_version == pkg_version:
                logger.debug('Filtering out Python package %s version %s found in provided requirements', pkg_name, pkg_version)
                continue
            logger.warning(('Python package %s exist with version %s (not %s) in provided requirements :'
                            ' if this version match your needs, please use it instead of adding another dependency'),
                           pkg_name, default_package_version, pkg_version)
        yield 'version-locked', (pkg_name, pkg_version, comment)
