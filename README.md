[![](https://img.shields.io/voyages-sncf-technologies/v/nexus_uploader.svg?style=flat)](https://pypi.python.org/pypi/nexus_uploader)
[![](https://img.shields.io/voyages-sncf-technologies/l/nexus_uploader.svg?style=flat)](https://pypi.python.org/pypi/nexus_uploader)

Python tools to help with the development & deployment of company-private Python packages.

It was developped to use Sonatype Nexus as a private Pypi mirror (until [it supports this natively](https://issues.sonatype.org/browse/NEXUS-6037)),
but should be adaptable to any repository supporting artifact upload with HTTP.

It is composed of 2 distincts :

- `nexus_uploader` : a simple module to be used as a `setup_requires` entry in `setup.py`, in order to easily upload Python packages onto a Nexus.
- `pyRequirements2nexus` : a CLI tool to convert standard Python `requirements.txt` into `nexus-requirements.txt` files,
made of URLs pointing to installable packages that `pyRequirements2nexus` mirrored on your Nexus.

![](https://raw.githubusercontent.com/voyages-sncf-technologies/nexus_uploader/master/docs/PythonPackaging.png)

# Features

## nexus_uploader features

- easy integration in `setup.py`
- HTTP BasicAuth to connect to Sonatype Nexus

## pyRequirements2nexus features

- full dependency resolution of Python packages, working with both Pypi public ones & private ones on a Nexus
- to install packages, the end machine only require a connexion to the Nexus host, not to the Internet
- support `-e` editable packages in `requirements.txt`
- support package URL fallbacks as comments in `requirements.txt`
- a list of packages already included in the base environment can be specified (e.g. if you are using Anaconda), so that they will be excluded from the final `nexus-requirements.txt`

Limitations

- only support `==` version locking in `requirements.txt` (not `>=`).
This is intentional, to ensure package versions do not change unexpectedly.


# How to upload home-made Python packages to my Nexus ?

Here is a handy recipe you can put in your `setup.py` :

```
setup(
    ...
    setup_requires=['nexus_uploader']
)
```

Usage:
```
$ python setup.py sdist nexus_upload --repository http://nexus/content/repositories/Snapshots/com/vsct/my_project --username $REPOSITORY_USER --password $REPOSITORY_PASSWORD
```


## Important note

Contrary to `requirements.txt` files, there is no way to include URLs to dependencies in `setup.py` `install_requires` (nor `setup_requires`).
To work around this limitation, `pyrequirements2nexus` takes advantage of the deprecated "dependency_links" mechanism.
Using them, it is able to discover the full chain of Python packages dependencies, both from Pypi **AND** from your local Nexus.

To easily generate the "dependency_links.txt" in your Nexus-hosted private package out of your `requirements.txt`, use the following recipe in your its `setup.py` :
```
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')) as requirements_file:
    requirements = requirements_file.readlines()
    dependency_links = [req for req in requirements if req.startswith('http')]
    install_requires = [req for req in requirements if not req.startswith('http')]

setup(
    ...
    install_requires=install_requires,
    dependency_links=dependency_links,
)
```

Because "dependency_links" are not supported since [pip 1.6](https://github.com/pypa/pip/pull/1519/commits/95ac4c16f544dcc4282d2a4245aba0384f7e629a),
they will **NOT** be installed by `pip install` normal recursive dependency-retrieval algorithm.
You should always use the flat `nexus-requirements.txt` with `pip install`.


# pyRequirements2nexus usage

    pip install nexus_uploader
    pyRequirements2nexus --help


# Installation of nexus-requirements.txt on an end machine

    pip install --user --no-index --no-deps --no-cache-dir --upgrade --requirement nexus-requirements.txt


# Supported requirements.txt format

    http://nexus/content/repositories/repo_id/my/project/group/mypkgname/1.0/mypkgname-1.0-py2.py3-none-any.tar.gz
    nose==1.3.7   # -> transformed into an URL like this: http://nexus/content/repositories/repo_id/my/project/group/...
    -e ../my/relative/path  # http://nexus/content/repositories/...fallback_url...


# Contributing

[pre-commit hooks](http://pre-commit.com) installation:
```
pip install -r dev-requirements
pre-commit install
```

Unit tests:
```
PYTHONPATH=. py.test tests/
```

Smoke tests using Pypi:
```
PYTHONPATH=. ipython3 --pdb tests/smoke_test_extract_classifier_and_extension.py 200
```


# FAQ

## pip install - Download error on https://pypi.python.org / Couldn't find index page for

The stack trace :
```
Collecting http://nexus/content/repositories/pip/com/vsct/pip/jsonschema/2.5.1/jsonschema-2.5.1-py2.py3-none-any.tar.gz (from -r scripts/requirements.pip (line 12))
  Downloading http://nexus/content/repositories/pip/com/vsct/pip/jsonschema/2.5.1/jsonschema-2.5.1-py2.py3-none-any.tar.gz (50kB)
    Complete output from command python setup.py egg_info:
    Download error on https://pypi.python.org/simple/vcversioner/: [Errno -2] Name or service not known -- Some packages may not be found!
    Couldn't find index page for 'vcversioner' (maybe misspelled?)
    Download error on https://pypi.python.org/simple/: [Errno -2] Name or service not known -- Some packages may not be found!
    No local packages or download links found for vcversioner
```

Explanation : https://github.com/Julian/jsonschema/issues/276

Solution :
```
$ cat <<EOF > ~/.pydistutils.cfg
[easy_install]
allow_hosts = nexus
find_links = http://nexus/content/repositories/pip/com/vsct/pip/vcversioner/2.14.0.0/
EOF
```


## Tip for easily removing packages from your nexus

    pip install --user repositorytools
    export REPOSITORY_USER=...
    export REPOSITORY_PASSWORD=
    artifact delete http://nexus/content/repositories/pip/com/vsct/pip/ultrajson/1.35/ultrajson-1.35-macosx-10.6-intel.tar.gz


# ToDo

- Python 2 support
- detect if package releases on Pypi require gcc compilation (are they using setuptools/distutils `Extension` in `setup.py` ?)
- classifier-based selection of Python packages
- add support for md5 & sha1 upload/checks
