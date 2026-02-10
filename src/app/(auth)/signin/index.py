from casp.rpc import rpc
from casp.layout import render_page


@rpc(limits="5/min")
def signin(email: str, password: str):
    print("🚀 ~ signin ~ data:", {"email": email, "password": password})


def page():
    return render_page(__file__)
