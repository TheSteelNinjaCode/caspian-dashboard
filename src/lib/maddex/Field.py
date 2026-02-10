from typing import Literal
from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Field(orientation: Literal["vertical", "horizontal", "responsive"] = "vertical", **props):
    incoming_class = props.pop("class", "")

    base_styles = "group/field flex w-full gap-3 data-[invalid=true]:text-destructive"

    orientation_styles = {
        "vertical": "flex-col [&>*]:w-full [&>.sr-only]:w-auto",
        "horizontal": (
            "flex-row items-center "
            "[&>[data-slot=field-label]]:flex-auto "
            "has-[>[data-slot=field-content]]:items-start has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px"
        ),
        "responsive": (
            "flex-col [&>*]:w-full [&>.sr-only]:w-auto "
            "@md/field-group:flex-row @md/field-group:items-center @md/field-group:[&>*]:w-auto "
            "@md/field-group:[&>[data-slot=field-label]]:flex-auto "
            "@md/field-group:has-[>[data-slot=field-content]]:items-start "
            "@md/field-group:has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px"
        )
    }

    final_class = merge_classes(
        base_styles,
        orientation_styles.get(orientation, orientation_styles["vertical"]),
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "role": "group",
        "data-slot": "field",
        "data-orientation": orientation,
        "class": final_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def FieldSet(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "flex flex-col gap-6",
        "has-[>[data-slot=checkbox-group]]:gap-3 has-[>[data-slot=radio-group]]:gap-3",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-set",
        "class": final_class
    }, props)

    return f"<fieldset {attributes}>{children}</fieldset>"


@component
def FieldLegend(variant: Literal["legend", "label"] = "legend", **props):
    incoming_class = props.pop("class", "")

    variant_styles = {
        "legend": "text-base",
        "label": "text-sm",
    }

    final_class = merge_classes(
        "mb-3 font-medium",
        "data-[variant=legend]:text-base data-[variant=label]:text-sm",
        variant_styles.get(variant, ""),
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-legend",
        "data-variant": variant,
        "class": final_class
    }, props)

    return f"<legend {attributes}>{children}</legend>"


@component
def FieldGroup(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "group/field-group @container/field-group flex w-full flex-col gap-7",
        "data-[slot=checkbox-group]:gap-3 [&>[data-slot=field-group]]:gap-4",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-group",
        "class": final_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def FieldContent(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "group/field-content flex flex-1 flex-col gap-1.5 leading-snug",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-content",
        "class": final_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def FieldLabel(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",
        "group/field-label peer/field-label flex w-fit gap-2 leading-snug group-data-[disabled=true]/field:opacity-50",
        "has-[>[data-slot=field]]:w-full has-[>[data-slot=field]]:flex-col has-[>[data-slot=field]]:rounded-md has-[>[data-slot=field]]:border [&>*]:data-[slot=field]:p-4",
        "has-data-[state=checked]:bg-primary/5 has-data-[state=checked]:border-primary dark:has-data-[state=checked]:bg-primary/10",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-label",
        "class": final_class
    }, props)

    return f"<label {attributes}>{children}</label>"


@component
def FieldTitle(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "flex w-fit items-center gap-2 text-sm leading-snug font-medium group-data-[disabled=true]/field:opacity-50",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-label",
        "class": final_class
    }, props)

    return f"<div {attributes}>{children}</div>"


@component
def FieldDescription(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "text-muted-foreground text-sm leading-normal font-normal group-has-[[data-orientation=horizontal]]/field:text-balance",
        "last:mt-0 nth-last-2:-mt-1 [[data-variant=legend]+&]:-mt-1.5",
        "[&>a:hover]:text-primary [&>a]:underline [&>a]:underline-offset-4",
        incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "field-description",
        "class": final_class
    }, props)

    return f"<p {attributes}>{children}</p>"


@component
def FieldSeparator(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", None)

    final_class = merge_classes(
        "relative -my-2 h-5 text-sm group-data-[variant=outline]/field-group:-mb-2",
        incoming_class
    )

    attributes = get_attributes({
        "data-slot": "field-separator",
        "data-content": "true" if children else "false",
        "class": final_class
    }, props)

    separator_html = '<div class="shrink-0 bg-border h-[1px] w-full absolute inset-0 top-1/2"></div>'

    content_html = ""
    if children:
        content_html = (
            f"""<span class="bg-background text-muted-foreground relative mx-auto block w-fit px-2" data-slot="field-separator-content">
                {children}
            </span>"""
        )

    return f"<div {attributes}>{separator_html}{content_html}</div>"


@component
def FieldError(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", None)
    errors = props.pop("errors", [])

    content_html = ""

    if children:
        content_html = str(children)
    elif errors:
        unique_errors = {}
        for err in errors:
            if err and "message" in err:
                unique_errors[err["message"]] = err

        unique_values = list(unique_errors.values())

        if len(unique_values) == 1:
            content_html = unique_values[0]["message"]
        else:
            list_items = "".join(
                [f"<li>{err['message']}</li>" for err in unique_values])
            content_html = f'<ul class="ml-4 flex list-disc flex-col gap-1">{list_items}</ul>'

    if not content_html:
        return ""

    final_class = merge_classes(
        "text-destructive text-sm font-normal", incoming_class)

    attributes = get_attributes({
        "role": "alert",
        "data-slot": "field-error",
        "class": final_class
    }, props)

    return f"<div {attributes}>{content_html}</div>"
