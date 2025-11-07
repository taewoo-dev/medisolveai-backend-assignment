from typing import Any

import pytest
from pytest_asyncio import is_async_test

pytest_plugins = ("app.tests.fixtures",)


def pytest_collection_modifyitems(items: Any) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)
