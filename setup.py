#!/usr/bin/env python

import io, sys
from os import path
from setuptools import setup, find_packages

version = '1.0.14'
setup_requires = []

if 'nexus_upload' in sys.argv:
    sys.argv.remove('nexus_upload')
    setup_requires.append('nexus_uploader')

if '--snapshot' in sys.argv:
    sys.argv.remove('--snapshot')
    version += '-SNAPSHOT'

parent_dir = path.abspath(path.dirname(__file__))

# Using .rst as long as Markdown is not properly supported by pypi/warehouse :( -> https://github.com/pypa/warehouse/issues/869
with io.open(path.join(parent_dir, 'README.rst'), encoding='utf-8') as readme_file:
    rst_readme = readme_file.read()

def md2rst(md_lines):
    'Only converts headers'
    lvl2header_char = {1: '=', 2: '-', 3: '~'}
    for md_line in md_lines:
        if md_line.startswith('#'):
            header_indent, header_text = md_line.split(' ', 1)
            yield header_text
            header_char = lvl2header_char[len(header_indent)]
            yield header_char * len(header_text)
        else:
            yield md_line

with io.open(path.join(parent_dir, 'CHANGELOG.md'), encoding='utf-8') as changelog_file:
    md_changelog = changelog_file.read()
rst_changelog = '\n'.join(md2rst(md_changelog.splitlines()))

with io.open(path.join(parent_dir, 'requirements.txt')) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='nexus_uploader',
    description='CLI tool to upload Python packages listed in a requirements.txt file into a Sonatype Nexus (from Pypi), and return the list of the artifact URLs',
    long_description=rst_readme + '\n\n' + rst_changelog,
    author='Lucas Cimon',
    author_email='lucas.cimon+pypi@@gmail.com',
    url='http://github.com/voyages-sncf-technologies/nexus_uploader',
    install_requires=requirements,
    packages=find_packages(),
    version=version,
    setup_requires=setup_requires,
    zip_safe=True,  # http://peak.telecommunity.com/DevCenter/setuptools#setting-the-zip-safe-flag
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    keywords='nexus artifacts packages upload requirements pip-compile',
    license='Apache License 2.0',
    include_package_data=True,  # Active la prise en compte du fichier MANIFEST.in
    entry_points={
        'console_scripts': ['pyRequirements2nexus = nexus_uploader.pyrequirements2nexus:main'],
        'distutils.commands': ['nexus_upload = nexus_uploader.nexus_upload_cmd:NexusUploadCmd'],
    },
)
