import json, os, tarfile

from pip._vendor.packaging.version import Version
from pip.index import FormatControl, Link
from pip.req import InstallRequirement
from pip.download import PipSession

from piptools.repositories.base import BaseRepository
from piptools.utils import as_tuple, make_install_requirement

import pytest


def pytest_addoption(parser):
    parser.addoption('--run-pypi-integration-tests', action='store_true')


@pytest.fixture
def FakePypiRepository(tmpdir):
    FakeRepository.tmpdir = str(tmpdir)
    return FakeRepository


class FakePackageFinder:
    format_control = FormatControl(set(), set())
    def find_requirement(self, req, upgrade):
        return Link(str(req)) # this URL will be passed to FakePipSession.get
    def add_dependency_links(self, links):
        pass


class FakeRepository(BaseRepository):
    """
    Mock for pip_compile.PyPIRepository
    Inspired by: https://raw.githubusercontent.com/nvie/pip-tools/1.6.5/tests/conftest.py
    """
    finder = FakePackageFinder()
    tmpdir = None

    @property
    def source_dir(self):
        return self.tmpdir

    @property
    def _download_dir(self):
        return self.tmpdir

    def __init__(self, *args, **kwargs):
        self.session = FakePipSession(self.tmpdir)
        with open('tests/fixtures/fake-index.json', 'r') as f:
            self.index = json.load(f)
        with open('tests/fixtures/fake-editables.json', 'r') as f:
            self.editables = json.load(f)

    def find_best_match(self, ireq, prereleases=False):
        if ireq.editable:
            return ireq
        versions = ireq.specifier.filter(self.index[ireq.req.key], prereleases=prereleases)
        best_version = max(versions, key=Version)
        return make_install_requirement(ireq.req.key, best_version, ireq.extras)

    def get_dependencies(self, ireq):
        if ireq.editable:
            return self.editables[str(ireq.link)]
        name, version, extras = as_tuple(ireq)
        # Store non-extra dependencies under the empty string
        extras = ireq.extras + ('',)
        dependencies = [dep for extra in extras for dep in self.index[name][version][extra]]
        return [InstallRequirement.from_line(dep) for dep in dependencies]

    def get_hashes(self, ireq):
        raise NotImplementedError # not needed

class FakePipSession(PipSession):
    def __init__(self, tmpdir):
        self.tmpdir = tmpdir

    def get(self, url, headers, stream):
        'Returns a mock valid tarball containing a single setup.py'
        assert '==' in url, '"url" should come from FakePackageFinder.find_requirement'
        pkg_name, version = url.split('==')
        tarball_filepath = _create_pkg_tarball(self.tmpdir, pkg_name, version)
        return MockRequestsResponse(url, tarball_filepath)

class MockRequestsResponse:
    def __init__(self, url, filepath):
        'Those are the only attributes/method used by pip/download.py'
        self.url = url
        self.raw = open(filepath, 'rb')
        self.headers= {'content-length': self.raw.tell()}

    def raise_for_status(self):
        pass

def _create_pkg_tarball(tmpdir, pkg_name, version):
    'Creates a tarball containing a single valid setup.py file for the (pkg_name, version) provided'
    tarball_basefilename = pkg_name + '-' + version
    pkg_dir = os.path.join(tmpdir, tarball_basefilename)
    os.mkdir(pkg_dir)
    with open(os.path.join(pkg_dir, 'setup.py'), 'w+') as setup_py:
        setup_py.write("from distutils.core import setup\nsetup(name='" + pkg_name + "', version='" + version + "', url='" + pkg_name + '==' + version + "')")
    tarball_filepath = os.path.join(tmpdir, tarball_basefilename + '.tar.gz')
    with tarfile.open(tarball_filepath, 'w:gz') as tar:
        tar.add(pkg_dir, arcname=os.path.basename(pkg_dir))
    return tarball_filepath
