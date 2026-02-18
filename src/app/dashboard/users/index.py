from math import ceil
from typing import Any, cast
from casp.layout import render_page
from casp.rpc import rpc
from src.lib.prisma import prisma
from src.lib.prisma.db import UserWhereInput

PAGE_SIZE = 5

# --- Helper Function (Shared Logic) ---
async def fetch_users_data(search: str = "", page: int = 1):
    current_page = int(page)
    
    # define filter
    where_clause: UserWhereInput = {}
    if search:
        where_clause = {
            "OR": [
                {"name": {"contains": search}},
                {"email": {"contains": search}}
            ]
        }

    # get totals
    total_users = await prisma.user.count(where=where_clause)
    total_pages = ceil(total_users / PAGE_SIZE)
    
    # prevent out of bounds
    if current_page > total_pages and total_pages > 0:
        current_page = total_pages
    if current_page < 1: 
        current_page = 1

    skip = (current_page - 1) * PAGE_SIZE

    # fetch data
    users = await prisma.user.find_many(
        where=where_clause,
        take=PAGE_SIZE,
        skip=skip,
        order_by={"createdAt": "desc"}
    )

    return {
        "users": [user.to_dict() for user in users],
        "pagination": {
            "currentPage": current_page,
            "totalPages": total_pages,
            "totalUsers": total_users,
            "search": search,
            "hasPrev": current_page > 1,
            "hasNext": current_page < total_pages
        }
    }

# --- RPC Handler (For Client-Side Updates) ---
@rpc(require_auth=True)
async def search_paginate_users(search: str = "", page: int = 1):
    return await fetch_users_data(search, page)

# --- Page Handler (For Initial Load) ---
async def page():
    # Load default state (Page 1, no search)
    data = await fetch_users_data()
    return render_page(__file__, data)