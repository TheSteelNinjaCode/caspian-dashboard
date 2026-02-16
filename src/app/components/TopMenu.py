from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component, render_html
from casp.rpc import auth, rpc


@rpc(require_auth=True)
def logout():
    return auth.sign_out()


@component
def TopMenu():
    user = auth.get_payload()
    return render_html(__file__, {
        "user": user
    })
