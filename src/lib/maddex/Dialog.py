from typing import Optional

from casp.component_decorator import component, html
from casp.html_attrs import get_attributes, merge_classes
from markupsafe import Markup

from .Button import Button
from .Portal import Portal
from .Slot import Slot
from .utils import generate_id, parse_bool


def _render_dialog_content_script() -> Markup:
    return Markup(
        html(r"""
pp.layoutEffect(() => {
const portalEl = portalRef.current;
const contentEl = contentBoxRef.current;
if (!portalEl || !contentEl) return;

const initialParentDialog = portal.sourceParent?.closest('[data-slot="dialog"]');
if (!initialParentDialog) return;
const dialogInstanceId =
initialParentDialog.getAttribute("data-dialog-id") || null;

const getParentDialog = () => {
if (!dialogInstanceId) return initialParentDialog;

return (
document.querySelector(
`[data-slot="dialog"][data-dialog-id="${dialogInstanceId}"]`,
) || initialParentDialog
);
};

const overlay = portalEl.querySelector('[data-slot="dialog-overlay"]');
let previousState = null;
let closeTimer = null;
let pendingCloseHandler = null;
let restoreFocusTarget = null;
let observedDialog = null;
let dialogObserver = null;
const CLOSE_ANIMATION_FALLBACK_MS = 240;

const parseBool = (value) => value === true || value === "true";
const shouldCloseOnOverlayClick = () =>
parseBool(getParentDialog()?.getAttribute("data-close-on-overlay-click"));
const shouldResetOnOpen = () =>
parseBool(getParentDialog()?.getAttribute("data-reset-on-open"));

const disconnectDialogObserver = () => {
if (dialogObserver) {
dialogObserver.disconnect();
dialogObserver = null;
}
observedDialog = null;
};

const bindDialogObserver = () => {
const nextDialog = getParentDialog();
if (!nextDialog || nextDialog === observedDialog) return;

disconnectDialogObserver();
observedDialog = nextDialog;
dialogObserver = new MutationObserver(syncState);
dialogObserver.observe(nextDialog, {
attributes: true,
attributeFilter: [
"data-state",
"data-dialog-id",
"data-close-on-overlay-click",
"data-reset-on-open",
],
});
};

const clearCloseTimer = () => {
if (closeTimer !== null) {
clearTimeout(closeTimer);
closeTimer = null;
}
};

const clearPendingCloseHandler = () => {
if (pendingCloseHandler) {
contentEl.removeEventListener("animationend", pendingCloseHandler);
pendingCloseHandler = null;
}
};

const syncBodyOverflow = () => {
const hasOpenModal = document.querySelector(
'[data-slot="dialog"][data-state="open"], [data-slot="alert-dialog"][data-state="open"]',
);
document.body.style.overflow = hasOpenModal ? "hidden" : "";
};

const setPortalAccessibility = (isOpen) => {
portalEl.setAttribute("aria-hidden", isOpen ? "false" : "true");

if ("inert" in portalEl) {
portalEl.inert = !isOpen;
} else if (isOpen) {
portalEl.removeAttribute("inert");
} else {
portalEl.setAttribute("inert", "");
}
};

const focusableSelector =
'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

const moveFocusOutsidePortal = () => {
const activeElement = document.activeElement;
if (!(activeElement instanceof HTMLElement)) return;
if (!portalEl.contains(activeElement)) return;

const fallbackTarget =
restoreFocusTarget instanceof HTMLElement &&
document.contains(restoreFocusTarget) &&
!portalEl.contains(restoreFocusTarget)
? restoreFocusTarget
: getParentDialog()?.querySelector('[data-slot="dialog-trigger"]');

if (fallbackTarget instanceof HTMLElement) {
fallbackTarget.focus();
}

// The fallback target may be hidden or otherwise unfocusable
// (e.g. the dialog was opened from a menu item that has since
// closed). If focus is still inside the portal, blur it so focus
// is never trapped behind aria-hidden/inert.
if (portalEl.contains(document.activeElement)) {
activeElement.blur();
}
};

const focusDialog = () => {
const activeElement = document.activeElement;
restoreFocusTarget =
activeElement instanceof HTMLElement && !portalEl.contains(activeElement)
? activeElement
: getParentDialog()?.querySelector('[data-slot="dialog-trigger"]');

if (shouldResetOnOpen()) {
contentEl.scrollTop = 0;
}

const autoFocusEl =
contentEl.querySelector("[autofocus]") ||
contentEl.querySelector(focusableSelector);

(autoFocusEl || contentEl).focus?.();
};

const dispatchClose = () => {
const parentDialog = getParentDialog();
const closeDetail = {
dialogId: dialogInstanceId,
};

if (parentDialog) {
parentDialog.dispatchEvent(
new CustomEvent("dialog-close", {
bubbles: true,
composed: true,
detail: closeDetail,
}),
);
}

document.dispatchEvent(
new CustomEvent("dialog-close-request", {
detail: closeDetail,
}),
);
};

const finishClosedState = () => {
moveFocusOutsidePortal();
setPortalAccessibility(false);
portalEl.style.display = "none";
syncBodyOverflow();
};

const syncState = () => {
const parentDialog = getParentDialog();
if (!parentDialog) return;
bindDialogObserver();

const nextState = parentDialog.getAttribute("data-state") || "closed";
const isOpen = nextState === "open";

if (isOpen && previousState !== "open") {
portalEl.parentElement?.appendChild(portalEl);
clearCloseTimer();
clearPendingCloseHandler();
contentEl.setAttribute("data-state", "closed");
if (overlay) overlay.setAttribute("data-state", "closed");
portalEl.style.display = "";
setPortalAccessibility(true);
syncBodyOverflow();
queueMicrotask(() => {
if ((parentDialog.getAttribute("data-state") || "closed") !== "open") return;
contentEl.setAttribute("data-state", "open");
if (overlay) overlay.setAttribute("data-state", "open");
focusDialog();
});
} else if (!isOpen && previousState === "open") {
clearCloseTimer();
clearPendingCloseHandler();
contentEl.setAttribute("data-state", "closed");
if (overlay) overlay.setAttribute("data-state", "closed");

pendingCloseHandler = (event) => {
if (event.target !== contentEl) return;
clearPendingCloseHandler();
if ((parentDialog.getAttribute("data-state") || "closed") !== "closed") return;
finishClosedState();
};

contentEl.addEventListener("animationend", pendingCloseHandler);

closeTimer = window.setTimeout(() => {
clearPendingCloseHandler();
if ((parentDialog.getAttribute("data-state") || "closed") !== "closed") return;
finishClosedState();
}, CLOSE_ANIMATION_FALLBACK_MS);
} else if (previousState === null) {
if (isOpen) {
portalEl.style.display = "";
setPortalAccessibility(true);
contentEl.setAttribute("data-state", "open");
if (overlay) overlay.setAttribute("data-state", "open");
syncBodyOverflow();
} else {
contentEl.setAttribute("data-state", "closed");
if (overlay) overlay.setAttribute("data-state", "closed");
finishClosedState();
}
} else if (isOpen) {
portalEl.style.display = "";
setPortalAccessibility(true);
contentEl.setAttribute("data-state", "open");
if (overlay) overlay.setAttribute("data-state", "open");
syncBodyOverflow();
}

previousState = nextState;
};

bindDialogObserver();
syncState();
requestAnimationFrame(() => {
bindDialogObserver();
syncState();
});
const onDialogStateChange = (event) => {
if (event.detail?.dialogId !== dialogInstanceId) return;
bindDialogObserver();
syncState();
};

const onOverlayClick = (event) => {
if (!shouldCloseOnOverlayClick()) return;
if (event.target === overlay) {
event.stopPropagation();
dispatchClose();
}
};

const onContentClick = (event) => {
const target = event.target instanceof Element ? event.target : null;
const closeTarget = target?.closest("[data-dialog-close='true']");
if (!closeTarget) return;

event.stopPropagation();
dispatchClose();
};

const onKeyDown = (event) => {
if (event.key === "Escape") {
event.preventDefault();
dispatchClose();
}
};

if (overlay) overlay.addEventListener("click", onOverlayClick);
contentEl.addEventListener("click", onContentClick);
document.addEventListener("keydown", onKeyDown);
document.addEventListener("dialog-state-change", onDialogStateChange);

return () => {
clearCloseTimer();
clearPendingCloseHandler();
disconnectDialogObserver();
if (overlay) overlay.removeEventListener("click", onOverlayClick);
contentEl.removeEventListener("click", onContentClick);
document.removeEventListener("keydown", onKeyDown);
document.removeEventListener("dialog-state-change", onDialogStateChange);
setPortalAccessibility(false);
syncBodyOverflow();
};
}, []);
""")
    )


