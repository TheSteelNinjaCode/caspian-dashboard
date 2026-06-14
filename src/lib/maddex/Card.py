from typing import Literal

from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


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

    size_classes = {
        "default": "gap-6 py-6",
        "sm": "gap-4 py-4",
    }

    computed_class = merge_classes(
        "group/card bg-card text-card-foreground flex flex-col rounded-xl border shadow-sm",
        size_classes[resolved_size],
        incoming_class,
    )

    attributes = get_attributes({
        "data-slot": "card",
        "data-size": resolved_size,
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardHeader(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-1.5 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6 group-data-[size=sm]/card:gap-1 group-data-[size=sm]/card:px-4",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-header",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardTitle(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "leading-none font-semibold", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-title",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardDescription(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "text-muted-foreground text-sm", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-description",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardAction(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "col-start-2 row-span-2 row-start-1 self-start justify-self-end", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-action",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardContent(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "px-6 group-data-[size=sm]/card:px-4",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-content",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardFooter(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "flex items-center px-6 [.border-t]:pt-6 group-data-[size=sm]/card:px-4",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-footer",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"
