from casp.validate import Validate
from casp.rpc import rpc
from src.lib.prisma import prisma
from casp.layout import render_page


@rpc(require_auth=True)
async def create_update_user(id: str | None = None, name: str | None = None):
    validated_id = Validate.cuid(id) if id else None
    validated_name = Validate.string(name) if name else None
    if validated_id:
        # Update existing user
        updated_user = await prisma.user.update(
            where={"id": validated_id},
            data={"name": validated_name},
            omit={"password": True}
        )
        return {"success": True, "user": updated_user}
    else:
        if not validated_name:
            raise ValueError("Name is required to create a new user.")
        # Create new user
        new_user = await prisma.user.create(
            data={"name": validated_name},
            omit={"password": True}
        )
        return {"success": True, "user": new_user}


@rpc(require_auth=True)
async def delete_user(id: str):
    deleted_user = await prisma.user.delete(where={"id": id})
    return {"success": True, "user": deleted_user}


async def page():
    users = await prisma.user.find_many()
    return render_page(__file__, {
        "users": [user.to_dict() for user in users]
    })