@component
def Dialog(
    open: Optional[str] = None,
    onOpenChange: Optional[str] = None,
    closeOnOverlayClick: bool | str = True,
    resetOnOpen: bool | str = False,
    id: Optional[str] = None,
    **props,
):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("", incoming_class)

    children = props.pop("children", "")
    close_on_overlay_click = parse_bool(props.pop("closeOnOverlayClick", closeOnOverlayClick), True)
    reset_on_open = parse_bool(props.pop("resetOnOpen", resetOnOpen), False)
    open = props.pop("open", open)
    onOpenChange = props.pop("onOpenChange", onOpenChange)
    dialog_id = props.pop("id", id)
    dialog_instance_id = dialog_id or generate_id("dialog")

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog",
            "data-state": '{open ? "open" : "closed"}',
            "data-dialog-id": dialog_instance_id,
            "data-close-on-overlay-click": str(close_on_overlay_click).lower(),
            "data-reset-on-open": str(reset_on_open).lower(),
            "id": dialog_id,
            "pp-ref": "rootRef",
        },
        props,
    )

    return html(r"""
<div is-open="{{ open }}" on-open-change="{{ onOpenChange }}">
  <div {{ attributes }}>{{ children }}</div>

  <script>
    const normalizeControlledValue = (value) => {
      if (value == null) return undefined;
      if (typeof value !== "string") return value;

      const normalized = value.trim().toLowerCase();
      if (
        normalized === "" ||
        normalized === "none" ||
        normalized === "null" ||
        normalized === "undefined"
      ) {
        return undefined;
      }

      return value;
    };

    const rawOpen = pp.props.isOpen ?? {{ open | json }};
    const onOpenChange = pp.props.onOpenChange;
    const controlledOpen = normalizeControlledValue(rawOpen);
    const isControlled = controlledOpen !== undefined;

    const parseBool = (value) => {
      if (value === true) return true;
      if (typeof value === "string") {
        return value.trim().toLowerCase() === "true";
      }
      return false;
    };

    const [internalOpen, setInternalOpen] = pp.state(false);
    const open = isControlled ? parseBool(controlledOpen) : internalOpen;
    const rootRef = pp.ref();
    const dialogInstanceId = {{ dialog_instance_id | json }};

    const updateOpen = (shouldBeOpen) => {
      if (isControlled) {
        if (typeof onOpenChange === "function") {
          onOpenChange(shouldBeOpen);
        }
      } else {
        setInternalOpen(shouldBeOpen);
      }

      rootRef.current?.dispatchEvent(
        new CustomEvent("open-change", {
          detail: shouldBeOpen,
          bubbles: true,
        }),
      );
    };

    const openDialog = () => updateOpen(true);
    const closeDialog = () => updateOpen(false);

    const onOpen = (event) => {
      event.stopPropagation();
      openDialog();
    };

    const onClose = (event) => {
      event.stopPropagation();
      closeDialog();
    };

    const onDocumentCloseRequest = (event) => {
      if (event.detail?.dialogId !== dialogInstanceId) return;
      closeDialog();
    };

    pp.layoutEffect(() => {
      const root = rootRef.current;
      if (!root) return;

      const nextState = open ? "open" : "closed";
      root.setAttribute("data-state", nextState);
      root.setAttribute("data-dialog-id", dialogInstanceId);
      document.dispatchEvent(
        new CustomEvent("dialog-state-change", {
          detail: {
            dialogId: dialogInstanceId,
            state: nextState,
          },
        }),
      );
    }, [open]);

    pp.effect(() => {
      const el = rootRef.current;
      if (!el) return;

      el.addEventListener("dialog-open", onOpen);
      el.addEventListener("dialog-close", onClose);
      document.addEventListener("dialog-close-request", onDocumentCloseRequest);

      return () => {
        el.removeEventListener("dialog-open", onOpen);
        el.removeEventListener("dialog-close", onClose);
        document.removeEventListener("dialog-close-request", onDocumentCloseRequest);
      };
    }, []);
  </script>
</div>
""",
        children=children,
        attributes=attributes,
        dialog_instance_id=dialog_instance_id,
        open=open,
        onOpenChange=onOpenChange,
    )


