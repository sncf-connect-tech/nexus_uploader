#!/usr/bin/env python

import os, sys
from setuptools import setup, find_packages

version = '1.0.2'
setup_requires = []

if 'nexus_upload' in sys.argv:
    sys.argv.remove('nexus_upload')
    setup_requires.append('nexus_uploader')

if '--snapshot' in sys.argv:
    sys.argv.remove('--snapshot')
    version += '-SNAPSHOT'

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')) as file_requirements:
    requirements = file_requirements.readlines()

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = open('README.md').read()

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
