from casp.component_decorator import component, render_html
from markupsafe import Markup


def _as_markup(value) -> Markup:
    if value is None:
        return Markup("")
    if isinstance(value, Markup):
        return value

    return Markup(str(value))


@component
def Portal(
    children="",
    content_attributes="",
    portal_attributes="",
    overlay="",
    close="",
    script="",
):
    return render_html(
        "Portal.html",
        {
            "children": children,
            "content_attributes": _as_markup(content_attributes),
            "portal_attributes": _as_markup(portal_attributes),
            "overlay": overlay,
            "close": close,
            "script": _as_markup(script),
        },
    )