import pytest


def pytest_addoption(parser):
    parser.addoption('--run-pypi-integration-tests', action='store_true')


# Except from FakePackageFinder, everything under this is copied from: https://raw.githubusercontent.com/nvie/pip-tools/1.6.5/tests/conftest.py

import json

from pip._vendor.packaging.version import Version
from pip.index import FormatControl
from pip.req import InstallRequirement
from pytest import fixture

from piptools.repositories.base import BaseRepository
from piptools.utils import as_tuple, make_install_requirement


@fixture
def repository():
    return FakeRepository()


class FakeRepository(BaseRepository):
    finder = FakePackageFinder()

    def __init__(self):
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


class FakePackageFinder:
    format_control = FormatControl(set(), set())
