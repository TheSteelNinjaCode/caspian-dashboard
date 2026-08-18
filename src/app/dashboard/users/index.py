import math
from typing import cast
from urllib.parse import urlencode

from casp.component_decorator import html
from casp.layout import Metadata
from casp.rpc import rpc
from casp.validate import Validate
from werkzeug.security import generate_password_hash

from src.components.dashboard.users.UsersPagination import UsersPagination
from src.components.dashboard.users.UsersTable import UsersTable
from src.components.dashboard.users.UsersToolbar import UsersToolbar
from src.lib.prisma import prisma
from src.lib.prisma.models import UserCreateInput, UserUpdateInput, UserWhereInput

PAGE_SIZE = 5

metadata = Metadata(
    title="Users | Caspian Dashboard",
    description="Browse and search dashboard users.",
)


def _serialize_user(user) -> dict[str, str]:
    return {
        "id": user.id,
        "name": user.name or "Unnamed user",
        "email": user.email or "No email available",
        "created_at": user.createdAt.strftime("%B %d, %Y") if user.createdAt else "Unavailable",
    }


async def _delete_user(user_id: str) -> dict[str, str | bool]:
    normalized_id = (user_id or "").strip()
    if not normalized_id:
        return {"success": False, "message": "A user ID is required."}

    deleted_user = await prisma.user.delete(where={"id": normalized_id})
    if not deleted_user:
        return {"success": False, "message": "The selected user no longer exists."}

    return {"success": True, "id": deleted_user.id}


@rpc(require_auth=True, limits="20/minute")
async def delete_user(user_id: str) -> dict[str, str | bool]:
    return await _delete_user(user_id)


@rpc(require_auth=True, limits="20/minute")
async def save_user(name: str, email: str, password: str = "", user_id: str = "") -> dict[str, object]:
    normalized_id = (user_id or "").strip()
    name_validated = Validate.string(name)
    email_validated = Validate.email(email)

    if not name_validated or not email_validated:
        return {"success": False, "message": "A name and a valid email are required."}

    if not normalized_id and not password:
        return {"success": False, "message": "A password is required to create a user."}

    existing = await prisma.user.find_unique(where={"email": email_validated})
    if existing and existing.id != normalized_id:
        return {"success": False, "message": "A user with this email already exists."}

    if normalized_id:
        update_data = cast(UserUpdateInput, {"name": name_validated, "email": email_validated})
        if password:
            update_data["password"] = generate_password_hash(password)
        saved_user = await prisma.user.update(where={"id": normalized_id}, data=update_data)
    else:
        create_data = cast(
            UserCreateInput,
            {
                "name": name_validated,
                "email": email_validated,
                "password": generate_password_hash(password),
            },
        )
        saved_user = await prisma.user.create(data=create_data)

    if not saved_user:
        return {"success": False, "message": "Unable to save this user."}

    return {"success": True, "user": _serialize_user(saved_user)}


def _build_search_where(search_term: str) -> UserWhereInput:
    if not search_term:
        return {}

    return cast(
        UserWhereInput,
        {
            "OR": [
                {"name": {"contains": search_term}},
                {"email": {"contains": search_term}},
            ]
        },
    )


def _build_page_href(page_number: int, search_term: str) -> str:
    query = {}

    if page_number > 1:
        query["page"] = page_number

    if search_term:
        query["q"] = search_term

    query_string = urlencode(query)
    return f"/dashboard/users{f'?{query_string}' if query_string else ''}"


async def page(page: int = 1, q: str = ""):
    current_page = max(int(page or 1), 1)
    search_term = (q or "").strip()
    where = _build_search_where(search_term)

    total_users = await prisma.user.count(where=where)
    total_pages = max(math.ceil(total_users / PAGE_SIZE), 1)
    current_page = min(current_page, total_pages)
    skip = (current_page - 1) * PAGE_SIZE

    records = await prisma.user.find_many(
        where=where,
        order_by={"createdAt": "desc"},
        skip=skip,
        take=PAGE_SIZE,
    )

    users = [_serialize_user(user) for user in records]

    toolbar = UsersToolbar(search_term=search_term)
    table = UsersTable(users=users)
    pagination = UsersPagination(
        current_page=current_page,
        total_pages=total_pages,
        has_previous=current_page > 1,
        has_next=current_page < total_pages,
        previous_href=_build_page_href(current_page - 1, search_term),
        next_href=_build_page_href(current_page + 1, search_term),
    )

    return html(r"""
<section class="space-y-6">
  {{ toolbar }}
  {{ table }}
  {{ pagination }}

  <script>
        const [visibleUsers, setVisibleUsers] = pp.state({{ users | json }});
        const [createDialogOpen, setCreateDialogOpen] = pp.state(false);
        const [editDialogOpen, setEditDialogOpen] = pp.state(false);
        const [deleteDialogOpen, setDeleteDialogOpen] = pp.state(false);
        const [selectedUser, setSelectedUser] = pp.state(null);
        const [isDeleting, setIsDeleting] = pp.state(false);
        const [deleteError, setDeleteError] = pp.state("");
    const searchTimeout = pp.ref(null);

        function handleCreateSuccess(user) {
            setCreateDialogOpen(false);
            if (user) pp.redirect(window.location.pathname + window.location.search);
        }

        function openEditDialog(user) {
            setSelectedUser({ ...user });
            setEditDialogOpen(true);
        }

        function handleEditDialogOpenChange(nextOpen) {
            setEditDialogOpen(nextOpen);
        }

        function handleEditSuccess(user) {
            setEditDialogOpen(false);
            if (!user) return;
            setVisibleUsers((currentUsers) =>
                currentUsers.map((existing) => (existing.id === user.id ? user : existing)),
            );
        }

        function openDeleteDialog(user) {
            setSelectedUser({ ...user });
            setDeleteError("");
            setDeleteDialogOpen(true);
        }

        function handleDeleteDialogOpenChange(nextOpen) {
            if (isDeleting) return;
            setDeleteDialogOpen(nextOpen);
            if (!nextOpen) setDeleteError("");
        }

        async function confirmDelete() {
            if (!selectedUser?.id || isDeleting) return;

            setIsDeleting(true);
            setDeleteError("");
            try {
                const result = await pp.rpc("delete_user", { user_id: selectedUser.id });
                if (!result?.success) {
                    throw new Error(result?.message || "Unable to delete this user.");
                }

                setVisibleUsers((currentUsers) =>
                    currentUsers.filter((user) => user.id !== selectedUser.id),
                );
                setDeleteDialogOpen(false);
                setSelectedUser(null);
            } catch (error) {
                setDeleteError(error instanceof Error ? error.message : "Unable to delete this user.");
            } finally {
                setIsDeleting(false);
            }
        }

    function queueSearch(value) {
        const nextValue = value.trim();
        clearTimeout(searchTimeout.current);
        searchTimeout.current = setTimeout(() => {
            const nextUrl = nextValue
                ? `/dashboard/users?q=${encodeURIComponent(nextValue)}`
                : "/dashboard/users";

            if (nextUrl !== `${window.location.pathname}${window.location.search}`) {
                pp.redirect(nextUrl);
            }
        }, 250);
    }

    pp.effect(() => () => clearTimeout(searchTimeout.current), []);
  </script>
</section>
""",
        toolbar=toolbar,
        table=table,
        pagination=pagination,
        users=users,
    )
