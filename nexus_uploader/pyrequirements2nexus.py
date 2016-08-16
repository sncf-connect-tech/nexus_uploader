#!/usr/bin/env python3

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

# INSTALL: pip install pip-tools requests (the former is needed to get the pip-compile command)
# AUTHOR: Lucas Cimon

import argparse, getpass, logging, os, sys
from urllib.parse import urlparse
from .nexus import NexusRepositoryClient
from .pip_compile import pip_compile
from .requirements import read_requirements, requirements2reqfile_lines, subst_editable_pkg_fallback, filter_out_provided_requirements


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, stream=sys.stderr,
            format="%(asctime)s - pid:%(process)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(message)s")
    nexus_client = NexusRepositoryClient(base_url=args.nexus_url, repo_id=args.repo_id, artifact_group=args.artifact_group.replace('.', '/'), auth=(args.user, args.password))
    with open(args.in_reqfile, 'r') as in_reqfile_content:
        requirements = read_requirements(in_reqfile_content.readlines())
    requirements = [subst_editable_pkg_fallback(req) for req in requirements]
    requirements = read_requirements(pip_compile(requirements2reqfile_lines(requirements), urlparse(nexus_client.base_url).netloc, nexus_client.append_egg_hash_if_nexus_url))
    if args.default_packages:
        with open(args.default_packages, 'r') as default_pkgs_file:
            requirements = filter_out_provided_requirements(requirements, read_requirements(default_pkgs_file.readlines()))
    with open(args.out_reqfile, 'w') as out_reqfile_content:
        for req_type, req_info in requirements:
            if req_type == 'url':
                requirement_url, comment = req_info
                out_reqfile_content.write(requirement_url + (' # ' + comment if comment else '') + '\n')
            elif req_type == 'version-locked':
                pkg_name, pkg_version, comment = req_info
                nexus_artifact_url = nexus_client.upload_from_pypi_if_need_be(pkg_name, pkg_version)
                out_reqfile_content.write(nexus_artifact_url + (' # ' + comment if comment else '') + '\n')

def parse_args(argv):
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--nexus-url', required=True, help=' ')
    parser.add_argument('--artifact-group', required=True, help=' ')
    parser.add_argument('--repo-id', default='pip', help=' ')
    parser.add_argument('--default-packages', help='File containing a requirements.txt-style list of Python packages already included in the base environment')
    parser.add_argument('--user', help='A prompt will ask for your password - Else use environment variables REPOSITORY_USER / REPOSITORY_PASSWORD')
    parser.add_argument('--in-reqfile', default='requirements.txt')
    parser.add_argument('--out-reqfile', default='nexus-requirements.txt')
    # Subparsers could easily be added here, to enumerate artifacts / only retrieve a package release from Pypi / onlyu upload an artifact to nexus... but YAGNI prevails
    args = parser.parse_args(argv)
    if args.user:
        args.password = getpass.getpass(prompt='Please enter password for user {} : '.format(args.user))
    else:
        if 'REPOSITORY_USER' not in os.environ or 'REPOSITORY_PASSWORD' not in os.environ:
            parser.error('Repository user not specified. Please use the interactive --user option or define the environment variables REPOSITORY_USER / REPOSITORY_PASSWORD')
        args.user = os.environ['REPOSITORY_USER']
        args.password = os.environ['REPOSITORY_PASSWORD']
    return args

if __name__ == '__main__':
    main()
