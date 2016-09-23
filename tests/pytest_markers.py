import pytest

pypi_integration = pytest.mark.skipif(
    not pytest.config.getoption('--run-pypi-integration-tests'),
    reason='Require to create HTTPT connexions to Pypi'
)
