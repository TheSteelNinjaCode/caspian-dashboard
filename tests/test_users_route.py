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

    assert 'const [userPage, setUserPage] = pp.state({"users": [{"id": "user-123"' in result
    assert '"name": "Ada Lovelace"' in result


def test_get_users_page_filters_and_returns_rpc_pagination(monkeypatch):
    user = SimpleNamespace(
        id="user-123",
        name="Ada Lovelace",
        email="ada@example.com",
        createdAt=None,
    )
    count = AsyncMock(return_value=1)
    find_many = AsyncMock(return_value=[user])
    monkeypatch.setattr(users_route.prisma.user, "count", count)
    monkeypatch.setattr(users_route.prisma.user, "find_many", find_many)

    result = asyncio.run(users_route._get_users_page(1, "  ada  "))

    expected_where = {
        "OR": [
            {"name": {"contains": "ada"}},
            {"email": {"contains": "ada"}},
        ]
    }
    count.assert_awaited_once_with(where=expected_where)
    find_many.assert_awaited_once_with(
        where=expected_where,
        order_by={"createdAt": "desc"},
        skip=0,
        take=users_route.PAGE_SIZE,
    )
    assert result["users"][0]["name"] == "Ada Lovelace"
    assert result["pagination"] == {
        "currentPage": 1,
        "totalPages": 1,
        "hasPrevious": False,
        "hasNext": False,
        "previousHref": "/dashboard/users?q=ada",
        "nextHref": "/dashboard/users?page=2&q=ada",
    }
