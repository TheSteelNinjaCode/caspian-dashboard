from typing import Any, Literal
from casp.component_decorator import component
from casp.html_attrs import merge_classes, get_attributes

SeparatorOrientation = Literal["horizontal", "vertical"]


@component
def Separator(
    orientation: SeparatorOrientation = "horizontal",
    decorative: bool = True,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "bg-border shrink-0 "
        "data-[orientation=horizontal]:h-px data-[orientation=horizontal]:w-full "
        "data-[orientation=vertical]:h-full data-[orientation=vertical]:w-px",
        incoming_class,
    )

    base_attrs: dict[str, Any] = {
        "data-slot": "separator",
        "data-orientation": orientation,
        "class": computed_class,
    }

    if decorative:
        base_attrs.update(
            {
                "role": "presentation",
                "aria-hidden": "true",
            }
        )
    else:
        base_attrs.update(
            {
                "role": "separator",
                "aria-orientation": orientation,
            }
        )

    attrs = get_attributes(base_attrs, props)

    return f"<div {attrs}></div>"
