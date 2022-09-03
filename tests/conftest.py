import pytest


def pytest_collection_modifyitems(items):
    for item in items:
        # add marker to all tests
        item.add_marker(pytest.mark.asyncio)
