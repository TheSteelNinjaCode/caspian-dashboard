from typing import Optional
from casp.component_decorator import component, render_html
from casp.html_attrs import merge_classes, get_attributes
from casp.state_manager import StateManager
from .Portal import Portal
from .Slot import Slot
from .utils import generate_id


@component
def AlertDialog(
    open: Optional[str] = None,
    onOpenChange: Optional[str] = None,
    closeOnOverlayClick: bool | str = True,
    resetOnOpen: bool | str = False,
    overlayClass: Optional[str] = None,
    id: Optional[str] = None,
    **props,
) -> str:
    dialog_id = id if id else generate_id("alert-dialog-")
    portal_id = generate_id("alert-dialog-portal-")

    StateManager.set_state('alert_portal_id', portal_id)
    StateManager.set_state('alert_overlay_class', overlayClass)

    computed_class = merge_classes(props.pop("class", ""))
    children = props.pop("children", "")
    close_on_overlay_click = closeOnOverlayClick in (True, "true", "")
    reset_on_open = resetOnOpen in (True, "true", "")

    attributes = get_attributes(
        {
            "data-slot": "alert-dialog",
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
        "AlertDialog.html",
        attributes=attributes,
        children=children,
        dialog_id=dialog_id,
        id=dialog_id,
        portal_id=portal_id,
    )


@component
def AlertDialogTrigger(
    asChild: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(incoming_class)

    attributes = {
        "data-slot": "alert-dialog-trigger",
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

    final_attributes = get_attributes(attributes, props)
    return f"<button {final_attributes}>{children}</button>"


@component
def AlertDialogOverlay(**props) -> str:
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
        {"data-slot": "alert-dialog-overlay", "class": computed_class}, props)

    return f"<div {attributes}>{children}</div>"


@component
def AlertDialogContent(
    disable_portal: bool = False,
    portal_to: str = "body",
    portal_id: Optional[str] = None,
    overlay_class: str = "",
    **props,
) -> str:
    use_portal_id = portal_id if portal_id else StateManager.get_state(
        'alert_portal_id')
    overlay_class = overlay_class if overlay_class else StateManager.get_state(
        'alert_overlay_class')

    base_classes = (
        "bg-background data-[state=open]:animate-in data-[state=closed]:animate-out "
        "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 "
        "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 "
        "fixed top-[50%] left-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] "
        "translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 "
        "shadow-lg duration-200 sm:max-w-lg"
    )

    incoming_class = props.pop("class", "")
    computed_class = merge_classes(base_classes, incoming_class)
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "alert-dialog-content",
            "tabindex": "-1",
            "data-state": "closed",
            "data-portal-id": use_portal_id,
            "class": computed_class,
        },
        props
    )

    overlay = AlertDialogOverlay(class_name=overlay_class)

    inner = f"""
    <div>
        {overlay}
        <div {attributes}>
            {children}
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
def AlertDialogHeader(**props) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "flex flex-col gap-2 text-center sm:text-left",
        incoming_class
    )
    children = props.pop("children", "")
    attributes = get_attributes(
        {"data-slot": "alert-dialog-header", "class": computed_class}, props)

    return f"<div {attributes}>{children}</div>"


@component
def AlertDialogFooter(**props) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "flex flex-col-reverse gap-2 sm:flex-row sm:justify-end",
        incoming_class
    )
    children = props.pop("children", "")
    attributes = get_attributes(
        {"data-slot": "alert-dialog-footer", "class": computed_class}, props)

    return f"<div {attributes}>{children}</div>"


@component
def AlertDialogTitle(**props) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "text-lg font-semibold",
        incoming_class
    )
    children = props.pop("children", "")
    attributes = get_attributes(
        {"data-slot": "alert-dialog-title", "class": computed_class}, props)

    return f"<h3 {attributes}>{children}</h3>"


@component
def AlertDialogDescription(**props) -> str:
    incoming_class = props.pop("class", "")
    computed_class = merge_classes(
        "text-muted-foreground text-sm",
        incoming_class
    )
    children = props.pop("children", "")
    attributes = get_attributes(
        {"data-slot": "alert-dialog-description", "class": computed_class}, props)

    return f"<p {attributes}>{children}</p>"


@component
def AlertDialogAction(**props) -> str:
    incoming_class = props.pop("class", "")
    base_btn_class = (
        "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md "
        "text-sm font-medium transition-colors focus-visible:outline-none "
        "focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none "
        "disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 "
        "bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2"
    )

    computed_class = merge_classes(
        base_btn_class,
        incoming_class
    )

    attributes = get_attributes(
        {
            "data-slot": "alert-dialog-action",
            "type": "button",
            "class": computed_class
        },
        props
    )
    children = props.pop("children", "")

    return f"<button {attributes}>{children}</button>"


@component
def AlertDialogCancel(**props) -> str:
    incoming_class = props.pop("class", "")
    base_btn_class = (
        "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md "
        "text-sm font-medium transition-colors focus-visible:outline-none "
        "focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none "
        "disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0 "
        "border border-input bg-background shadow-sm hover:bg-accent "
        "hover:text-accent-foreground h-9 px-4 py-2"
    )

    computed_class = merge_classes(
        base_btn_class,
        incoming_class
    )

    attributes = get_attributes(
        {
            "data-slot": "alert-dialog-close",
            "type": "button",
            "class": computed_class
        },
        props
    )
    children = props.pop("children", "")

    return f"<button {attributes}>{children}</button>"
