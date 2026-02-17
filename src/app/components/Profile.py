from src.lib.prisma import prisma
from casp.rpc import auth, rpc
from casp.component_decorator import component, render_html

def get_user_profile():
    user = auth.get_payload()

    if not user:
        return None

    return user

@rpc(require_auth=True)
async def save_profile(name: str):
    user = auth.get_payload()

    if not user:
        return {"success": False, "message": "User not authenticated"}

    user_id = user.get("id")

    if not user_id:
        return {"success": False, "message": "User ID not found in token"}

    updated_profile = await prisma.user.update(
        where={
            'id': user_id
        },
        data={
            'name': name
        }
    )

    return {"success": True, "profile": updated_profile}


@component
def Profile(open: str | None = None, onOpenChange: str | None = None) -> str:
    user = get_user_profile()
    return render_html(__file__, {
        "open": open,
        "onOpenChange": onOpenChange,
        "user": user,
    })
