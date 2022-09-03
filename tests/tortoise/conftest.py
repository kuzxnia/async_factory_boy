import asyncio
from typing import Generator

import pytest
from tortoise.contrib.test import finalizer, initializer
from tortoise.transactions import current_transaction_map


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
def db(request):
    initializer(['tests.tortoise.models'], db_url="sqlite://test.db")
    current_transaction_map["default"] = current_transaction_map["models"]

    yield

    request.addfinalizer(finalizer)
