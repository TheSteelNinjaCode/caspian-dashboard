import html
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from casp.component_decorator import component
from casp.html_attrs import get_attributes, merge_classes

from .Separator import Separator
from .Slot import Slot

FieldOrientation = Literal["vertical", "horizontal", "responsive"]
FieldLegendVariant = Literal["legend", "label"]


def _normalize_choice(value: str | None, allowed: set[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else fallback


def _normalize_flag_attr(value: bool | str | None) -> str | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return "true" if value else "false"

    stripped = value.strip()
    if not stripped:
        return "true"

    if stripped.startswith("{") and stripped.endswith("}"):
        expression = stripped[1:-1].strip()
        return "{" + f"({expression}) ? 'true' : 'false'" + "}"

    normalized = stripped.lower()
    if normalized in {"true", "1", "yes", "on"}:
        return "true"
    if normalized in {"false", "0", "no", "off", "none", "null"}:
        return "false"

    return value


def _normalize_error_messages(
    errors: Sequence[Mapping[str, Any] | str | None] | Mapping[str, Any] | str | None,
) -> list[str]:
    if errors is None:
        return []

    if isinstance(errors, str):
        stripped = errors.strip()
        return [stripped] if stripped else []

    raw_items: Sequence[Mapping[str, Any] | str | None]
    if isinstance(errors, Mapping):
        raw_items = [errors]
    else:
        raw_items = errors

    seen: set[str] = set()
    messages: list[str] = []
    for item in raw_items:
        if item is None:
            continue

        message: str | None
        if isinstance(item, str):
            message = item.strip()
        elif isinstance(item, Mapping):
            raw_message = item.get("message")
            message = str(raw_message).strip() if raw_message is not None else None
        else:
            raw_message = getattr(item, "message", None)
            message = str(raw_message).strip() if raw_message is not None else None

        if not message or message in seen:
            continue

        seen.add(message)
        messages.append(message)

    return messages


def _field_label_proxy_script() -> str:
        return """
<script>
    const rootRef = pp.ref();

    pp.effect(() => {
        const label = rootRef.current;
        if (!(label instanceof HTMLLabelElement)) return;

        let isProxying = false;
        const interactiveSelector = [
            "[data-slot=checkbox]",
            "[data-slot=switch]",
            "[role=radio]",
            "button",
            "input",
            "textarea",
            "select",
            "a[href]",
            '[contenteditable="true"]',
            "[contenteditable='']",
        ].join(",");

        const onClick = (event) => {
            if (isProxying) return;

            const rawTarget = event.target;
            const target = rawTarget instanceof Element
                ? rawTarget
                : rawTarget instanceof Node
                    ? rawTarget.parentElement
                    : null;

            if (!(target instanceof Element)) return;

            const nearestInteractive = target.closest(interactiveSelector);
            let control = null;

            const targetId = label.htmlFor || label.getAttribute("for") || label.getAttribute("htmlFor");
            if (targetId) {
                const associatedControl = document.getElementById(targetId);
                if (associatedControl instanceof HTMLElement && associatedControl.matches("[data-slot=checkbox], [data-slot=switch], [role=radio]")) {
                    control = associatedControl;
                }
            } else if (label.querySelector("[data-slot=field]")) {
                const nestedControl = label.querySelector("[data-slot=checkbox], [data-slot=switch], [role=radio]");
                if (nestedControl instanceof HTMLElement) {
                    control = nestedControl;
                }
            }

            if (!(control instanceof HTMLElement)) return;
            if (nearestInteractive === control) return;
            if (nearestInteractive && nearestInteractive !== label && label.contains(nearestInteractive)) {
                return;
            }

            event.preventDefault();
            isProxying = true;
            control.click();
            queueMicrotask(() => {
                isProxying = false;
            });
        };

        label.addEventListener("click", onClick);
        return () => {
            label.removeEventListener("click", onClick);
        };
    }, [pp.props.for, pp.props.htmlFor]);
</script>
        """.strip()


@component
def FieldSet(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "field-set",
            "class": merge_classes(
                "flex flex-col gap-6",
                "has-[>[data-slot=checkbox-group]]:gap-3 has-[>[data-slot=radio-group]]:gap-3",
                incoming_class,
            ),
        },
        props,
    )

    return f"<fieldset {attributes}>{children}</fieldset>"


@component
def FieldLegend(
    variant: FieldLegendVariant | str = "legend",
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    resolved_variant = _normalize_choice(
        props.pop("variant", variant),
        {"legend", "label"},
        "legend",
    )

    attributes = get_attributes(
        {
            "data-slot": "field-legend",
            "data-variant": resolved_variant,
            "class": merge_classes(
                "mb-3 font-medium",
                "data-[variant=legend]:text-base",
                "data-[variant=label]:text-sm",
                incoming_class,
            ),
        },
        props,
    )

    return f"<legend {attributes}>{children}</legend>"


@component
def FieldGroup(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "field-group",
            "class": merge_classes(
                "group/field-group @container/field-group flex w-full flex-col gap-7",
                "data-[slot=checkbox-group]:gap-3 [&>[data-slot=field-group]]:gap-4",
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attributes}>{children}</div>"


@component
def Field(
    orientation: FieldOrientation | str = "vertical",
    invalid: bool | str | None = None,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    resolved_orientation = _normalize_choice(
        props.pop("orientation", orientation),
        {"vertical", "horizontal", "responsive"},
        "vertical",
    )
    invalid_attr = _normalize_flag_attr(
        props.pop("data-invalid", props.pop("dataInvalid", props.pop("invalid", invalid)))
    )

    orientation_classes = {
        "vertical": "flex-col [&>*]:w-full [&>.sr-only]:w-auto",
        "horizontal": (
            "flex-row items-center [&>[data-slot=field-label]]:flex-auto "
            "has-[>[data-slot=field-content]]:items-start "
            "has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px"
        ),
        "responsive": (
            "flex-col @md/field-group:flex-row @md/field-group:items-center [&>*]:w-full "
            "@md/field-group:[&>*]:w-auto [&>.sr-only]:w-auto "
            "@md/field-group:[&>[data-slot=field-label]]:flex-auto "
            "@md/field-group:has-[>[data-slot=field-content]]:items-start "
            "@md/field-group:has-[>[data-slot=field-content]]:[&>[role=checkbox],[role=radio]]:mt-px"
        ),
    }

    attributes = get_attributes(
        {
            "role": "group",
            "data-slot": "field",
            "data-orientation": resolved_orientation,
            "data-invalid": invalid_attr,
            "class": merge_classes(
                "group/field flex w-full gap-3 data-[invalid=true]:text-destructive",
                orientation_classes[resolved_orientation],
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attributes}>{children}</div>"


@component
def FieldContent(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "field-content",
            "class": merge_classes(
                "group/field-content flex flex-1 flex-col gap-1.5 leading-snug",
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attributes}>{children}</div>"


@component
def FieldLabel(
    asChild: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    computed_class = merge_classes(
        "group/field-label peer/field-label flex w-fit gap-2 leading-snug",
        "group-data-[disabled=true]/field:opacity-50",
        "has-[>[data-slot=field]]:w-full has-[>[data-slot=field]]:flex-col",
        "has-[>[data-slot=field]]:rounded-md has-[>[data-slot=field]]:border [&>*]:data-[slot=field]:p-4",
        "has-data-[state=checked]:border-primary has-data-[state=checked]:bg-primary/5",
        "dark:has-data-[state=checked]:bg-primary/10",
        incoming_class,
    )

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{
                "data-slot": "field-label",
                "class": computed_class,
                **props,
            },
        )

    proxy_script = _field_label_proxy_script()
    attributes = get_attributes(
        {
            "data-slot": "field-label",
            "pp-ref": "rootRef",
            "class": merge_classes(
                "flex items-center gap-2 text-sm leading-none font-medium select-none",
                "group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50",
                "peer-disabled:cursor-not-allowed peer-disabled:opacity-50",
                computed_class,
            ),
        },
        props,
    )

    return f"<label {attributes}>{children}{proxy_script}</label>"


@component
def FieldTitle(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "field-label",
            "class": merge_classes(
                "flex w-fit items-center gap-2 text-sm leading-snug font-medium",
                "group-data-[disabled=true]/field:opacity-50",
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attributes}>{children}</div>"


@component
def FieldDescription(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "field-description",
            "class": merge_classes(
                "text-sm leading-normal font-normal text-muted-foreground",
                "group-has-[[data-orientation=horizontal]]/field:text-balance",
                "last:mt-0 nth-last-2:-mt-1 [[data-variant=legend]+&]:-mt-1.5",
                "[&>a]:underline [&>a]:underline-offset-4 [&>a:hover]:text-primary",
                incoming_class,
            ),
        },
        props,
    )

    return f"<p {attributes}>{children}</p>"


@component
def FieldSeparator(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    has_content = bool(children and str(children).strip())

    attributes = get_attributes(
        {
            "data-slot": "field-separator",
            "data-content": "true" if has_content else "false",
            "class": merge_classes(
                "relative -my-2 h-5 text-sm group-data-[variant=outline]/field-group:-mb-2",
                incoming_class,
            ),
        },
        props,
    )

    separator = Separator(**{"class": "absolute inset-0 top-1/2"})
    if not has_content:
        return f"<div {attributes}>{separator}</div>"

    content_attributes = get_attributes(
        {
            "data-slot": "field-separator-content",
            "class": "relative mx-auto block w-fit bg-background px-2 text-muted-foreground",
        }
    )

    return (
        f"<div {attributes}>"
        f"{separator}"
        f"<span {content_attributes}>{children}</span>"
        f"</div>"
    )


@component
def FieldError(
    errors: Sequence[Mapping[str, Any] | str | None] | Mapping[str, Any] | str | None = None,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    messages = _normalize_error_messages(props.pop("errors", errors))

    if children:
        content = children
    elif len(messages) == 1:
        content = html.escape(messages[0])
    elif len(messages) > 1:
        items = "".join(f"<li>{html.escape(message)}</li>" for message in messages)
        content = f'<ul class="ml-4 flex list-disc flex-col gap-1">{items}</ul>'
    else:
        return ""

    attributes = get_attributes(
        {
            "role": "alert",
            "data-slot": "field-error",
            "class": merge_classes(
                "text-sm font-normal text-destructive",
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attributes}>{content}</div>"