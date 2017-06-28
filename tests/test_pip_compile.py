from nexus_uploader.pip_compile import pip_compile
from nexus_uploader.requirements import read_requirements

from unittest.mock import patch
from .pytest_markers import pypi_integration


@pypi_integration  # only ran with --run-pypi-integration-tests
def test_pipcompile_with_real_repository():
    reqs_gen = pip_compile(['nexus_uploader'],
                           nexus_hostname='dummy-nexus.wtf',
                           append_egg_hash_to_url_if_need_be=raise_if_called)
    assert len(read_requirements(reqs_gen)) == 6


def test_pipcompile_with_mocked_repository(FakePypiRepository):
    with patch('nexus_uploader.pip_compile.PyPIRepository', FakePypiRepository):
        reqs_gen = pip_compile(['pytest'],
                               nexus_hostname='dummy-nexus.wtf',
                               append_egg_hash_to_url_if_need_be=raise_if_called)
        assert read_requirements(reqs_gen) == \
            [('version-locked', ('py', '1.4.31', 'via pytest')), ('version-locked', ('pytest', '3.0.2', ''))]


def raise_if_called(*args, **kwargs):
    raise NotImplementedError
