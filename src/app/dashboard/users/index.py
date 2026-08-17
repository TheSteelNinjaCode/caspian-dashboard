import math
from typing import cast
from urllib.parse import urlencode

from casp.component_decorator import html
from casp.layout import Metadata

from src.components.dashboard.users.UsersPagination import UsersPagination
from src.components.dashboard.users.UsersTable import UsersTable
from src.components.dashboard.users.UsersToolbar import UsersToolbar
from src.lib.prisma import prisma
from src.lib.prisma.models import UserWhereInput

PAGE_SIZE = 5

metadata = Metadata(
    title="Users | Caspian Dashboard",
    description="Browse and search dashboard users.",
)


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

    users = [
        {
            "id": user.id,
            "name": user.name or "Unnamed user",
            "email": user.email or "No email available",
            "created_at": user.createdAt.strftime("%B %d, %Y") if user.createdAt else "Unavailable",
        }
        for user in records
    ]

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
    const searchTimeout = pp.ref(null);

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
    )
