from typing import Any, cast
from casp.component_decorator import component, render_html
from werkzeug.security import generate_password_hash
from casp.validate import Validate
from casp.rpc import rpc
from src.lib.prisma import prisma


@rpc(require_auth=True)
async def create_update_user(
    id: str | None = None,
    name: str | None = None,
    email: str | None = None,
    password: str | None = None
):
    print("ID: ", id)
    # validated_id = Validate.cuid(id) if id else None
    
    # print(f"Received data for user creation/update: id={validated_id}, name={name}, email={email}")

    # We type hint as dict[str, Any] to be more permissive,
    # but we will still need to cast it for Prisma's strict inputs.
    data: dict[str, Any] = {}

    if name:
        data["name"] = Validate.string(name)
    if email:
        data["email"] = Validate.email(email)

    # Only hash and add password if it is provided
    if password:
        data["password"] = generate_password_hash(password)

    if id:
        # --- Update existing user ---
        # We use cast(Any, data) to tell the type checker to ignore the strict TypedDict requirement
        updated_user = await prisma.user.update(
            where={"id": id},
            data=cast(Any, data),
            omit={"password": True}
        )
        return {"success": True, "user": updated_user}
    else:
        # --- Create new user ---
        # Validate required fields for creation
        if not name or not email or not password:
            raise ValueError(
                "Name, Email, and Password are required for new users.")

        new_user = await prisma.user.create(
            data=cast(Any, data),
            omit={"password": True}
        )
        return {"success": True, "user": new_user}


@component
def CreateUpdateDialog(openDialog: str, setOpenDialog: str, selectedUser: str | None = None, users: str | None = None, setUsers: str | None = None):
    return render_html(__file__, {
        "openDialog": openDialog,
        "setOpenDialog": setOpenDialog,
        "selectedUser": selectedUser,
        "users": users,
        "setUsers": setUsers
    })
