import random
from typing import Literal, Optional

from casp.component_decorator import component, html
from casp.html_attrs import get_attributes, merge_classes

from src.lib.ppicons.PanelLeft import PanelLeft

from .Button import Button
from .Separator import Separator
from .Skeleton import Skeleton
from .Slot import Slot
from .utils import parse_bool, pop_prop_alias

SidebarSide = Literal["left", "right"]
SidebarVariant = Literal["sidebar", "floating", "inset"]
SidebarCollapsible = Literal["offcanvas", "icon", "none"]
SidebarMenuButtonVariant = Literal["default", "outline"]
SidebarMenuButtonSize = Literal["default", "sm", "lg"]
SidebarMenuSubButtonSize = Literal["sm", "md"]


def _normalize_choice(value: str | None, allowed: set[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else fallback


def _join_styles(*parts: str) -> str:
    normalized_parts: list[str] = []

    for part in parts:
        cleaned = (part or "").strip()
        if not cleaned:
            continue

        normalized_parts.append(cleaned.rstrip(";"))

    return "; ".join(normalized_parts)


def sidebar_menu_button_style(
    variant: SidebarMenuButtonVariant | str = "default",
    size: SidebarMenuButtonSize | str = "default",
    *class_names: str,
) -> str:
    normalized_variant = _normalize_choice(
        variant,
        {"default", "outline"},
        "default",
    )
    normalized_size = _normalize_choice(
        size,
        {"default", "sm", "lg"},
        "default",
    )

    base_class = (
        "peer/menu-button flex w-full items-center gap-2 overflow-hidden rounded-md p-2 "
        "text-left text-sm ring-sidebar-ring outline-hidden transition-[width,height,padding] "
        "group-has-data-[sidebar=menu-action]/menu-item:pr-8 group-data-[collapsible=icon]:size-8! "
        "group-data-[collapsible=icon]:p-2! hover:bg-sidebar-accent hover:text-sidebar-accent-foreground "
        "focus-visible:ring-2 active:bg-sidebar-accent active:text-sidebar-accent-foreground "
        "disabled:pointer-events-none disabled:opacity-50 aria-disabled:pointer-events-none "
        "aria-disabled:opacity-50 data-[active=true]:bg-sidebar-accent data-[active=true]:font-medium "
        "data-[active=true]:text-sidebar-accent-foreground data-[state=open]:hover:bg-sidebar-accent "
        "data-[state=open]:hover:text-sidebar-accent-foreground [&>span:last-child]:truncate "
        "[&_svg]:size-4 [&_svg]:shrink-0"
    )

    variant_classes = {
        "default": "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
        "outline": (
            "bg-background shadow-[0_0_0_1px_hsl(var(--sidebar-border))] "
            "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground "
            "hover:shadow-[0_0_0_1px_hsl(var(--sidebar-accent))]"
        ),
    }

    size_classes = {
        "default": "h-8 text-sm",
        "sm": "h-7 text-xs",
        "lg": "h-12 text-sm group-data-[collapsible=icon]:p-0!",
    }

    return merge_classes(
        base_class,
        variant_classes[normalized_variant],
        size_classes[normalized_size],
        *class_names,
    )


@component
def SidebarProvider(
    defaultOpen: bool | str = True,
    open: Optional[str] = None,
    onOpenChange: Optional[str] = None,
    **props,
):
    incoming_class = props.pop("class", "")
    incoming_style = props.pop("style", "")
    children = props.pop("children", "")

    initial_open = parse_bool(open if open is not None else defaultOpen, True)
    style_value = _join_styles(
        "--sidebar-width: 16rem",
        "--sidebar-width-mobile: 18rem",
        "--sidebar-width-icon: 3rem",
        incoming_style,
    )

    attributes = get_attributes(
        {
            "class": merge_classes(
                "group/sidebar-wrapper flex min-h-svh w-full has-data-[variant=inset]:bg-sidebar",
                incoming_class,
            ),
            "data-slot": "sidebar-wrapper",
            "data-sidebar-provider": "true",
            "data-state": "expanded" if initial_open else "collapsed",
            "data-open": "true" if initial_open else "false",
            "data-mobile": "false",
            "data-mobile-open": "false",
            "style": style_value,
            "open": open,
            "default-open": defaultOpen,
            "on-open-change": onOpenChange,
            "pp-ref": "rootRef",
        },
        props,
    )

    # html
    return html(r"""
<div {{ attributes }}>
  {{ children }}

  <script>
    const SIDEBAR_COOKIE_NAME = "sidebar_state";
    const SIDEBAR_COOKIE_MAX_AGE = 60 * 60 * 24 * 7;
    const SIDEBAR_KEYBOARD_SHORTCUT = "b";
    const SIDEBAR_MEDIA_QUERY = "(max-width: 767px)";

    const normalizeSentinel = (value) => {
      if (value == null) return undefined;

      if (typeof value === "string") {
        const normalized = value.trim().toLowerCase();
        if (["", "none", "null", "undefined"].includes(normalized)) {
          return undefined;
        }
      }

      return value;
    };

    const parseBool = (value, fallback = false) => {
      if (value === true) return true;
      if (value === false) return false;
      if (value == null) return fallback;
      if (typeof value !== "string") return Boolean(value);

      const normalized = value.trim().toLowerCase();
      if (["true", "1", "yes", "on", "", "{true}"].includes(normalized)) return true;
      if (["false", "0", "no", "off", "none", "null", "undefined", "{false}"].includes(normalized)) return false;
      return fallback;
    };

    const rootRef = pp.ref();
    const mediaQueryRef = pp.ref(null);
    const controlledOpen = normalizeSentinel(pp.props.open);
    const isControlled = controlledOpen !== undefined;
    const initialOpen = parseBool(
      controlledOpen ?? pp.props.defaultOpen,
      true,
    );
    const initialMobile =
      typeof window !== "undefined" && typeof window.matchMedia === "function"
        ? window.matchMedia(SIDEBAR_MEDIA_QUERY).matches
        : false;

    const openRef = pp.ref(initialOpen);
    const stateRef = pp.ref(initialOpen ? "expanded" : "collapsed");
    const mobileRef = pp.ref(initialMobile);
    const mobileOpenRef = pp.ref(false);
    const controlledRef = pp.ref(isControlled);
    const onOpenChangeRef = pp.ref(pp.props.onOpenChange);

    const writeCookie = (nextOpen) => {
      if (typeof document === "undefined") return;
      document.cookie = `${SIDEBAR_COOKIE_NAME}=${nextOpen}; path=/; max-age=${SIDEBAR_COOKIE_MAX_AGE}`;
    };

    const syncDom = () => {
      const root = rootRef.current;
      if (!(root instanceof HTMLElement)) return;

      root.dataset.state = stateRef.current;
      root.dataset.open = openRef.current ? "true" : "false";
      root.dataset.mobile = mobileRef.current ? "true" : "false";
      root.dataset.mobileOpen = mobileOpenRef.current ? "true" : "false";

      root.querySelectorAll("[data-slot='sidebar']").forEach((node) => {
        if (!(node instanceof HTMLElement)) return;

        const collapsibleMode = (node.getAttribute("data-collapsible-mode") || "offcanvas").trim();
        const collapsibleValue =
          stateRef.current === "collapsed" && collapsibleMode !== "none"
            ? collapsibleMode
            : "";

        node.dataset.state = stateRef.current;
        node.dataset.open = openRef.current ? "true" : "false";
        node.dataset.mobile = mobileRef.current ? "true" : "false";
        node.dataset.mobileOpen = mobileOpenRef.current ? "true" : "false";
        node.dataset.collapsible = collapsibleValue;
      });

      const shouldShowTooltip = !mobileRef.current && stateRef.current === "collapsed";
      root.querySelectorAll("[data-slot='sidebar-menu-button'][data-tooltip-content]").forEach((node) => {
        if (!(node instanceof HTMLElement)) return;

        const tooltip = node.getAttribute("data-tooltip-content") || "";
        if (shouldShowTooltip && tooltip) {
          node.setAttribute("title", tooltip);
        } else {
          node.removeAttribute("title");
        }
      });

      if (typeof document !== "undefined") {
        document.body.style.overflow = mobileRef.current && mobileOpenRef.current ? "hidden" : "";
      }
    };

    const updateDesktopOpen = (valueOrUpdater) => {
      const nextOpen =
        typeof valueOrUpdater === "function"
          ? valueOrUpdater(openRef.current)
          : valueOrUpdater;

      if (controlledRef.current) {
        if (typeof onOpenChangeRef.current === "function") {
          onOpenChangeRef.current(nextOpen);
        }
      } else {
        openRef.current = nextOpen;
        stateRef.current = nextOpen ? "expanded" : "collapsed";
        syncDom();
      }

      writeCookie(nextOpen);
    };

    const updateMobileOpen = (valueOrUpdater) => {
      const nextOpen =
        typeof valueOrUpdater === "function"
          ? valueOrUpdater(mobileOpenRef.current)
          : valueOrUpdater;

      mobileOpenRef.current = nextOpen;
      syncDom();
    };

    const toggleSidebar = () => {
      if (mobileRef.current) {
        updateMobileOpen((previous) => !previous);
        return;
      }

      updateDesktopOpen((previous) => !previous);
    };

    pp.layoutEffect(() => {
      controlledRef.current = isControlled;
      onOpenChangeRef.current = pp.props.onOpenChange;

      if (isControlled) {
        openRef.current = parseBool(controlledOpen, true);
        stateRef.current = openRef.current ? "expanded" : "collapsed";
      }

      syncDom();
    }, [controlledOpen, isControlled, pp.props.onOpenChange]);

    pp.effect(() => {
      if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
        return undefined;
      }

      const mediaQuery = window.matchMedia(SIDEBAR_MEDIA_QUERY);
      mediaQueryRef.current = mediaQuery;

      const onMediaChange = (event) => {
        mobileRef.current = event.matches;
        if (!event.matches) {
          mobileOpenRef.current = false;
        }
        syncDom();
      };

      mobileRef.current = mediaQuery.matches;
      syncDom();

      if (typeof mediaQuery.addEventListener === "function") {
        mediaQuery.addEventListener("change", onMediaChange);
        return () => mediaQuery.removeEventListener("change", onMediaChange);
      }

      mediaQuery.addListener(onMediaChange);
      return () => mediaQuery.removeListener(onMediaChange);
    }, []);

    pp.effect(() => {
      const root = rootRef.current;
      if (!(root instanceof HTMLElement)) return;

      const onClick = (event) => {
        const target = event.target instanceof Node ? event.target : null;
        const element = target instanceof Element
          ? target.closest("[data-sidebar='trigger'], [data-sidebar='rail'], [data-sidebar='mobile-overlay'], [data-sidebar='mobile-close']")
          : null;

        if (!(element instanceof HTMLElement) || !root.contains(element)) {
          return;
        }

        if (element.matches("[data-sidebar='mobile-overlay'], [data-sidebar='mobile-close']")) {
          event.preventDefault();
          updateMobileOpen(false);
          return;
        }

        if (element.matches("[data-sidebar='trigger'], [data-sidebar='rail']")) {
          event.preventDefault();
          toggleSidebar();
        }
      };

      const onToggle = (event) => {
        event.stopPropagation();
        toggleSidebar();
      };

      const onOpenChange = (event) => {
        if (!(event instanceof CustomEvent)) return;
        event.stopPropagation();

        const detail = event.detail || {};
        const nextOpen = parseBool(detail.open, true);

        if (detail.mobile) {
          updateMobileOpen(nextOpen);
        } else {
          updateDesktopOpen(nextOpen);
        }
      };

      const onKeyDown = (event) => {
        const key = typeof event.key === "string" ? event.key.toLowerCase() : "";

        if (key === SIDEBAR_KEYBOARD_SHORTCUT && (event.metaKey || event.ctrlKey)) {
          event.preventDefault();
          toggleSidebar();
          return;
        }

        if (event.key === "Escape" && mobileOpenRef.current) {
          event.preventDefault();
          updateMobileOpen(false);
        }
      };

      root.addEventListener("click", onClick);
      root.addEventListener("sidebar-toggle", onToggle);
      root.addEventListener("sidebar-open-change", onOpenChange);
      window.addEventListener("keydown", onKeyDown);

      return () => {
        root.removeEventListener("click", onClick);
        root.removeEventListener("sidebar-toggle", onToggle);
        root.removeEventListener("sidebar-open-change", onOpenChange);
        window.removeEventListener("keydown", onKeyDown);
        if (typeof document !== "undefined") {
          document.body.style.overflow = "";
        }
      };
    }, []);
  </script>
</div>
""",
        attributes=attributes,
        children=children,
    )


@component
def Sidebar(
    side: SidebarSide | str = "left",
    variant: SidebarVariant | str = "sidebar",
    collapsible: SidebarCollapsible | str = "offcanvas",
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    dir_value = props.pop("dir", None)

    normalized_side = _normalize_choice(side, {"left", "right"}, "left")
    normalized_variant = _normalize_choice(
        variant,
        {"sidebar", "floating", "inset"},
        "sidebar",
    )
    normalized_collapsible = _normalize_choice(
        collapsible,
        {"offcanvas", "icon", "none"},
        "offcanvas",
    )

    root_attributes = get_attributes(
        {
            "class": "group peer text-sidebar-foreground",
            "data-slot": "sidebar",
            "data-side": normalized_side,
            "data-variant": normalized_variant,
            "data-state": "expanded",
            "data-collapsible": "",
            "data-collapsible-mode": normalized_collapsible,
            "data-open": "true",
            "data-mobile": "false",
            "data-mobile-open": "false",
            "dir": dir_value,
        }
    )

    overlay_attributes = get_attributes(
        {
            "class": (
                "fixed inset-0 z-30 bg-black/50 opacity-0 pointer-events-none "
                "transition-opacity duration-200 md:hidden group-data-[mobile-open=true]:opacity-100 "
                "group-data-[mobile-open=true]:pointer-events-auto"
            ),
            "data-sidebar": "mobile-overlay",
            "aria-hidden": "true",
        }
    )

    gap_class = merge_classes(
        "relative hidden w-(--sidebar-width) bg-transparent transition-[width] duration-200 ease-linear md:block",
        "group-data-[collapsible=offcanvas]:w-0",
        "group-data-[side=right]:rotate-180",
        (
            "group-data-[collapsible=icon]:w-[calc(var(--sidebar-width-icon)+(--spacing(4)))]"
            if normalized_variant in {"floating", "inset"}
            else "group-data-[collapsible=icon]:w-(--sidebar-width-icon)"
        ),
    )
    gap_attributes = get_attributes(
        {
            "class": gap_class,
            "data-slot": "sidebar-gap",
        }
    )

    container_class = merge_classes(
        "fixed inset-y-0 z-40 flex h-svh w-[var(--sidebar-width-mobile)] transition-[transform,left,right,width] duration-200 ease-linear md:z-10 md:w-(--sidebar-width)",
        "data-[side=left]:left-0 data-[side=right]:right-0",
        "data-[side=left]:group-data-[mobile-open=false]:-translate-x-full data-[side=right]:group-data-[mobile-open=false]:translate-x-full md:translate-x-0",
        "md:data-[side=left]:group-data-[mobile-open=false]:translate-x-0 md:data-[side=right]:group-data-[mobile-open=false]:translate-x-0",
        "md:data-[side=left]:group-data-[collapsible=offcanvas]:left-[calc(var(--sidebar-width)*-1)] md:data-[side=right]:group-data-[collapsible=offcanvas]:right-[calc(var(--sidebar-width)*-1)]",
        (
            "p-2 md:group-data-[collapsible=icon]:w-[calc(var(--sidebar-width-icon)+(--spacing(4))+2px)]"
            if normalized_variant in {"floating", "inset"}
            else "md:group-data-[collapsible=icon]:w-(--sidebar-width-icon) md:group-data-[collapsible=icon]:border-transparent md:group-data-[side=left]:border-r md:group-data-[side=right]:border-l"
        ),
        incoming_class,
    )
    container_attributes = get_attributes(
        {
            "class": container_class,
            "data-slot": "sidebar-container",
            "data-side": normalized_side,
            "aria-hidden": "false",
        },
        props,
    )

    inner_attributes = get_attributes(
        {
            "class": merge_classes(
                "flex h-full w-full flex-col bg-sidebar text-sidebar-foreground",
                "group-data-[variant=floating]:rounded-lg group-data-[variant=floating]:border group-data-[variant=floating]:border-sidebar-border group-data-[variant=floating]:shadow-sm",
                "group-data-[variant=inset]:rounded-lg group-data-[variant=inset]:border group-data-[variant=inset]:border-sidebar-border group-data-[variant=inset]:shadow-sm",
            ),
            "data-sidebar": "sidebar",
            "data-slot": "sidebar-inner",
        }
    )

    return html(r"""
<div {{ root_attributes }}><div {{ overlay_attributes }}></div>
  <div {{ gap_attributes }}></div>
  <div {{ container_attributes }}><div {{ inner_attributes }}>{{ children }}</div>
  </div>
</div>
""",
        root_attributes=root_attributes,
        overlay_attributes=overlay_attributes,
        gap_attributes=gap_attributes,
        container_attributes=container_attributes,
        inner_attributes=inner_attributes,
        children=children,
    )


@component
def SidebarTrigger(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    icon = PanelLeft(**{"class": "rtl:rotate-180"})

    content = children or f'{icon}<span class="sr-only">Toggle Sidebar</span>'
    return Button(
        variant="ghost",
        size="icon",
        **{
            "class": merge_classes("size-7", incoming_class),
            "children": content,
            "data-slot": "sidebar-trigger",
            "data-sidebar": "trigger",
            **props,
        },
    )


@component
def SidebarRail(**props):
    incoming_class = props.pop("class", "")

    attributes = get_attributes(
        {
            "type": "button",
            "aria-label": "Toggle Sidebar",
            "tabindex": "-1",
            "title": "Toggle Sidebar",
            "data-slot": "sidebar-rail",
            "data-sidebar": "rail",
            "class": merge_classes(
                "absolute inset-y-0 z-20 hidden w-4 -translate-x-1/2 transition-all ease-linear group-data-[side=left]:-right-4 group-data-[side=right]:left-0 after:absolute after:inset-y-0 after:left-1/2 after:w-[2px] hover:after:bg-sidebar-border sm:flex",
                "in-data-[side=left]:cursor-w-resize in-data-[side=right]:cursor-e-resize",
                "[[data-side=left][data-state=collapsed]_&]:cursor-e-resize [[data-side=right][data-state=collapsed]_&]:cursor-w-resize",
                "group-data-[collapsible=offcanvas]:translate-x-0 group-data-[collapsible=offcanvas]:after:left-full hover:group-data-[collapsible=offcanvas]:bg-sidebar",
                "[[data-side=left][data-collapsible=offcanvas]_&]:-right-2 [[data-side=right][data-collapsible=offcanvas]_&]:-left-2",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""<button {{ attributes }}></button>""", attributes=attributes)


@component
def SidebarInset(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-inset",
            "class": merge_classes(
                "relative flex w-full flex-1 flex-col bg-background",
                "md:peer-data-[variant=inset]:m-2 md:peer-data-[variant=inset]:ml-0 md:peer-data-[variant=inset]:rounded-xl",
                "md:peer-data-[variant=inset]:shadow-sm md:peer-data-[variant=inset]:peer-data-[state=collapsed]:ml-2",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""
<main {{ attributes }}>{{ children }}
</main>
""",
        attributes=attributes,
        children=children,
    )


@component
def SidebarInput(**props):
    incoming_class = props.pop("class", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-input",
            "data-sidebar": "input",
            "class": merge_classes(
                "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex h-8 w-full min-w-0 rounded-md border px-3 py-1 text-base shadow-none transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive bg-background",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""<input {{ attributes }} />""", attributes=attributes)


@component
def SidebarHeader(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-header",
            "data-sidebar": "header",
            "class": merge_classes("flex flex-col gap-2 p-2", incoming_class),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarFooter(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-footer",
            "data-sidebar": "footer",
            "class": merge_classes("flex flex-col gap-2 p-2", incoming_class),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarSeparator(**props):
    incoming_class = props.pop("class", "")
    return Separator(
        **{
            "class": merge_classes("w-full bg-sidebar-border", incoming_class),
            "data-slot": "sidebar-separator",
            "data-sidebar": "separator",
            **props,
        }
    )


@component
def SidebarContent(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-content",
            "data-sidebar": "content",
            "class": merge_classes(
                "flex min-h-0 flex-1 flex-col gap-2 overflow-auto group-data-[collapsible=icon]:overflow-hidden",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarGroup(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-group",
            "data-sidebar": "group",
            "class": merge_classes("relative flex w-full min-w-0 flex-col p-2", incoming_class),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarGroupLabel(
    asChild: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))

    attributes = {
        "data-slot": "sidebar-group-label",
        "data-sidebar": "group-label",
        "class": merge_classes(
            "flex h-8 shrink-0 items-center rounded-md px-2 text-xs font-medium text-sidebar-foreground/70 ring-sidebar-ring outline-hidden transition-[margin,opacity] duration-200 ease-linear focus-visible:ring-2 [&>svg]:size-4 [&>svg]:shrink-0",
            "group-data-[collapsible=icon]:-mt-8 group-data-[collapsible=icon]:opacity-0",
            incoming_class,
        ),
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes(attributes, props)
    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)


@component
def SidebarGroupAction(
    asChild: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))

    attributes = {
        "data-slot": "sidebar-group-action",
        "data-sidebar": "group-action",
        "class": merge_classes(
            "absolute top-3.5 right-3 flex aspect-square w-5 items-center justify-center rounded-md p-0 text-sidebar-foreground ring-sidebar-ring outline-hidden transition-transform hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 [&>svg]:size-4 [&>svg]:shrink-0",
            "after:absolute after:-inset-2 md:after:hidden",
            "group-data-[collapsible=icon]:hidden",
            incoming_class,
        ),
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes({"type": "button", **attributes}, props)
    return html(r"""<button {{ attrs }}>{{ children }}</button>""", attrs=attrs, children=children)


@component
def SidebarGroupContent(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-group-content",
            "data-sidebar": "group-content",
            "class": merge_classes("w-full text-sm", incoming_class),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarMenu(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu",
            "data-sidebar": "menu",
            "class": merge_classes("flex w-full min-w-0 flex-col gap-1", incoming_class),
        },
        props,
    )

    return html(r"""
<ul {{ attributes }}>{{ children }}
</ul>
""",
        attributes=attributes,
        children=children,
    )


@component
def SidebarMenuItem(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu-item",
            "data-sidebar": "menu-item",
            "class": merge_classes("group/menu-item relative", incoming_class),
        },
        props,
    )

    return html(r"""<li {{ attributes }}>{{ children }}</li>""", attributes=attributes, children=children
    )


@component
def SidebarMenuButton(
    asChild: bool | str | None = False,
    isActive: bool | str | None = False,
    variant: SidebarMenuButtonVariant | str = "default",
    size: SidebarMenuButtonSize | str = "default",
    tooltip: Optional[str] = None,
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
    is_active = parse_bool(pop_prop_alias(props, "isActive", isActive))
    tooltip_value = props.pop("tooltip", tooltip)
    normalized_variant = _normalize_choice(variant, {"default", "outline"}, "default")
    normalized_size = _normalize_choice(size, {"default", "sm", "lg"}, "default")

    attributes = {
        "data-slot": "sidebar-menu-button",
        "data-sidebar": "menu-button",
        "data-size": normalized_size,
        "data-active": str(is_active).lower(),
        "data-tooltip-content": tooltip_value,
        "class": sidebar_menu_button_style(normalized_variant, normalized_size, incoming_class),
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes({"type": "button", **attributes}, props)
    return html(r"""<button {{ attrs }}>{{ children }}</button>""", attrs=attrs, children=children)


@component
def SidebarMenuAction(
    asChild: bool | str | None = False,
    showOnHover: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
    show_on_hover = parse_bool(pop_prop_alias(props, "showOnHover", showOnHover))

    action_class = merge_classes(
        "absolute top-1.5 right-1 flex aspect-square w-5 items-center justify-center rounded-md p-0 text-sidebar-foreground ring-sidebar-ring outline-hidden transition-transform peer-hover/menu-button:text-sidebar-accent-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 [&>svg]:size-4 [&>svg]:shrink-0",
        "after:absolute after:-inset-2 md:after:hidden",
        "peer-data-[size=sm]/menu-button:top-1 peer-data-[size=default]/menu-button:top-1.5 peer-data-[size=lg]/menu-button:top-2.5",
        "group-data-[collapsible=icon]:hidden",
        (
            "group-focus-within/menu-item:opacity-100 group-hover/menu-item:opacity-100 peer-data-[active=true]/menu-button:text-sidebar-accent-foreground data-[state=open]:opacity-100 md:opacity-0"
            if show_on_hover
            else ""
        ),
        incoming_class,
    )

    attributes = {
        "data-slot": "sidebar-menu-action",
        "data-sidebar": "menu-action",
        "class": action_class,
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes({"type": "button", **attributes}, props)
    return html(r"""<button {{ attrs }}>{{ children }}</button>""", attrs=attrs, children=children)


@component
def SidebarMenuBadge(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu-badge",
            "data-sidebar": "menu-badge",
            "class": merge_classes(
                "pointer-events-none absolute right-1 flex h-5 min-w-5 items-center justify-center rounded-md px-1 text-xs font-medium text-sidebar-foreground tabular-nums select-none",
                "peer-hover/menu-button:text-sidebar-accent-foreground peer-data-[active=true]/menu-button:text-sidebar-accent-foreground",
                "peer-data-[size=sm]/menu-button:top-1 peer-data-[size=default]/menu-button:top-1.5 peer-data-[size=lg]/menu-button:top-2.5",
                "group-data-[collapsible=icon]:hidden",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ children }}</div>""", attributes=attributes, children=children
    )


@component
def SidebarMenuSkeleton(
    showIcon: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    show_icon = parse_bool(props.pop("showIcon", showIcon))
    width = f"{random.randint(50, 90)}%"

    icon = ""
    if show_icon:
        icon = Skeleton(
            **{
                "class": "size-4 rounded-md",
                "data-slot": "sidebar-menu-skeleton-icon",
                "data-sidebar": "menu-skeleton-icon",
            }
        )

    text = Skeleton(
        **{
            "class": "h-4 max-w-(--skeleton-width) flex-1",
            "style": f"--skeleton-width: {width}",
            "data-slot": "sidebar-menu-skeleton-text",
            "data-sidebar": "menu-skeleton-text",
        }
    )

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu-skeleton",
            "data-sidebar": "menu-skeleton",
            "class": merge_classes("flex h-8 items-center gap-2 rounded-md px-2", incoming_class),
        },
        props,
    )

    return html(r"""<div {{ attributes }}>{{ icon }}{{ text }}</div>""",
        attributes=attributes,
        icon=icon,
        text=text,
    )


@component
def SidebarMenuSub(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu-sub",
            "data-sidebar": "menu-sub",
            "class": merge_classes(
                "mx-3.5 flex min-w-0 translate-x-px flex-col gap-1 border-l border-sidebar-border px-2.5 py-0.5",
                "group-data-[collapsible=icon]:hidden",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""
<ul {{ attributes }}>{{ children }}
</ul>
""",
        attributes=attributes,
        children=children,
    )


@component
def SidebarMenuSubItem(**props):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")

    attributes = get_attributes(
        {
            "data-slot": "sidebar-menu-sub-item",
            "data-sidebar": "menu-sub-item",
            "class": merge_classes("group/menu-sub-item relative", incoming_class),
        },
        props,
    )

    return html(r"""<li {{ attributes }}>{{ children }}</li>""", attributes=attributes, children=children
    )


@component
def SidebarMenuSubButton(
    asChild: bool | str | None = False,
    size: SidebarMenuSubButtonSize | str = "md",
    isActive: bool | str | None = False,
    **props,
):
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
    normalized_size = _normalize_choice(size, {"sm", "md"}, "md")
    is_active = parse_bool(pop_prop_alias(props, "isActive", isActive))

    button_class = merge_classes(
        "flex h-7 min-w-0 -translate-x-px items-center gap-2 overflow-hidden rounded-md px-2 text-sidebar-foreground ring-sidebar-ring outline-hidden hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 active:bg-sidebar-accent active:text-sidebar-accent-foreground disabled:pointer-events-none disabled:opacity-50 aria-disabled:pointer-events-none aria-disabled:opacity-50 [&>span:last-child]:truncate [&>svg]:size-4 [&>svg]:shrink-0 [&>svg]:text-sidebar-accent-foreground",
        "data-[active=true]:bg-sidebar-accent data-[active=true]:text-sidebar-accent-foreground",
        "text-xs" if normalized_size == "sm" else "text-sm",
        "group-data-[collapsible=icon]:hidden",
        incoming_class,
    )

    attributes = {
        "data-slot": "sidebar-menu-sub-button",
        "data-sidebar": "menu-sub-button",
        "data-size": normalized_size,
        "data-active": str(is_active).lower(),
        "class": button_class,
    }

    if as_child:
        return Slot(
            children=children,
            asChild=True,
            **{**attributes, **props},
        )

    attrs = get_attributes(attributes, props)
    return html(r"""<a {{ attrs }}>{{ children }}</a>""", attrs=attrs, children=children)
