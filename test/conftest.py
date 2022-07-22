"""
Configuration file for pytest
"""
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--skip-numerical", action="store_true", default=True, help="Skip numerical comparison with Matlab implementation"
    )


@pytest.fixture(scope="session")
def skip_numerical(request):
    if request.config.getoption("--skip-numerical"):
        pytest.skip()
