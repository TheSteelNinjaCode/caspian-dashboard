from .utils import generate_id
from typing import Any
from casp.component_decorator import component, render_html
from casp.html_attrs import merge_classes, get_attributes


@component
def Portal(
    children: Any = "",
    to: str = "body",
    **props,
) -> str:
    portal_id = props.get("id", generate_id("pp-portal-"))
    src_id = generate_id("pp-portal-src-")

    target_selector = "#pp-portal-root" if (not to or to == "body") else to

    incoming_class = props.pop("class", "")
    computed_class = merge_classes(incoming_class)

    attr_dict = {
        "id": portal_id,
        "data-slot": "portal",
        "data-portal-id": portal_id,
        "data-portal-target": target_selector,
        "to": to,
        "class": computed_class,
    }

    attrs = get_attributes(props, attr_dict)

    return render_html(
        "Portal.html",
        src_id=src_id,
        attrs=attrs,
        children=children,
        portal_id=portal_id,
        target_selector=target_selector
    )
