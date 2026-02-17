from .Slot import Slot
from .Separator import Separator
from typing import Literal
from casp.component_decorator import component
from casp.html_attrs import merge_classes, get_attributes

Orientation = Literal["horizontal", "vertical"]


@component
def ButtonGroup(
    orientation: Orientation = "horizontal",
    **props,
) -> str:
    base_classes = (
        "flex w-fit items-stretch [&>*]:focus-visible:z-10 [&>*]:focus-visible:relative "
        "[&>[data-slot=select-trigger]:not([class*='w-'])]:w-fit [&>input]:flex-1 "
        "has-[select[aria-hidden=true]:last-child]:[&>[data-slot=select-trigger]:last-of-type]:rounded-r-md "
        "has-[>[data-slot=button-group]]:gap-2"
    )

    orientation_classes = {
        "horizontal": (
            "[&>*:not(:first-child)]:rounded-l-none "
            "[&>*:not(:first-child)]:border-l-0 "
            "[&>*:not(:last-child)]:rounded-r-none"
        ),
        "vertical": (
            "flex-col "
            "[&>*:not(:first-child)]:rounded-t-none "
            "[&>*:not(:first-child)]:border-t-0 "
            "[&>*:not(:last-child)]:rounded-b-none"
        ),
    }

    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    computed_class = merge_classes(
        base_classes,
        orientation_classes.get(
            orientation, orientation_classes["horizontal"]),
        incoming_class,
    )

    attrs = get_attributes(
        {
            "role": "group",
            "data-slot": "button-group",
            "data-orientation": orientation,
            "class": computed_class,
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def ButtonGroupText(
    asChild: bool | str | None = False,
    **props,
) -> str:
    base_classes = (
        "bg-muted flex items-center gap-2 rounded-md border px-4 text-sm font-medium shadow-xs "
        "[&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4"
    )

    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")

    computed_class = merge_classes(
        base_classes,
        incoming_class,
    )

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{"class": computed_class, **props}
        )

    attrs = get_attributes(
        {
            "class": computed_class,
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def ButtonGroupSeparator(
    orientation: Orientation = "vertical",
    **props,
) -> str:
    base_classes = "bg-input relative !m-0 self-stretch data-[orientation=vertical]:h-auto"
    incoming_class = props.pop("class", "")

    computed_class = merge_classes(
        base_classes,
        incoming_class,
    )

    return Separator(
        orientation=orientation,
        data_slot="button-group-separator",
        class_name=computed_class,
        **props
    )
