#!/usr/bin/env python

import sys
from os import path
from setuptools import setup, find_packages

version = '1.0.5'
setup_requires = []

if 'nexus_upload' in sys.argv:
    sys.argv.remove('nexus_upload')
    setup_requires.append('nexus_uploader')

if '--snapshot' in sys.argv:
    sys.argv.remove('--snapshot')
    version += '-SNAPSHOT'

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as long_desc_file:
    long_description = long_desc_file.read()

with open(path.join(here, 'requirements.txt')) as requirements_file:
    requirements = requirements_file.readlines()

setup(
    name='nexus_uploader',
    description='CLI tool to upload Python packages listed in a requirements.txt file into a Sonatype Nexus (from Pypi), and return the list of the artifact URLs',
    long_description=long_description,
    author='Lucas Cimon',
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
