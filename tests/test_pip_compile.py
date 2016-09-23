from nexus_uploader.pip_compile import pip_compile
from nexus_uploader.requirements import read_requirements

from unittest.mock import patch
from .pytest_markers import pypi_integration


@pypi_integration  # only ran with --run-pypi-integration-tests
def test_pipcompile_with_real_repository():
    nexus_requirements = read_requirements(pip_compile(['nexus_uploader'], 'dummy-nexus.wtf', raise_if_called))
    assert len(nexus_requirements) == 6


def test_pipcompile_with_mocked_repository(FakePypiRepository):
    with patch('nexus_uploader.pip_compile.PyPIRepository', FakePypiRepository):
        assert read_requirements(pip_compile(['pytest'], 'dummy-nexus.wtf', raise_if_called)) == \
            [('version-locked', ('py', '1.4.31', 'via pytest')), ('version-locked', ('pytest', '3.0.2', ''))]


def raise_if_called(*args, **kwargs):
    raise NotImplementedError
