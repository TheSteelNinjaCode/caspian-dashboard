from __future__ import annotations
from typing import Literal, Optional
from casp.component_decorator import component, render_html
from casp.html_attrs import merge_classes, get_attributes

ToasterPosition = Literal[
    "top-left",
    "top-center",
    "top-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]


@component
def Toast(
    toasts: str | None = "{[]}",
    onChange: str = "",
    position: ToasterPosition = "bottom-right",
    maxToasts: int = 5,
    duration: int = 4000,
    richColors: bool | None = True,
    **props,
) -> str:
    pos_classes: str = {
        "top-left": "top-0 left-0",
        "top-center": "top-0 left-1/2 -translate-x-1/2",
        "top-right": "top-0 right-0",
        "bottom-left": "bottom-0 left-0",
        "bottom-center": "bottom-0 left-1/2 -translate-x-1/2",
        "bottom-right": "bottom-0 right-0",
    }.get(position, "bottom-0 right-0")

    container_class = merge_classes(
        f"fixed z-[100] flex flex-col p-4 w-full md:max-w-[420px] pointer-events-none",
        pos_classes,
        props.pop("class", ""),
    )

    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "class": container_class,
            "data-slot": "toaster",
            "toasts": toasts,
            "onChange": onChange,
        },
        props,
    )

    return render_html(
        __file__,
        attrs=attrs,
        position=position,
        max_toasts=maxToasts,
        duration=duration,
        rich_colors=richColors,
        children=children,
    )
