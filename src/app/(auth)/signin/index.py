from casp.auth import auth
from casp.rpc import rpc
from casp.layout import render_page
from casp.validate import Validate, Rule
from src.lib.prisma import prisma
from werkzeug.security import check_password_hash


@rpc(limits="5/min")
async def signin(email: str, password: str):
    email_validated = Validate.email(email)
    password_validated = Validate.with_rules(
        password, [
            Rule.REQUIRED,
            Rule.min(3),
            Rule.max(20)
        ])

    if not email_validated or not password_validated == True:
        return {"success": False, "message": "Invalid email or password."}

    user = await prisma.user.find_unique(
        where={"email": email_validated},
        include={"userRole": True},
    )

    print("🚀 ~ signin ~ user:", user)

    if not user:
        return {"success": False, "message": "Invalid email or password."}

    stored_password: str | None = user.password
    if not stored_password or not check_password_hash(stored_password, password):
        return {"success": False, "message": "Invalid email or password."}

    user_data = user.to_dict(omit={'password': True})
    return auth.sign_in(data=user_data, redirect_to="/dashboard")


def page():
    return render_page(__file__)
