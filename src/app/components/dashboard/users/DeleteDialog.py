from src.lib.prisma import prisma
from casp.rpc import rpc
from casp.component_decorator import render_html
from casp.component_decorator import component


@rpc(require_auth=True)
async def delete_user(id: str):
    deleted_user = await prisma.user.delete(where={"id": id})
    return {"success": True, "user": deleted_user}


@component
def DeleteDialog(openDialog: str, setOpenDialog: str,  selectedUser: str | None = None, users: str | None = None, setUsers: str | None = None):
    return render_html(__file__, {
        "openDialog": openDialog,
        "setOpenDialog": setOpenDialog,
        "selectedUser": selectedUser,
        "users": users,
        "setUsers": setUsers
    })
