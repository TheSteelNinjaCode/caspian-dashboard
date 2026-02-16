from .Slot import Slot
from casp.state_manager import StateManager
from casp.component_decorator import component, render_html
from casp.html_attrs import merge_classes, get_attributes
from .utils import generate_id
from src.lib.ppicons.ChevronRight import ChevronRight
from src.lib.ppicons.Check import Check


@component
def DropdownMenu(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    base_classes = "relative inline-block text-left"
    computed_class = merge_classes(base_classes, incoming_class)

    dropdown_menu_id = props.pop("id", generate_id("dropdown-menu-"))
    dropdown_menu_trigger_id = generate_id("dropdown-trigger-")
    StateManager.set_state("maddex-dropdown-menu-id", dropdown_menu_id)
    StateManager.set_state(
        "maddex-dropdown-menu-trigger-id", dropdown_menu_trigger_id)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu",
            "class": computed_class,
        },
        props
    )

    return render_html("DropdownMenu.html", attributes=attrs, children=children, id=dropdown_menu_id, trigger_id=dropdown_menu_trigger_id)


@component
def DropdownMenuSub(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = "flex flex-col relative group/sub"
    computed_class = merge_classes(base_classes, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub",
            "class": computed_class,
            "role": "none"
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuTrigger(asChild: bool | str | None = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    base_classes = (
        "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors "
        "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring "
        "disabled:pointer-events-none disabled:opacity-50"
    )

    computed_class = merge_classes(base_classes, incoming_class)
    dropdown_menu_trigger_id = StateManager.get_state(
        "maddex-dropdown-menu-trigger-id")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-trigger",
            "type": "button",
            "aria-haspopup": "true",
            "aria-expanded": "false",
            "class": computed_class,
            "id": dropdown_menu_trigger_id
        },
        props
    )

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{
                "class": computed_class,
                "data-slot": "dropdown-menu-trigger",
                "aria-haspopup": "true",
                "aria-expanded": "false",
                "id": dropdown_menu_trigger_id,
                **props}
        )

    return f"""<button {attrs}>
<span class="sr-only">Open menu</span>
{children}
</button>"""


@component
def DropdownMenuSubTrigger(inset: bool = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = (
        "flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-none "
        "focus:bg-accent data-[state=open]:bg-accent "
        "hover:bg-accent hover:text-accent-foreground "
        "group-hover/sub:bg-accent group-hover/sub:text-accent-foreground"
    )

    inset_class = "pl-8" if inset else ""
    computed_class = merge_classes(base_classes, inset_class, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub-trigger",
            "role": "menuitem",
            "aria-haspopup": "true",
            "aria-expanded": "false",
            "class": computed_class,
        },
        props
    )

    chevron_right_icon = ChevronRight(class_name="ml-auto h-4 w-4")

    return f"""<div {attrs}>
    {children}
    {chevron_right_icon}
</div>"""


@component
def DropdownMenuContent(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    dropdown_menu_id = StateManager.get_state("maddex-dropdown-menu-id")

    base_classes = (
        "hidden absolute right-0 z-50 mt-1 w-48 min-w-32 origin-top-right rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md"
    )

    computed_class = merge_classes(base_classes, incoming_class)
    dropdown_menu_trigger_id = StateManager.get_state(
        "maddex-dropdown-menu-trigger-id")

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-content",
            "role": "menu",
            "class": computed_class,
            "id": dropdown_menu_id,
            "aria-orientation": "vertical",
            "aria-labelledby": dropdown_menu_trigger_id,
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuSubContent(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = (
        "z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-lg "
        "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 "
        "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95"
    )

    interaction_classes = (
        "hidden group-hover/sub:block absolute left-full top-0 shadow-none "
        "before:absolute before:-left-1 before:top-0 before:h-full before:w-2 before:content-['']"
    )

    computed_class = merge_classes(
        base_classes, interaction_classes, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-sub-content",
            "role": "menu",
            "class": computed_class,
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuItem(inset: bool = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = (
        "relative flex cursor-default select-none items-center gap-2 rounded-sm px-2 py-1.5 text-sm outline-hidden transition-colors "
        "focus:bg-accent focus:text-accent-foreground "
        "hover:bg-accent hover:text-accent-foreground "
        "data-[disabled]:pointer-events-none data-[disabled]:opacity-50 "
        "[&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0"
    )

    inset_class = "pl-8" if inset else ""
    computed_class = merge_classes(base_classes, inset_class, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-item",
            "role": "menuitem",
            "class": computed_class,
            "tabindex": "-1",
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuGroup(asChild: bool | str | None = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")
    computed_class = merge_classes("", incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-group",
            "class": computed_class,
            "role": "group",
        },
        props
    )

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{"class": computed_class, **props}
        )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuLabel(inset: bool = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = "text-muted-foreground px-1.5 py-1 text-xs font-medium"
    inset_class = "pl-8" if inset else ""

    computed_class = merge_classes(base_classes, inset_class, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-label",
            "class": computed_class,
            "data-inset": str(inset).lower(),
        },
        props
    )

    return f"<div {attrs}>{children}</div>"


@component
def DropdownMenuSeparator(**props) -> str:
    incoming_class = props.pop("class", "")

    base_classes = "-mx-1 my-1 h-px bg-muted"
    computed_class = merge_classes(base_classes, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-separator",
            "role": "separator",
            "class": computed_class,
        },
        props
    )

    return f"<div {attrs}></div>"


@component
def DropdownMenuShortcut(**props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = "ml-auto text-xs tracking-widest opacity-60"
    computed_class = merge_classes(base_classes, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-shortcut",
            "class": computed_class,
        },
        props
    )

    return f"<span {attrs}>{children}</span>"

@component
def DropdownMenuCheckboxItem(
    checked: bool = False,
    **props
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    base_classes = (
        "relative flex cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 "
        "text-sm outline-none transition-colors focus:bg-accent focus:text-accent-foreground "
        "data-[disabled]:pointer-events-none data-[disabled]:opacity-50 hover:bg-accent hover:text-accent-foreground"
    )

    computed_class = merge_classes(base_classes, incoming_class)

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-checkbox-item",
            "role": "menuitemcheckbox",
            "aria-checked": str(checked).lower(),
            "class": computed_class,
        },
        props
    )
    
    check_icon = Check(class_name="h-4 w-4")

    icon_html = ""
    if checked:
        icon_html = (
            '<span class="absolute right-2 flex h-3.5 w-3.5 items-center justify-center">'
            f'{check_icon}'
            '</span>'
        )

    return f"<div {attrs}>{children}{icon_html}</div>"
