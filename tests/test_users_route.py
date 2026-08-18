import asyncio
import importlib
from types import SimpleNamespace
from unittest.mock import AsyncMock


users_route = importlib.import_module("src.app.dashboard.users.index")


def test_delete_user_rejects_empty_id():
    result = asyncio.run(users_route._delete_user("   "))

    assert result == {"success": False, "message": "A user ID is required."}


def test_delete_user_removes_existing_user(monkeypatch):
    delete = AsyncMock(return_value=SimpleNamespace(id="user-123"))
    monkeypatch.setattr(users_route.prisma.user, "delete", delete)

    result = asyncio.run(users_route._delete_user(" user-123 "))

    assert result == {"success": True, "id": "user-123"}
    delete.assert_awaited_once_with(where={"id": "user-123"})


def test_delete_user_reports_missing_user(monkeypatch):
    delete = AsyncMock(return_value=None)
    monkeypatch.setattr(users_route.prisma.user, "delete", delete)

    result = asyncio.run(users_route._delete_user("missing-user"))

    assert result == {
        "success": False,
        "message": "The selected user no longer exists.",
    }


def test_page_serializes_queried_users_into_owner_script(monkeypatch):
    user = SimpleNamespace(
        id="user-123",
        name="Ada Lovelace",
        email="ada@example.com",
        createdAt=None,
    )
    monkeypatch.setattr(users_route.prisma.user, "count", AsyncMock(return_value=1))
    monkeypatch.setattr(users_route.prisma.user, "find_many", AsyncMock(return_value=[user]))

    result = str(asyncio.run(users_route.page()))

    assert 'const [visibleUsers, setVisibleUsers] = pp.state([{"id": "user-123"' in result
    assert '"name": "Ada Lovelace"' in result