@component
def DialogTrigger(
    asChild: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("", incoming_class)
    children = props.pop("children", "")

    attributes = {
        "class": final_class,
        "data-slot": "dialog-trigger",
        "type": "button",
        "pp-ref": "triggerRef",
    }

    as_child = parse_bool(props.pop("asChild", asChild))

    if as_child:
        trigger = Slot(
            children=children,
            asChild=True,
            **attributes,
            **props,
        )
    else:
        final_attributes = get_attributes(attributes, props)
        trigger = Markup(f"<button {final_attributes}>{children}</button>")

    return html(r"""
<div>
  {{ trigger }}

  <script>
    const triggerRef = pp.ref();

    const handleClick = () => {
      triggerRef.current?.dispatchEvent(
        new CustomEvent("dialog-open", {
          bubbles: true,
          composed: true,
        }),
      );
    };

    pp.effect(() => {
      const el = triggerRef.current;
      if (!el) return;

      el.addEventListener("click", handleClick);
      return () => el.removeEventListener("click", handleClick);
    }, []);
  </script>
</div>
""",
        trigger=trigger,
    )


@component
def DialogClose(
    asChild: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("", incoming_class)
    children = props.pop("children", "")
    as_child = parse_bool(props.pop("asChild", asChild))

    attr_dict = {
        "class": final_class,
        "data-slot": "dialog-close",
        "data-dialog-close": "true",
        "type": "button",
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **attr_dict,
            **props,
        )

    attributes = get_attributes(attr_dict, props)

    return html(r"""<button {{ attributes }}>{{ children }}</button>""",
        attributes=attributes,
        children=children,
    )


@component
def DialogOverlay(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "fixed inset-0 isolate z-50 bg-black/10 duration-200 "
        "supports-backdrop-filter:backdrop-blur-xs data-[state=closed]:pointer-events-none "
        "data-[state=open]:animate-in data-[state=open]:fade-in-0 "
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-overlay",
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def DialogContent(
    showCloseButton: bool | str | None = True,
    **props,
):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "fixed top-1/2 left-1/2 z-50 grid w-full max-w-[min(24rem,calc(100vw-2rem))] "
        "-translate-x-1/2 -translate-y-1/2 gap-4 rounded-xl bg-popover p-4 text-sm text-popover-foreground "
        "ring-1 ring-foreground/10 duration-200 outline-none "
        "data-[state=closed]:pointer-events-none "
        "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 "
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
        incoming_class,
    )

    children = props.pop("children", "")
    show_close_button = parse_bool(props.pop("showCloseButton", showCloseButton), True)

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-content",
            "tabindex": "-1",
            "data-state": "closed",
        },
        props,
    )

    close_btn = ""
    if show_close_button:
        close_btn = DialogClose(
            asChild=True,
            children=Button(
                variant="ghost",
                size="icon-sm",
                **{"class": "absolute top-2 right-2"},
                children='<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg><span class="sr-only">Close</span>',
            ),
        )

    overlay = DialogOverlay()
    portal_attributes = get_attributes(
        {
            "style": "z-index: 50; display: none;",
            "aria-hidden": "true",
            "inert": "",
        }
    )
    script = _render_dialog_content_script()

    return Portal(
        children=children,
        content_attributes=attributes,
        portal_attributes=portal_attributes,
        overlay=overlay,
        close=close_btn,
        script=script,
    )


@component
def DialogHeader(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("flex flex-col gap-2", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-header",
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def DialogFooter(
    showCloseButton: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "-mx-4 -mb-4 flex flex-col-reverse gap-2 rounded-b-xl border-t bg-muted/50 p-4 sm:flex-row sm:justify-end",
        incoming_class,
    )

    children = props.pop("children", "")
    show_close_button = parse_bool(props.pop("showCloseButton", showCloseButton), False)

    if show_close_button:
        children = f"{children}{DialogClose(asChild=True, children=Button(variant='outline', children='Close'))}"

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-footer",
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def DialogTitle(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "cn-font-heading text-base leading-none font-medium", incoming_class
    )

    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-title",
        },
        props,
    )

    return html(r"""<h2 {{ attributes }}>{{ children }}</h2>""", attributes=attributes, children=children
    )


@component
def DialogDescription(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "text-sm text-muted-foreground *:[a]:underline *:[a]:underline-offset-3 *:[a]:hover:text-foreground",
        incoming_class,
    )

    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "class": final_class,
            "data-slot": "dialog-description",
        },
        props,
    )

    return html(r"""<p {{ attributes }}>{{ children }}</p>""", attributes=attributes, children=children
    )
