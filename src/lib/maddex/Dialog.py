from typing import Optional
from casp.component_decorator import component, render_html
from casp.html_attrs import merge_classes, get_attributes
from casp.state_manager import StateManager
from .Portal import Portal
from .Slot import Slot
from ..ppicons.X import X
from .utils import generate_id


@component
def Dialog(
    open: Optional[str] = None,
    onOpenChange: Optional[str] = None,
    closeOnOverlayClick: bool | str = True,
    resetOnOpen: bool | str = False,
    overlayClass: Optional[str] = None,
    id: Optional[str] = None,
    **props,
) -> str:
    dialog_id = id if id else generate_id("dialog-")
    final_portal_id = generate_id("dialog-portal-")

    StateManager.set_state('portal_id', final_portal_id)
    StateManager.set_state('overlay_class', overlayClass)

    computed_class = merge_classes(props.pop("class", ""))
    children = props.pop("children", "")
    close_on_overlay_click = closeOnOverlayClick in (True, "true", "")
    reset_on_open = resetOnOpen in (True, "true", "")

    attributes = get_attributes(
        {
            "data-slot": "dialog",
            "data-state": "{open ? 'open' : 'closed'}",
            "id": dialog_id,
            "class": computed_class,
            "open": open,
            "onOpenChange": onOpenChange,
            "closeonoverlayclick": close_on_overlay_click,
            "resetonopen": reset_on_open,
        },
        props
    )

    return render_html(
        "Dialog.html",
        attributes=attributes,
        children=children,
        dialog_id=dialog_id,
        final_portal_id=final_portal_id,
    )


@component
def DialogTrigger(
    asChild: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(incoming_class)

    attributes = {
        "data-slot": "dialog-trigger",
        "type": "button",
        "class": computed_class
    }

    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **attributes
        )

    final_attributes = get_attributes(
        {
            "data-slot": "dialog-trigger",
            "type": "button",
            "class": computed_class
        },
        props
    )
    return f"<button {final_attributes}>{children}</button>"


@component
def DialogClose(
    asChild: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(incoming_class)

    attributes_dict = {
        "data-slot": "dialog-close",
        "type": "button",
        "class": computed_class
    }
    final_attributes = get_attributes(attributes_dict, props)
    children = props.pop("children", "")
    as_child = props.pop("asChild", asChild) in (True, "true", "")

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **attributes_dict
        )

    return f"""
<button {final_attributes}>
    {children}
    <span class="sr-only">Close</span>
</button>
"""


@component
def DialogOverlay(**props) -> str:
    base_classes = (
        "data-[state=open]:animate-in data-[state=closed]:animate-out "
        "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 "
        "fixed inset-0 z-50 bg-black/50"
    )
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    computed_class = merge_classes(
        base_classes, incoming_class)
    attributes = get_attributes(
        {"data-slot": "dialog-overlay", "class": computed_class}, props)
    return f"""<div {attributes}>{children}</div>"""


@component
def DialogContent(
    disable_portal: bool = False,
    portal_to: str = "body",
    portal_id: Optional[str] = None,
    overlay_class: str = "",
    **props,
) -> str:
    use_portal_id = portal_id if portal_id else StateManager.get_state(
        'portal_id')
    overlay_class = overlay_class if overlay_class else StateManager.get_state(
        'overlay_class')
    base_classes = (
        "bg-background data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 fixed top-[50%] left-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg duration-200 sm:max-w-lg"
    )
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(base_classes, incoming_class)
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "dialog-content",
            "tabindex": "-1",
            "data-state": "closed",
            "data-portal-id": use_portal_id,
            "class": computed_class,
        },
        props
    )

    close_icon = X(class_name="size-4")
    close_btn = DialogClose(
        children=close_icon,
        class_name=(
            "ring-offset-background focus:ring-ring data-[state=open]:bg-accent "
            "data-[state=open]:text-muted-foreground absolute top-4 right-4 rounded-xs "
            "opacity-70 transition-opacity hover:opacity-100 focus:ring-2 "
            "focus:ring-offset-2 focus:outline-hidden disabled:pointer-events-none "
            "[&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4 z-50"
        )
    )
    overlay = DialogOverlay(class_name=overlay_class)

    inner = f"""
<div>
    {overlay}
    <div {attributes}>
        {children}
        {close_btn}
    </div>
</div>
"""

    if disable_portal:
        return inner

    return Portal(
        children=inner,
        to=portal_to,
        id=use_portal_id,
        hidden="true"
    )


@component
def DialogHeader(**props) -> str:
    computed_class = merge_classes(
        "flex flex-col gap-2 text-center sm:text-left", props.pop("class", ""))
    children = props.pop("children", "")

    attributes = get_attributes(
        {"data-slot": "dialog-header", "class": computed_class}, props)

    return f"<div {attributes}>{children}</div>"


@component
def DialogFooter(**props) -> str:
    computed_class = merge_classes(
        "flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", props.pop("class", ""))
    children = props.pop("children", "")

    attributes = get_attributes(
        {"data-slot": "dialog-footer", "class": computed_class}, props)

    return f"<div {attributes}>{children}</div>"


@component
def DialogTitle(**props) -> str:
    computed_class = merge_classes(
        "text-lg leading-none font-semibold", props.pop("class", ""))
    children = props.pop("children", "")

    attributes = get_attributes(
        {"data-slot": "dialog-title", "class": computed_class}, props)

    return f"<h3 {attributes}>{children}</h3>"


@component
def DialogDescription(**props) -> str:
    computed_class = merge_classes(
        "text-muted-foreground text-sm", props.pop("class", ""))
    children = props.pop("children", "")
    attributes = get_attributes(
        {"data-slot": "dialog-description", "class": computed_class}, props)

    return f"<p {attributes}>{children}</p>"
