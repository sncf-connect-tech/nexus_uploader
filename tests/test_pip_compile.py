from nexus_uploader.pip_compile import pip_compile
from nexus_uploader.requirements import read_requirements

from unittest.mock import patch
from .pytest_markers import pypi_integration


@pypi_integration  # only ran with --run-pypi-integration-tests
def test_pipcompile_with_real_repository():
    nexus_requirements = read_requirements(pip_compile(['nexus_uploader'], 'dummy-nexus.wtf', raise_if_called))
    assert len(nexus_requirements) == 6


def test_pipcompile_with_mocked_repository(repository):
    with patch('nexus_uploader.pip_compile.LocalRequirementsRepository', new=lambda **kwargs: repository):
        assert read_requirements(pip_compile(['ipython'], 'dummy-nexus.wtf', raise_if_called)) == \
            [('version-locked', ('gnureadline', '6.3.3', 'via ipython')), ('version-locked', ('ipython', '2.1.0', ''))]


def raise_if_called(*args, **kwargs):
    raise NotImplementedError
