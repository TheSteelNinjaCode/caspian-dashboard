from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Card(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "bg-card text-card-foreground flex flex-col gap-6 rounded-xl border py-6 shadow-sm", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def CardHeader(**props):
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "@container/card-header grid auto-rows-min grid-rows-[auto_auto] items-start gap-2 px-6 has-data-[slot=card-action]:grid-cols-[1fr_auto] [.border-b]:pb-6", incoming_class)

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
    computed_class = merge_classes("px-6", incoming_class)

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
        "flex items-center px-6 [.border-t]:pt-6", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "card-footer",
        "class": computed_class
    }, props)

    return f"<div {attributes}>{children}</div>"
