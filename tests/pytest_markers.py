import pytest

pypi_integration = pytest.mark.skipif(
    not pytest.config.getoption('--run-pypi-integration-tests'),
    reason='Require to create HTTP connexions to Pypi'
)

# TODO: add Nexus integration tests
