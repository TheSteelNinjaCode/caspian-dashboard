from typing import Literal

from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component, html


CardSize = Literal["default", "sm"]


def _resolve_size(size: str) -> CardSize:
    if size == "sm":
        return "sm"
    return "default"


@component
def Card(size: CardSize | str = "default", **props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    resolved_size = _resolve_size(props.pop("size", size))

    computed_class = merge_classes(
        "flex flex-col gap-6 rounded-xl border bg-card py-6 text-card-foreground shadow-sm",
        incoming_class,
    )

    attributes = get_attributes(
        {"data-slot": "card", "data-size": resolved_size, "class": computed_class}, props
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardHeader(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-header", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardTitle(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes("leading-none font-semibold", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-title", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardDescription(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes("text-sm text-muted-foreground", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-description", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardAction(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end", incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-action", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardContent(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "px-6",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-content", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def CardFooter(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "flex items-center px-6 [.border-t]:pt-6",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({"data-slot": "card-footer", "class": computed_class}, props)

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )
