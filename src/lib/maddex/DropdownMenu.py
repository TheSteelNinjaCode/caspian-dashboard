from typing import Literal, Optional

from casp.component_decorator import component, render_html
from casp.html_attrs import get_attributes, merge_classes
from casp.state_manager import StateManager
from markupsafe import Markup

from .Portal import Portal
from .Slot import Slot
from .utils import generate_id
from src.lib.ppicons.Check import Check
from src.lib.ppicons.ChevronRight import ChevronRight

DropdownMenuSide = Literal["top", "right", "bottom", "left"]
DropdownMenuAlign = Literal["start", "center", "end"]


def _parse_bool(value: bool | str | None, fallback: bool = False) -> bool:
    if value is None:
        return fallback

    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "on", ""}:
            return True
        if normalized in {"false", "0", "no", "off"}:
            return False

    return value is True


def _normalize_choice(value: str | None, allowed: set[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else fallback


@component
def DropdownMenu(
    open: Optional[str] = None,
    onOpenChange: Optional[str] = None,
    closeOnOutsideClick: bool | str = True,
    closeOnSelect: bool | str = True,
    id: Optional[str] = None,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    computed_class = merge_classes("relative inline-block text-left", incoming_class)

    dropdown_menu_event_id = generate_id("dropdown-menu")
    dropdown_menu_id = id or generate_id("dropdown-menu")
    dropdown_menu_trigger_id = generate_id("dropdown-trigger")

    StateManager.set_state("maddex-dropdown-menu-id", dropdown_menu_id)
    StateManager.set_state(
        "maddex-dropdown-menu-trigger-id", dropdown_menu_trigger_id,
    )

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu",
            "class": computed_class,
            "data-state": '{open ? "open" : "closed"}',
            "data-dropdown-menu-event-id": dropdown_menu_event_id,
            "data-close-on-outside-click": str(
                _parse_bool(closeOnOutsideClick, True)
            ).lower(),
            "data-close-on-select": str(_parse_bool(closeOnSelect, True)).lower(),
            "pp-ref": "rootRef",
        },
        props,
    )

    return render_html(
        "DropdownMenu.html",
        {
            "attributes": attrs,
            "children": children,
            "open": open,
            "onOpenChange": onOpenChange,
        },
    )


@component
def DropdownMenuTrigger(asChild: bool | str | None = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    dropdown_menu_trigger_id = StateManager.get_state(
        "maddex-dropdown-menu-trigger-id"
    )

    trigger_class = incoming_class
    if not as_child:
        trigger_class = merge_classes(
            "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
            incoming_class,
        )

    attributes = {
        "data-slot": "dropdown-menu-trigger",
        "type": "button",
        "aria-haspopup": "menu",
        "aria-expanded": "false",
        "aria-controls": StateManager.get_state("maddex-dropdown-menu-id"),
        "data-state": "closed",
        "pp-ref": "triggerRef",
        "class": trigger_class,
        "id": dropdown_menu_trigger_id,
    }

    if as_child:
        trigger = Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )
    else:
        attrs = get_attributes(attributes, props)
        trigger = Markup(
            f"""<button {attrs}>
<span class=\"sr-only\">Open menu</span>
{children}
</button>"""
        )

    return render_html(
        "DropdownMenuTrigger.html",
        {
            "trigger": trigger,
        },
    )


@component
def DropdownMenuContent(
    side: DropdownMenuSide | str = "bottom",
    align: DropdownMenuAlign | str = "center",
    sideOffset: int | str = 4,
    **props,
) -> str:
    normalized_side = _normalize_choice(
        side, {"top", "right", "bottom", "left"}, "bottom"
    )
    normalized_align = _normalize_choice(
        align, {"start", "center", "end"}, "center"
    )

    try:
        normalized_side_offset = max(float(sideOffset), 0)
    except (TypeError, ValueError):
        normalized_side_offset = 4.0

    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    dropdown_menu_id = StateManager.get_state("maddex-dropdown-menu-id")
    dropdown_menu_trigger_id = StateManager.get_state(
        "maddex-dropdown-menu-trigger-id"
    )

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-content",
            "role": "menu",
            "class": merge_classes(
                "fixed z-50 min-w-56 overflow-visible rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md outline-none pointer-events-auto data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
                incoming_class,
            ),
            "id": dropdown_menu_id,
            "aria-orientation": "vertical",
            "aria-labelledby": dropdown_menu_trigger_id,
            "data-state": "closed",
            "data-side": normalized_side,
            "data-align": normalized_align,
            "data-side-offset": str(normalized_side_offset),
            "tabindex": "-1",
        },
        props,
    )

    portal_attributes = get_attributes(
        {
            "style": "position: fixed; inset: 0; z-index: 50; display: none; pointer-events: none",
        }
    )
    script = render_html("DropdownMenuContentScript.js")

    return Portal(
        children=children,
        content_attributes=attrs,
        portal_attributes=portal_attributes,
        script=script,
    )


@component
def DropdownMenuGroup(asChild: bool | str | None = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    attributes = {
        "data-slot": "dropdown-menu-group",
        "class": merge_classes("", incoming_class),
        "role": "group",
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes(attributes, props)
    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuItem(
    inset: bool = False,
    asChild: bool | str | None = False,
    disabled: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    is_disabled = _parse_bool(props.pop("disabled", disabled))

    attributes = {
        "data-slot": "dropdown-menu-item",
        "role": "menuitem",
        "class": merge_classes(
            "relative flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground data-[highlighted=true]:bg-accent data-[highlighted=true]:text-accent-foreground data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
            "pl-8" if inset else "",
            incoming_class,
        ),
        "data-disabled": str(is_disabled).lower(),
        "data-menu-close-on-select": "true",
        "data-highlighted": "false",
        "tabindex": "-1",
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes(attributes, props)
    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuCheckboxItem(
    checked: bool | str = False,
    onCheckedChange: Optional[str] = None,
    disabled: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    is_checked = _parse_bool(checked)
    is_disabled = _parse_bool(props.pop("disabled", disabled))

    indicator = Check(class_name="h-4 w-4")
    indicator_html = (
        '<span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">'
        f'<span data-checkbox-indicator class="{"" if is_checked else "hidden"}">{indicator}</span>'
        "</span>"
    )

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-checkbox-item",
            "role": "menuitemcheckbox",
            "class": merge_classes(
                "relative flex cursor-default select-none items-center gap-2 rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground data-[highlighted=true]:bg-accent data-[highlighted=true]:text-accent-foreground data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
                incoming_class,
            ),
            "data-disabled": str(is_disabled).lower(),
            "data-menu-keep-open": "false",
            "data-checked": str(is_checked).lower(),
            "data-highlighted": "false",
            "aria-checked": str(is_checked).lower(),
            "tabindex": "-1",
        },
        props,
    )

    return render_html(
        "DropdownMenuCheckboxItem.html",
        {
            "attributes": attrs,
            "children": children,
            "indicator": Markup(indicator_html),
            "checked": is_checked,
            "rawChecked": checked,
            "disabled": is_disabled,
            "onCheckedChange": onCheckedChange,
        },
    )


@component
def DropdownMenuRadioGroup(
    value: Optional[str] = None,
    onValueChange: Optional[str] = None,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-radio-group",
            "class": merge_classes("", incoming_class),
            "value": value or "",
            "on-value-change": onValueChange,
            "data-value": value or "",
            "role": "group",
        },
        props,
    )

    return render_html(
        "DropdownMenuRadioGroup.html",
        {
            "attributes": attrs,
            "children": children,
        },
    )


@component
def DropdownMenuRadioItem(
    value: str,
    checked: bool | str | None = False,
    disabled: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    is_checked = _parse_bool(checked)
    is_disabled = _parse_bool(props.pop("disabled", disabled))

    indicator_html = (
        '<span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">'
        f'<span data-radio-indicator class="{"" if is_checked else "hidden"} size-2 rounded-full bg-current"></span>'
        "</span>"
    )

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-radio-item",
            "role": "menuitemradio",
            "class": merge_classes(
                "relative flex cursor-default select-none items-center gap-2 rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground data-[highlighted=true]:bg-accent data-[highlighted=true]:text-accent-foreground data-[disabled=true]:pointer-events-none data-[disabled=true]:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
                incoming_class,
            ),
            "data-disabled": str(is_disabled).lower(),
            "data-menu-keep-open": "false",
            "data-value": value,
            "data-checked": str(is_checked).lower(),
            "data-highlighted": "false",
            "aria-checked": str(is_checked).lower(),
            "tabindex": "-1",
        },
        props,
    )

    return f"<div {attrs}>{indicator_html}{children}</div>"


@component
def DropdownMenuLabel(inset: bool = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-label",
            "class": merge_classes(
                "px-2 py-1.5 text-xs font-semibold text-muted-foreground",
                "pl-8" if inset else "",
                incoming_class,
            ),
            "data-inset": str(inset).lower(),
        },
        props,
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuSeparator(**props) -> str:
    incoming_class = props.pop("class", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-separator",
            "role": "separator",
            "class": merge_classes("-mx-1 my-1 h-px bg-muted", incoming_class),
        },
        props,
    )

    return f"<div {attrs}></div>"


@component
def DropdownMenuShortcut(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-shortcut",
            "class": merge_classes("ml-auto text-xs tracking-widest opacity-60", incoming_class),
        },
        props,
    )

    return f"<span {attrs}>{children}</span>"


@component
def DropdownMenuSub(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub",
            "class": merge_classes("relative flex flex-col", incoming_class),
            "role": "none",
        },
        props,
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuSubTrigger(inset: bool = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    chevron_right_icon = ChevronRight(class_name="ml-auto h-4 w-4")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub-trigger",
            "role": "menuitem",
            "aria-haspopup": "menu",
            "aria-expanded": "false",
            "data-menu-keep-open": "true",
            "tabindex": "-1",
            "class": merge_classes(
                "flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent focus:text-accent-foreground hover:bg-accent hover:text-accent-foreground data-[highlighted=true]:bg-accent data-[highlighted=true]:text-accent-foreground data-[state=open]:bg-accent [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
                "pl-8" if inset else "",
                incoming_class,
            ),
            "data-highlighted": "false",
        },
        props,
    )

    return f"""<div {attrs}>
{children}
{chevron_right_icon}
</div>"""


@component
def DropdownMenuSubContent(
    side: DropdownMenuSide | str = "right",
    align: DropdownMenuAlign | str = "start",
    **props,
) -> str:
    normalized_side = _normalize_choice(
        side, {"top", "right", "bottom", "left"}, "right"
    )
    normalized_align = _normalize_choice(
        align, {"start", "center", "end"}, "start"
    )
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub-content",
            "role": "menu",
            "data-state": "closed",
            "aria-hidden": "true",
            "hidden": "true",
            "data-side": normalized_side,
            "data-align": normalized_align,
            "class": merge_classes(
                "fixed z-[60] min-w-[8rem] rounded-md border bg-popover p-1 text-popover-foreground shadow-lg outline-hidden data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=right]:data-[state=open]:slide-in-from-left-2 data-[side=right]:data-[state=closed]:slide-out-to-left-2 data-[side=left]:data-[state=open]:slide-in-from-right-2 data-[side=left]:data-[state=closed]:slide-out-to-right-2",
                incoming_class,
            ),
        },
        props,
    )

    return f"<div {attrs}>{children}</div>"
