from typing import Literal, Optional

from casp.component_decorator import component, html
from casp.html_attrs import get_attributes, merge_classes
from markupsafe import Markup

from .Portal import Portal
from .Slot import Slot
from .utils import generate_id, parse_bool, pop_prop_alias
from src.lib.ppicons.Check import Check
from src.lib.ppicons.ChevronRight import ChevronRight

DropdownMenuSide = Literal["top", "right", "bottom", "left"]
DropdownMenuAlign = Literal["start", "center", "end"]

_DROPDOWN_MENU_ID_PLACEHOLDER = "__maddex_dropdown_menu_id__"
_DROPDOWN_MENU_TRIGGER_ID_PLACEHOLDER = "__maddex_dropdown_menu_trigger_id__"


def _normalize_choice(value: str | None, allowed: set[str], fallback: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else fallback


def _dropdown_menu_content_script() -> str:
    return """
const parseBool = (value) => {
  if (value === true) return true;
  if (typeof value !== "string") return false;

  const normalized = value.trim().toLowerCase();
  return normalized === "" || ["true", "1", "yes", "on"].includes(normalized);
};

const schedule = (callback) => {
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(() => callback());
    return;
  }

  setTimeout(callback, 0);
};

const parseNumber = (value, fallback) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const getViewportBox = () => {
  const visualViewport = window.visualViewport;

  return {
    width: visualViewport
      ? visualViewport.width
      : document.documentElement.clientWidth,
    height: visualViewport
      ? visualViewport.height
      : document.documentElement.clientHeight,
    x: visualViewport ? visualViewport.offsetLeft : 0,
    y: visualViewport ? visualViewport.offsetTop : 0,
  };
};

const hasFineHoverPointer = () => {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return false;
  }

  return window.matchMedia("(hover: hover) and (pointer: fine)").matches;
};

const shouldUseHoverInteraction = (event = null) => {
  if (event && "pointerType" in event) {
    return event.pointerType === "mouse";
  }

  return hasFineHoverPointer();
};

const shouldUseTapInteraction = (pointerType = "") => {
  if (pointerType === "touch" || pointerType === "pen") {
    return true;
  }

  return !hasFineHoverPointer();
};

const isAnchorPresentInViewport = (anchorEl) => {
  if (!(anchorEl instanceof HTMLElement)) return false;
  if (!document.documentElement.contains(anchorEl)) return false;

  const rect = anchorEl.getBoundingClientRect();
  const viewport = getViewportBox();

  return (
    rect.width > 0 &&
    rect.height > 0 &&
    rect.bottom > viewport.y &&
    rect.top < viewport.y + viewport.height &&
    rect.right > viewport.x &&
    rect.left < viewport.x + viewport.width
  );
};

const resolveTransformOrigin = (side, align) => {
  let x = "center";
  let y = "center";

  if (side === "top") y = "bottom";
  if (side === "bottom") y = "top";
  if (side === "left") x = "right";
  if (side === "right") x = "left";

  if (side === "top" || side === "bottom") {
    if (align === "start") x = "left";
    if (align === "end") x = "right";
  } else {
    if (align === "start") y = "top";
    if (align === "end") y = "bottom";
  }

  return `${y} ${x}`;
};

const finishAfterAnimation = (element, callback, fallbackMs = 200) => {
  if (!(element instanceof HTMLElement)) {
    callback();
    return () => {};
  }

  let finished = false;
  let timeoutId = null;

  const finish = () => {
    if (finished) return;
    finished = true;
    if (timeoutId !== null) {
      clearTimeout(timeoutId);
      timeoutId = null;
    }
    element.removeEventListener("animationend", onAnimationEnd);
    callback();
  };

  const onAnimationEnd = (event) => {
    if (event.target !== element) return;
    finish();
  };

  element.addEventListener("animationend", onAnimationEnd);
  timeoutId = setTimeout(finish, fallbackMs);

  return finish;
};

const getMenuItems = (container) => {
  if (!(container instanceof HTMLElement)) return [];

  return Array.from(
    container.querySelectorAll(
      '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
    ),
  ).filter((item) => {
    if (!(item instanceof HTMLElement)) return false;
    if (item.getAttribute("data-disabled") === "true") return false;
    return item.offsetParent !== null && item.closest('[role="menu"]') === container;
  });
};

const clearMenuHighlights = (menuEl) => {
  if (!(menuEl instanceof HTMLElement)) return;

  getMenuItems(menuEl).forEach((item) => {
    if (item instanceof HTMLElement) {
      item.setAttribute("data-highlighted", "false");
    }
  });
};

const syncCheckboxItem = (item) => {
  if (!(item instanceof HTMLElement)) return;

  const isChecked = item.getAttribute("aria-checked") === "true";
  item.setAttribute("data-checked", isChecked ? "true" : "false");

  const indicator = item.querySelector("[data-checkbox-indicator]");
  if (indicator instanceof HTMLElement) {
    indicator.classList.toggle("hidden", !isChecked);
  }
};

const syncRadioGroup = (group) => {
  if (!(group instanceof HTMLElement)) return;

  const items = Array.from(
    group.querySelectorAll('[data-slot="dropdown-menu-radio-item"]'),
  ).filter((item) => item instanceof HTMLElement);

  let selectedValue = group.getAttribute("data-value") || "";

  if (!selectedValue) {
    const initiallyChecked = items.find(
      (item) => item.getAttribute("aria-checked") === "true",
    );
    selectedValue = initiallyChecked?.getAttribute("data-value") || "";
    group.setAttribute("data-value", selectedValue);
  }

  items.forEach((item) => {
    const isChecked =
      selectedValue !== "" && item.getAttribute("data-value") === selectedValue;

    item.setAttribute("aria-checked", isChecked ? "true" : "false");
    item.setAttribute("data-checked", isChecked ? "true" : "false");

    const indicator = item.querySelector("[data-radio-indicator]");
    if (indicator instanceof HTMLElement) {
      indicator.classList.toggle("hidden", !isChecked);
    }
  });
};

const syncItemState = (dropdown) => {
  dropdown
    .querySelectorAll('[data-slot="dropdown-menu-checkbox-item"]')
    .forEach(syncCheckboxItem);

  dropdown
    .querySelectorAll('[data-slot="dropdown-menu-radio-group"]')
    .forEach(syncRadioGroup);
};

const updateFloatingPosition = (
  anchorEl,
  menuEl,
  preferredSide,
  preferredAlign,
  sideOffset,
  options = {},
) => {
  if (!(anchorEl instanceof HTMLElement) || !(menuEl instanceof HTMLElement)) return;

  const viewportPadding = 8;
  const anchorRect = anchorEl.getBoundingClientRect();
  const viewport = getViewportBox();

  const constrainToViewport = options.constrainToViewport !== false;
  const allowSideFlip = options.allowSideFlip !== false;
  const preserveCurrentSide = options.preserveCurrentSide === true;

  menuEl.style.maxWidth = "";
  menuEl.style.maxHeight = "";
  menuEl.style.overflowX = "";
  menuEl.style.overflowY = "";
  menuEl.style.overscrollBehavior = "";

  const menuRect = menuEl.getBoundingClientRect();
  const naturalWidth = menuEl.scrollWidth || menuEl.offsetWidth || menuRect.width;
  const naturalHeight = menuEl.scrollHeight || menuEl.offsetHeight || menuRect.height;
  const viewportMaxWidth = Math.max(160, viewport.width - viewportPadding * 2);

  const availableTop = Math.max(
    0,
    anchorRect.top - viewport.y - viewportPadding - sideOffset,
  );
  const availableBottom = Math.max(
    0,
    viewport.y + viewport.height - anchorRect.bottom - viewportPadding - sideOffset,
  );
  const availableLeft = Math.max(
    0,
    anchorRect.left - viewport.x - viewportPadding - sideOffset,
  );
  const availableRight = Math.max(
    0,
    viewport.x + viewport.width - anchorRect.right - viewportPadding - sideOffset,
  );

  const oppositeSide = {
    top: "bottom",
    right: "left",
    bottom: "top",
    left: "right",
  };

  const availableForSide = (side) => {
    if (side === "top") return availableTop;
    if (side === "bottom") return availableBottom;
    if (side === "left") return availableLeft;
    return availableRight;
  };

  let actualSide = preserveCurrentSide
    ? menuEl.getAttribute("data-resolved-side") ||
      menuEl.getAttribute("data-side") ||
      preferredSide
    : preferredSide;

  const naturalMainAxis =
    preferredSide === "left" || preferredSide === "right" ? naturalWidth : naturalHeight;
  const preferredAvailable = availableForSide(preferredSide);
  const oppositeAvailable = availableForSide(oppositeSide[preferredSide] || preferredSide);

  if (
    allowSideFlip &&
    naturalMainAxis > preferredAvailable &&
    oppositeAvailable > preferredAvailable
  ) {
    actualSide = oppositeSide[preferredSide] || preferredSide;
  }

  let renderedWidth = naturalWidth;
  let renderedHeight = naturalHeight;

  const applySizeForSide = (side) => {
    menuEl.style.maxWidth = "";
    menuEl.style.maxHeight = "";
    menuEl.style.overflowX = "";
    menuEl.style.overflowY = "";
    menuEl.style.overscrollBehavior = "";
    renderedWidth = naturalWidth;
    renderedHeight = naturalHeight;

    if (!constrainToViewport) {
      return;
    }

    const availableWidthForSide =
      side === "left" || side === "right"
        ? Math.max(160, Math.min(viewportMaxWidth, availableForSide(side)))
        : viewportMaxWidth;

    if (naturalWidth > availableWidthForSide) {
      menuEl.style.maxWidth = `${Math.round(availableWidthForSide)}px`;
      menuEl.style.overflowX = "auto";
      menuEl.style.overscrollBehavior = "contain";
      renderedWidth = availableWidthForSide;
    }

    if (side === "top" || side === "bottom") {
      const availableHeight = Math.max(
        120,
        Math.min(viewport.height - viewportPadding * 2, availableForSide(side)),
      );
      if (naturalHeight > availableHeight) {
        menuEl.style.maxHeight = `${Math.round(availableHeight)}px`;
        menuEl.style.overflowY = "auto";
        menuEl.style.overscrollBehavior = "contain";
        renderedHeight = availableHeight;
      }
      return;
    }

    const availableHeight = Math.max(120, viewport.height - viewportPadding * 2);
    if (naturalHeight > availableHeight) {
      menuEl.style.maxHeight = `${Math.round(availableHeight)}px`;
      menuEl.style.overflowY = "auto";
      menuEl.style.overscrollBehavior = "contain";
      renderedHeight = availableHeight;
    }
  };

  applySizeForSide(actualSide);

  const alignLeft = () => {
    if (preferredAlign === "start") return anchorRect.left;
    if (preferredAlign === "end") return anchorRect.right - renderedWidth;
    return anchorRect.left + (anchorRect.width - renderedWidth) / 2;
  };

  const alignTop = () => {
    if (preferredAlign === "start") return anchorRect.top;
    if (preferredAlign === "end") return anchorRect.bottom - renderedHeight;
    return anchorRect.top + (anchorRect.height - renderedHeight) / 2;
  };

  const placeForSide = (side) => {
    if (side === "top") {
      return {
        top: anchorRect.top - renderedHeight - sideOffset,
        left: alignLeft(),
      };
    }

    if (side === "right") {
      return {
        top: alignTop(),
        left: anchorRect.right + sideOffset,
      };
    }

    if (side === "left") {
      return {
        top: alignTop(),
        left: anchorRect.left - renderedWidth - sideOffset,
      };
    }

    return {
      top: anchorRect.bottom + sideOffset,
      left: alignLeft(),
    };
  };

  const shouldFlip = (side, coords) => {
    if (!allowSideFlip || !constrainToViewport) return false;
    if (side === "top") return coords.top < viewport.y + viewportPadding;
    if (side === "right") {
      return coords.left + renderedWidth > viewport.x + viewport.width - viewportPadding;
    }
    if (side === "left") return coords.left < viewport.x + viewportPadding;
    return coords.top + renderedHeight > viewport.y + viewport.height - viewportPadding;
  };

  let coords = placeForSide(actualSide);

  if (shouldFlip(actualSide, coords)) {
    actualSide = oppositeSide[actualSide] || preferredSide;
    applySizeForSide(actualSide);
    coords = placeForSide(actualSide);
  }

  if (constrainToViewport) {
    const minLeft = viewport.x + viewportPadding;
    const maxLeft = viewport.x + viewport.width - renderedWidth - viewportPadding;
    const minTop = viewport.y + viewportPadding;
    const maxTop = viewport.y + viewport.height - renderedHeight - viewportPadding;

    coords.left = clamp(coords.left, minLeft, Math.max(minLeft, maxLeft));
    coords.top = clamp(coords.top, minTop, Math.max(minTop, maxTop));
  }

  menuEl.setAttribute("data-side", actualSide);
  menuEl.setAttribute("data-resolved-side", actualSide);
  menuEl.setAttribute("data-resolved-align", preferredAlign);
  menuEl.style.position = "fixed";
  menuEl.style.left = `${Math.round(coords.left)}px`;
  menuEl.style.top = `${Math.round(coords.top)}px`;
  menuEl.style.transformOrigin = resolveTransformOrigin(actualSide, preferredAlign);
};

pp.effect(() => {
  const portalEl = portalRef.current;
  const contentEl = contentBoxRef.current;
  const dropdownOwnerId =
    contentEl?.getAttribute("data-dropdown-owner")
    || portalEl?.getAttribute("data-dropdown-owner")
    || "";
  const dropdown =
    (dropdownOwnerId
      ? document.querySelector(`[data-dropdown-menu-event-id="${dropdownOwnerId}"]`)
      : null)
    || portal.sourceParent?.closest('[data-slot="dropdown-menu"]');

  if (
    !(portalEl instanceof HTMLElement) ||
    !(contentEl instanceof HTMLElement) ||
    !(dropdown instanceof HTMLElement)
  ) {
    return;
  }

  const ownerBoundary =
    dropdown.parentElement?.closest("[pp-component]")
    || dropdown.closest("[pp-component]");
  const ownerComponentId = ownerBoundary?.getAttribute("pp-component") || "";
  if (!ownerComponentId) return;

  const normalizedId = ownerComponentId.replace(/[^a-zA-Z0-9_-]+/g, "_");
  const runtimeIds = {
    eventId: `dropdown-event-${normalizedId}`,
    contentId: `dropdown-content-${normalizedId}`,
    triggerId: `dropdown-trigger-${normalizedId}`,
  };
  dropdown.setAttribute("data-dropdown-menu-event-id", runtimeIds.eventId);
  dropdown.setAttribute("data-dropdown-menu-content-id", runtimeIds.contentId);
  dropdown.setAttribute("data-dropdown-menu-trigger-id", runtimeIds.triggerId);
  contentEl.setAttribute("id", runtimeIds.contentId);
  contentEl.setAttribute("aria-labelledby", runtimeIds.triggerId);
  contentEl.setAttribute("data-dropdown-owner", runtimeIds.eventId);
  portalEl.setAttribute("data-dropdown-owner", runtimeIds.eventId);

  const triggerEl = dropdown.querySelector('[data-slot="dropdown-menu-trigger"]');
  if (!(triggerEl instanceof HTMLElement)) return;

  const dropdownMenuId = runtimeIds.eventId;
  if (!dropdownMenuId) return;

  const preferredSide = (contentEl.getAttribute("data-side") || "bottom").toLowerCase();
  const preferredAlign = (contentEl.getAttribute("data-align") || "center").toLowerCase();
  const sideOffset = parseNumber(contentEl.getAttribute("data-side-offset"), 4);
  const closeOnOutsideClick = parseBool(
    dropdown.getAttribute("data-close-on-outside-click"),
  );
  const closeOnSelect = parseBool(dropdown.getAttribute("data-close-on-select"));

  let frameId = null;
  let closeTimerId = null;
  let rootClosing = false;
  let focusTriggerAfterClose = false;
  let lastInteractionWasKeyboard = false;
  const submenuRecords = [];
  const teardownCallbacks = [];

  const clearAllMenuHighlights = () => {
    clearMenuHighlights(contentEl);
    submenuRecords.forEach((record) => clearMenuHighlights(record.content));
  };

  const scrollLockState = {
    locked: false,
    bodyOverflow: document.body.style.overflow,
    bodyPaddingRight: document.body.style.paddingRight,
    htmlOverflow: document.documentElement.style.overflow,
  };

  const getScrollbarWidth = () =>
    Math.max(0, window.innerWidth - document.documentElement.clientWidth);

  const isInsideDropdownTree = (target) => {
    if (!(target instanceof Node)) return false;

    if (contentEl.contains(target) || dropdown.contains(target)) {
      return true;
    }

    return submenuRecords.some(
      (record) => record.content.contains(target) || record.trigger.contains(target),
    );
  };

  const isMobileViewport = () =>
    typeof window !== "undefined"
    && typeof window.matchMedia === "function"
    && window.matchMedia("(max-width: 767px)").matches;

  const lockPageScroll = () => {
    if (scrollLockState.locked) return;

    scrollLockState.locked = true;

    // On mobile, setting overflow:hidden on <html>/<body> breaks a sticky page
    // header (it drops out of the viewport while a fixed dropdown overlay is
    // open and the page repaints). The wheel/touchmove prevention in
    // preventOutsideScroll already locks scrolling on touch devices, so skip the
    // overflow lock there and only apply it on desktop where it's safe.
    if (isMobileViewport()) return;

    const scrollbarWidth = getScrollbarWidth();

    document.documentElement.style.overflow = "hidden";
    document.body.style.overflow = "hidden";

    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }
  };

  const unlockPageScroll = () => {
    if (!scrollLockState.locked) return;

    scrollLockState.locked = false;

    document.documentElement.style.overflow = scrollLockState.htmlOverflow;
    document.body.style.overflow = scrollLockState.bodyOverflow;
    document.body.style.paddingRight = scrollLockState.bodyPaddingRight;
  };

  const preventOutsideScroll = (event) => {
    if (dropdown.getAttribute("data-state") !== "open") return;
    if (isInsideDropdownTree(event.target)) return;

    event.preventDefault();
  };

  const scrollLockOptions = {
    passive: false,
    capture: true,
  };

  const getSubmenuParentRecord = (menuEl) =>
    submenuRecords.find((record) => record.content === menuEl) || null;

  const cancelFrame = () => {
    if (frameId !== null) {
      cancelAnimationFrame(frameId);
      frameId = null;
    }
  };

  const cancelCloseTimer = () => {
    if (closeTimerId !== null) {
      clearTimeout(closeTimerId);
      closeTimerId = null;
    }
  };

  const updateRootPosition = () => {
    const triggerIsPresent = isAnchorPresentInViewport(triggerEl);

    // Reactive page updates can replace the trigger while the portaled menu is
    // animating closed (for example, when a menu item opens a dialog). A
    // detached trigger reports a 0,0 rectangle; positioning from it makes the
    // closing menu flash in the top-left corner of the viewport. Keep the last
    // valid/frozen geometry until the portal finishes closing instead.
    if (rootClosing || !triggerIsPresent) return;

    updateFloatingPosition(
      triggerEl,
      contentEl,
      preferredSide,
      preferredAlign,
      sideOffset,
      {
        constrainToViewport: true,
        allowSideFlip: true,
        preserveCurrentSide: false,
      },
    );
  };

  const updateSubmenuPosition = (record) => {
    if (!record) return;

    const triggerIsPresent = isAnchorPresentInViewport(record.trigger);

    updateFloatingPosition(
      record.trigger,
      record.content,
      record.preferredSide,
      record.preferredAlign,
      0,
      {
        constrainToViewport: triggerIsPresent,
        allowSideFlip: triggerIsPresent,
        preserveCurrentSide: !triggerIsPresent,
      },
    );
  };

  const clearFrozenGeometry = (element) => {
    if (!(element instanceof HTMLElement)) return;
    element.style.position = "";
    element.style.left = "";
    element.style.top = "";
    element.style.width = "";
    element.style.height = "";
  };

  const freezeCurrentGeometry = (element) => {
    if (!(element instanceof HTMLElement)) return;
    const rect = element.getBoundingClientRect();
    element.style.position = "fixed";
    element.style.left = `${Math.round(rect.left)}px`;
    element.style.top = `${Math.round(rect.top)}px`;
    if (rect.width > 0) {
      element.style.width = `${Math.round(rect.width)}px`;
    }
    if (rect.height > 0) {
      element.style.height = `${Math.round(rect.height)}px`;
    }
  };

  const closeSubmenuRecord = (record, immediate = false) => {
    if (!record) return;
    if (record.hoverCloseTimer !== null) {
      clearTimeout(record.hoverCloseTimer);
      record.hoverCloseTimer = null;
    }

    if (record.closeTimer !== null) {
      clearTimeout(record.closeTimer);
      record.closeTimer = null;
    }

    const alreadyClosing =
      !record.isOpen && record.content.getAttribute("data-state") === "closed";

    if (alreadyClosing && !immediate) {
      return;
    }

    if (record.hideCleanup) {
      record.hideCleanup();
      record.hideCleanup = null;
    }

    clearMenuHighlights(record.content);

    record.isOpen = false;
    record.lockedOpen = false;
    record.trigger.setAttribute("data-state", "closed");
    record.trigger.setAttribute("aria-expanded", "false");
    record.content.setAttribute("data-state", "closed");
    record.content.setAttribute("aria-hidden", "true");
    record.content.style.pointerEvents = "none";

    const finish = () => {
      if (!record.isOpen) {
        record.content.hidden = true;
      }
    };

    if (immediate) {
      finish();
      return;
    }

    record.hideCleanup = finishAfterAnimation(record.content, () => {
      finish();
      record.hideCleanup = null;
    });
  };

  const collectDescendants = (record) =>
    submenuRecords.filter((candidate) => {
      let current = candidate.parentRecord;
      while (current) {
        if (current === record) return true;
        current = current.parentRecord;
      }
      return false;
    });

  const getRecordDepth = (record) => {
    let depth = 0;
    let current = record?.parentRecord || null;
    while (current) {
      depth += 1;
      current = current.parentRecord;
    }
    return depth;
  };

  const closeSubtree = (record, immediate = false) => {
    if (!record) return;

    const branch = [record, ...collectDescendants(record)].sort(
      (left, right) => getRecordDepth(right) - getRecordDepth(left),
    );

    branch.forEach((entry) => closeSubmenuRecord(entry, immediate));
  };

  const closeSiblingSubmenus = (record) => {
    submenuRecords.forEach((candidate) => {
      if (candidate === record) return;
      if (candidate.parentMenu !== record.parentMenu) return;
      closeSubtree(candidate, false);
    });
  };

  const branchContainsNode = (record, node) => {
    if (!(node instanceof Node) || !record) return false;
    if (record.trigger.contains(node) || record.content.contains(node)) return true;
    return collectDescendants(record).some(
      (descendant) =>
        descendant.trigger.contains(node) || descendant.content.contains(node),
    );
  };

  const openSubmenuRecord = (record, options = {}) => {
    if (!record) return;
    if (rootClosing) return;
    if ((dropdown.getAttribute("data-state") || "closed") !== "open") return;
    const { lockOpen = false } = options;
    if (record.hoverCloseTimer !== null) {
      clearTimeout(record.hoverCloseTimer);
      record.hoverCloseTimer = null;
    }
    if (record.closeTimer !== null) {
      clearTimeout(record.closeTimer);
      record.closeTimer = null;
    }
    if (record.hideCleanup) {
      record.hideCleanup();
      record.hideCleanup = null;
    }

    closeSiblingSubmenus(record);
    clearMenuHighlights(record.parentMenu);
    clearMenuHighlights(record.content);

    record.isOpen = true;
    if (lockOpen) {
      record.lockedOpen = true;
    }
    record.trigger.setAttribute("data-state", "open");
    record.trigger.setAttribute("aria-expanded", "true");
    record.content.hidden = false;
    record.content.style.pointerEvents = "auto";

    schedule(() => {
      updateSubmenuPosition(record);
      void record.content.offsetWidth;
      record.content.setAttribute("data-state", "open");
      record.content.setAttribute("aria-hidden", "false");
      clearMenuHighlights(record.content);
    });
  };

  const closeAllSubmenus = (immediate = false) => {
    const ordered = [...submenuRecords].sort(
      (left, right) => getRecordDepth(right) - getRecordDepth(left),
    );

    ordered.forEach((record) => closeSubmenuRecord(record, immediate));
  };

  const getChildRecords = (menuEl) =>
    submenuRecords.filter((record) => record.parentMenu === menuEl);

  const syncBranchForInteraction = (menuEl, targetNode, options = {}) => {
    if (rootClosing) return;
    if ((dropdown.getAttribute("data-state") || "closed") !== "open") return;
    if (!(menuEl instanceof HTMLElement)) return;
    const { openTarget = true } = options;
    const childRecords = getChildRecords(menuEl);
    if (!(targetNode instanceof Element)) return;

    const item = targetNode.closest(
      '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
    );
    if (!(item instanceof HTMLElement) || item.closest('[role="menu"]') !== menuEl) return;

    const targetRecord =
      childRecords.find((record) => record.trigger === item || record.trigger.contains(item))
      || null;

    childRecords.forEach((record) => {
      if (record === targetRecord) return;
      closeSubtree(record, false);
    });

    if (targetRecord && openTarget) {
      openSubmenuRecord(targetRecord);
    }
  };

  const activateItem = (item) => {
    if (!(item instanceof HTMLElement)) return;
    if (item.getAttribute("data-disabled") === "true") return;

    const slot = item.getAttribute("data-slot") || "";

    if (slot === "dropdown-menu-checkbox-item") {
      const nextChecked = item.getAttribute("aria-checked") !== "true";
      item.setAttribute("aria-checked", nextChecked ? "true" : "false");
      syncCheckboxItem(item);
      if (typeof item._ppOnCheckedChange === "function") {
        item._ppOnCheckedChange(nextChecked);
      }
      const detail = { checked: nextChecked };
      item.dispatchEvent(new CustomEvent("checkedchange", { detail, bubbles: true }));
      item.dispatchEvent(new CustomEvent("change", { detail, bubbles: true }));
    }

    if (slot === "dropdown-menu-radio-item") {
      const group = item.closest('[data-slot="dropdown-menu-radio-group"]');
      if (group instanceof HTMLElement) {
        const nextValue = item.getAttribute("data-value") || "";
        group.setAttribute("data-value", nextValue);
        syncRadioGroup(group);
        if (typeof group._ppOnValueChange === "function") {
          group._ppOnValueChange(nextValue);
        }
        const detail = { value: nextValue };
        group.dispatchEvent(new CustomEvent("valuechange", { detail, bubbles: true }));
        group.dispatchEvent(new CustomEvent("change", { detail, bubbles: true }));
      }
    }

    const keepOpen = item.getAttribute("data-menu-keep-open") === "true";
    if (!keepOpen && closeOnSelect) {
      focusTriggerAfterClose = true;
      closeAllSubmenus(false);
      clearAllMenuHighlights();
      dropdown.dispatchEvent(
        new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
          bubbles: false,
        }),
      );
    }
  };

  const ensureItemVisibleInMenu = (menuEl, itemEl) => {
    if (!(menuEl instanceof HTMLElement) || !(itemEl instanceof HTMLElement)) return;
    if (menuEl.scrollHeight <= menuEl.clientHeight) return;

    const menuRect = menuEl.getBoundingClientRect();
    const itemRect = itemEl.getBoundingClientRect();
    const padding = 6;

    const topLimit = menuRect.top + padding;
    const bottomLimit = menuRect.bottom - padding;

    if (itemRect.top < topLimit) {
      menuEl.scrollTop -= topLimit - itemRect.top;
      return;
    }

    if (itemRect.bottom > bottomLimit) {
      menuEl.scrollTop += itemRect.bottom - bottomLimit;
    }
  };

  const focusItemAt = (menuEl, items, index) => {
    if (!items.length) return;
    const normalizedIndex = Math.max(0, Math.min(index, items.length - 1));
    const item = items[normalizedIndex];
    if (!(item instanceof HTMLElement)) return;
    items.forEach((entry) => {
      if (entry instanceof HTMLElement) {
        entry.setAttribute("data-highlighted", entry === item ? "true" : "false");
      }
    });
    ensureItemVisibleInMenu(menuEl, item);
    try {
      item.focus({ preventScroll: true });
    } catch {
      item.focus();
    }
  };

  const bindMenuKeyboard = (menuEl, onEscapeLeft) => {
    const handler = (event) => {
      const items = getMenuItems(menuEl);
      const focusedItem =
        event.target instanceof Element
          ? event.target.closest(
              '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
            )
          : null;
      const currentIndex = items.findIndex((item) => item === focusedItem);

      if (event.key === "ArrowDown") {
        event.preventDefault();
        lastInteractionWasKeyboard = true;
        focusItemAt(menuEl, items, currentIndex >= 0 ? currentIndex + 1 : 0);
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        lastInteractionWasKeyboard = true;
        focusItemAt(menuEl, items, currentIndex >= 0 ? currentIndex - 1 : items.length - 1);
      }

      if (event.key === "Home") {
        event.preventDefault();
        lastInteractionWasKeyboard = true;
        focusItemAt(menuEl, items, 0);
      }

      if (event.key === "End") {
        event.preventDefault();
        lastInteractionWasKeyboard = true;
        focusItemAt(menuEl, items, items.length - 1);
      }

      if (event.key === "Enter" || event.key === " ") {
        if (focusedItem instanceof HTMLElement) {
          event.preventDefault();
          lastInteractionWasKeyboard = true;
          activateItem(focusedItem);
        }
      }

      if (event.key === "Escape") {
        event.preventDefault();
        onEscapeLeft?.("escape");
      }

      if (event.key === "ArrowLeft") {
        onEscapeLeft?.("left");
      }

      if (event.key === "ArrowRight") {
        onEscapeLeft?.("right");
      }
    };

    menuEl.addEventListener("keydown", handler);
    teardownCallbacks.push(() => menuEl.removeEventListener("keydown", handler));

    const onFocusIn = (event) => {
      if (!lastInteractionWasKeyboard) {
        clearMenuHighlights(menuEl);
        return;
      }

      const focusedItem =
        event.target instanceof Element
          ? event.target.closest(
              '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
            )
          : null;
      const items = getMenuItems(menuEl);
      items.forEach((item) => {
        if (item instanceof HTMLElement) {
          item.setAttribute(
            "data-highlighted",
            item === focusedItem ? "true" : "false",
          );
        }
      });
    };

    const onPointerDown = () => {
      lastInteractionWasKeyboard = false;
      clearMenuHighlights(menuEl);
    };

    menuEl.addEventListener("focusin", onFocusIn);
    menuEl.addEventListener("pointerdown", onPointerDown);
    teardownCallbacks.push(() => menuEl.removeEventListener("focusin", onFocusIn));
    teardownCallbacks.push(() => menuEl.removeEventListener("pointerdown", onPointerDown));
  };

  const bindSubmenus = () => {
    const subRoots = Array.from(
      contentEl.querySelectorAll('[data-slot="dropdown-menu-sub"]'),
    ).filter((node) => node instanceof HTMLElement);

    subRoots.forEach((subRoot) => {
      if (!(subRoot instanceof HTMLElement)) return;
      if (subRoot.dataset.submenuBound === "true") return;
      subRoot.dataset.submenuBound = "true";

      const subTrigger = subRoot.querySelector('[data-slot="dropdown-menu-sub-trigger"]');
      const subContent = subRoot.querySelector('[data-slot="dropdown-menu-sub-content"]');
      const parentMenu = subRoot.closest('[role="menu"]');
      if (
        !(subTrigger instanceof HTMLElement) ||
        !(subContent instanceof HTMLElement) ||
        !(parentMenu instanceof HTMLElement)
      ) {
        return;
      }

      if (subContent.parentElement === subRoot) {
        const placeholder = document.createComment("dropdown-sub-placeholder");
        subRoot.replaceChild(placeholder, subContent);
        document.body.appendChild(subContent);
      }

      const record = {
        root: subRoot,
        trigger: subTrigger,
        content: subContent,
        parentMenu,
        parentRecord: getSubmenuParentRecord(parentMenu),
        preferredSide: (subContent.getAttribute("data-side") || "right").toLowerCase(),
        preferredAlign: (subContent.getAttribute("data-align") || "start").toLowerCase(),
        isOpen: false,
        closeTimer: null,
        hoverCloseTimer: null,
        hideCleanup: null,
        lockedOpen: false,
      };
      submenuRecords.push(record);

      subTrigger.setAttribute("data-state", "closed");
      subTrigger.setAttribute("aria-expanded", "false");
      subContent.setAttribute("data-state", "closed");
      subContent.setAttribute("aria-hidden", "true");
      subContent.setAttribute("data-preferred-side", record.preferredSide);
      subContent.setAttribute("data-preferred-align", record.preferredAlign);
      subContent.hidden = true;
      subContent.style.pointerEvents = "none";
      clearMenuHighlights(subContent);

      const isWithinBranch = (node) => branchContainsNode(record, node);
      const getSubmenuSide = () =>
        (
          record.content.getAttribute("data-resolved-side")
          || record.content.getAttribute("data-side")
          || record.preferredSide
          || "right"
        ).toLowerCase();

      const getSubmenuOpenKey = () => {
        const side = (
          record.preferredSide
          || record.content.getAttribute("data-preferred-side")
          || record.content.getAttribute("data-side")
          || "right"
        ).toLowerCase();
        if (side === "left") return "ArrowLeft";
        if (side === "top") return "ArrowUp";
        if (side === "bottom") return "ArrowDown";
        return "ArrowRight";
      };

      const getSubmenuCloseReason = (reason) => {
        const side = getSubmenuSide();
        if (side === "left") return reason === "right";
        if (side === "top") return reason === "down";
        if (side === "bottom") return reason === "up";
        return reason === "left";
      };

      const shouldKeepHoverGracePeriod = (event) => {
        if (!(event instanceof MouseEvent)) return false;
        const side = record.preferredSide;
        const triggerRect = record.trigger.getBoundingClientRect();

        if (side === "right") return event.clientX >= triggerRect.right;
        if (side === "left") return event.clientX <= triggerRect.left;
        if (side === "bottom") return event.clientY >= triggerRect.bottom;
        if (side === "top") return event.clientY <= triggerRect.top;
        return false;
      };

      const scheduleHoverClose = (relatedTarget, event = null) => {
        if (record.lockedOpen) return;
        if (isWithinBranch(relatedTarget)) return;
        if (relatedTarget instanceof Element) {
          const siblingItem = relatedTarget.closest(
            '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
          );
          if (
            siblingItem instanceof HTMLElement
            && siblingItem.closest('[role="menu"]') === record.parentMenu
          ) {
            closeSubtree(record, false);
            return;
          }
        }
        if (!shouldKeepHoverGracePeriod(event)) {
          closeSubtree(record, false);
          return;
        }
        if (record.hoverCloseTimer !== null) {
          clearTimeout(record.hoverCloseTimer);
        }
        record.hoverCloseTimer = setTimeout(() => {
          record.hoverCloseTimer = null;
          if (record.lockedOpen) return;
          if (isWithinBranch(document.activeElement)) return;
          closeSubtree(record, false);
        }, 110);
      };

      let lastSubTriggerPointerType = "";

      const onTriggerEnter = (event) => {
        if (!shouldUseHoverInteraction(event)) return;
        lastInteractionWasKeyboard = false;
        clearMenuHighlights(record.parentMenu);
        record.lockedOpen = false;
        openSubmenuRecord(record);
      };

      const onContentEnter = (event) => {
        if (!shouldUseHoverInteraction(event)) return;
        lastInteractionWasKeyboard = false;
        clearMenuHighlights(record.content);
        openSubmenuRecord(record, { lockOpen: true });
      };

      const onTriggerLeave = (event) => {
        if (!shouldUseHoverInteraction(event)) return;
        scheduleHoverClose(event.relatedTarget, event);
      };

      const onContentLeave = (event) => {
        if (!shouldUseHoverInteraction(event)) return;
        if (record.lockedOpen) return;
        scheduleHoverClose(event.relatedTarget, event);
      };

      const onTriggerFocus = () => {
        record.lockedOpen = false;
      };

      const onContentFocus = () => openSubmenuRecord(record, { lockOpen: true });

      const onTriggerFocusOut = () => {
        if (record.lockedOpen) return;
        schedule(() => {
          if (record.lockedOpen) return;
          if (isWithinBranch(document.activeElement)) return;
          closeSubtree(record, false);
        });
      };

      const onContentFocusOut = () => {
        if (record.lockedOpen) return;
        schedule(() => {
          if (record.lockedOpen) return;
          if (isWithinBranch(document.activeElement)) return;
          closeSubtree(record, false);
        });
      };

      const onTriggerKeyDown = (event) => {
        const openKey = getSubmenuOpenKey();
        if (event.key !== openKey) return;
        event.preventDefault();
        event.stopPropagation();
        lastInteractionWasKeyboard = true;
        openSubmenuRecord(record, { lockOpen: true });
        schedule(() => {
          const items = getMenuItems(subContent);
          items[0]?.focus();
        });
      };

      const onTriggerPointerDown = (event) => {
        lastSubTriggerPointerType = event.pointerType || "";
        lastInteractionWasKeyboard = false;
        clearMenuHighlights(record.parentMenu);
      };

      const onTriggerClick = (event) => {
        if (!shouldUseTapInteraction(lastSubTriggerPointerType)) return;

        event.preventDefault();
        event.stopPropagation();

        if (record.isOpen) {
          closeSubtree(record, false);
          return;
        }

        clearMenuHighlights(record.parentMenu);
        clearMenuHighlights(record.content);
        openSubmenuRecord(record, { lockOpen: true });
      };

      subTrigger.addEventListener("mouseenter", onTriggerEnter);
      subContent.addEventListener("mouseenter", onContentEnter);
      subTrigger.addEventListener("mouseleave", onTriggerLeave);
      subContent.addEventListener("mouseleave", onContentLeave);
      subTrigger.addEventListener("focusin", onTriggerFocus);
      subContent.addEventListener("focusin", onContentFocus);
      subTrigger.addEventListener("focusout", onTriggerFocusOut);
      subContent.addEventListener("focusout", onContentFocusOut);
      subTrigger.addEventListener("keydown", onTriggerKeyDown);
      subTrigger.addEventListener("pointerdown", onTriggerPointerDown);
      subTrigger.addEventListener("click", onTriggerClick);

      teardownCallbacks.push(() => subTrigger.removeEventListener("mouseenter", onTriggerEnter));
      teardownCallbacks.push(() => subContent.removeEventListener("mouseenter", onContentEnter));
      teardownCallbacks.push(() => subTrigger.removeEventListener("mouseleave", onTriggerLeave));
      teardownCallbacks.push(() => subContent.removeEventListener("mouseleave", onContentLeave));
      teardownCallbacks.push(() => subTrigger.removeEventListener("focusin", onTriggerFocus));
      teardownCallbacks.push(() => subContent.removeEventListener("focusin", onContentFocus));
      teardownCallbacks.push(() => subTrigger.removeEventListener("focusout", onTriggerFocusOut));
      teardownCallbacks.push(() => subContent.removeEventListener("focusout", onContentFocusOut));
      teardownCallbacks.push(() => subTrigger.removeEventListener("keydown", onTriggerKeyDown));
      teardownCallbacks.push(() => subTrigger.removeEventListener("pointerdown", onTriggerPointerDown));
      teardownCallbacks.push(() => subTrigger.removeEventListener("click", onTriggerClick));

      bindMenuKeyboard(subContent, (reason) => {
        if (getSubmenuCloseReason(reason)) {
          closeSubmenuRecord(record, false);
          schedule(() => subTrigger.focus());
          return;
        }

        if (reason === "left" || reason === "right" || reason === "up" || reason === "down") {
          return;
        }

        closeAllSubmenus(false);
        clearAllMenuHighlights();
        dropdown.dispatchEvent(
          new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
            bubbles: false,
          }),
        );
        schedule(() => triggerEl.focus());
      });

      const onSubContentClick = (event) => {
        const target = event.target;
        if (!(target instanceof Element)) return;

        const item = target.closest(
          '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
        );
        if (!(item instanceof HTMLElement) || !subContent.contains(item)) return;
        activateItem(item);
      };

      subContent.addEventListener("click", onSubContentClick);
      teardownCallbacks.push(() => subContent.removeEventListener("click", onSubContentClick));

      const onSubMenuPointerOver = (event) => {
        if (!shouldUseHoverInteraction(event)) return;
        lastInteractionWasKeyboard = false;
        clearMenuHighlights(subContent);
        syncBranchForInteraction(subContent, event.target);
      };

      const onSubMenuFocusIn = (event) =>
        syncBranchForInteraction(subContent, event.target, { openTarget: false });

      subContent.addEventListener("pointerover", onSubMenuPointerOver);
      subContent.addEventListener("focusin", onSubMenuFocusIn);
      teardownCallbacks.push(() => subContent.removeEventListener("pointerover", onSubMenuPointerOver));
      teardownCallbacks.push(() => subContent.removeEventListener("focusin", onSubMenuFocusIn));
    });
  };

  const syncState = () => {
    const state = dropdown.getAttribute("data-state") || "closed";
    contentEl.setAttribute("data-state", state);
    const isHidden = portalEl.style.display === "none";

    if (state === "open" && isHidden) {
      rootClosing = false;
      cancelFrame();
      cancelCloseTimer();
      clearFrozenGeometry(contentEl);
      lockPageScroll();
      portalEl.style.display = "";
      contentEl.style.pointerEvents = "auto";
      contentEl.setAttribute("data-state", "closed");
      clearAllMenuHighlights();
      updateRootPosition();
      void contentEl.offsetWidth;
      frameId = requestAnimationFrame(() => {
        updateRootPosition();
        bindSubmenus();
        contentEl.setAttribute("data-state", "open");
        syncItemState(dropdown);
        clearAllMenuHighlights();
        if (!contentEl.contains(document.activeElement)) {
          contentEl.focus();
        }
        frameId = null;
      });
      return;
    }

    if (state === "open") {
      rootClosing = false;
      cancelCloseTimer();
      clearFrozenGeometry(contentEl);
      lockPageScroll();
      portalEl.style.display = "";
      contentEl.style.pointerEvents = "auto";
      updateRootPosition();
      bindSubmenus();
      contentEl.setAttribute("data-state", "open");
      syncItemState(dropdown);
      return;
    }

    cancelFrame();
    rootClosing = true;
    contentEl.style.pointerEvents = "none";
    freezeCurrentGeometry(contentEl);
    closeAllSubmenus(false);
    clearAllMenuHighlights();
    contentEl.setAttribute("data-state", "closed");
    cancelCloseTimer();
    closeTimerId = setTimeout(() => {
      if ((dropdown.getAttribute("data-state") || "closed") !== "closed") return;
      closeTimerId = null;
      finishAfterAnimation(contentEl, () => {
        if ((dropdown.getAttribute("data-state") || "closed") !== "closed") return;
        closeAllSubmenus(true);
        portalEl.style.display = "none";
        clearFrozenGeometry(contentEl);
        unlockPageScroll();
        rootClosing = false;
        if (focusTriggerAfterClose) {
          focusTriggerAfterClose = false;
          schedule(() => triggerEl.focus());
        }
      });
    }, 0);
  };

  bindMenuKeyboard(contentEl, (reason) => {
    if (reason !== "escape") return;
    closeAllSubmenus(false);
    clearAllMenuHighlights();
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
    schedule(() => triggerEl.focus());
  });

  const getClickedMenuItem = (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return null;

    const item = target.closest(
      '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
    );

    return item instanceof HTMLElement && contentEl.contains(item) ? item : null;
  };

  const onContentClickCapture = (event) => {
    const item = getClickedMenuItem(event);
    if (!item || item.getAttribute("data-disabled") === "true") return;

    const keepOpen = item.getAttribute("data-menu-keep-open") === "true";
    if (keepOpen || !closeOnSelect) return;

    // A menu item's application onclick may synchronously update PulsePoint
    // state and replace the trigger before this event bubbles back to the menu.
    // Complete the visual close in the component's capture phase while the
    // original anchor is still connected. The consumer keeps a normal onclick;
    // it does not need route-specific timing or lifecycle attributes.
    cancelFrame();
    cancelCloseTimer();
    rootClosing = true;
    freezeCurrentGeometry(contentEl);
    contentEl.style.pointerEvents = "none";
    contentEl.setAttribute("data-state", "closed");
  };

  const onContentClick = (event) => {
    const item = getClickedMenuItem(event);
    if (!item) return;
    activateItem(item);
  };

  const onRootMenuPointerOver = (event) => {
    if (!shouldUseHoverInteraction(event)) return;
    lastInteractionWasKeyboard = false;
    clearMenuHighlights(contentEl);
    syncBranchForInteraction(contentEl, event.target);
  };

  const onRootMenuFocusIn = (event) => {
    syncBranchForInteraction(contentEl, event.target, { openTarget: false });
  };

  const onDocumentPointerDown = (event) => {
    if (!closeOnOutsideClick) return;
    if (dropdown.getAttribute("data-state") !== "open") return;

    const target = event.target;
    if (!(target instanceof Node)) return;
    const insideSubmenu = submenuRecords.some(
      (record) => record.content.contains(target) || record.trigger.contains(target),
    );

    if (contentEl.contains(target) || dropdown.contains(target) || insideSubmenu) return;

    closeAllSubmenus(false);
    clearAllMenuHighlights();
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
  };

  const onDocumentKeyDown = (event) => {
    if (dropdown.getAttribute("data-state") !== "open") return;
    if (event.key !== "Escape") return;

    event.preventDefault();
    closeAllSubmenus(true);
    clearAllMenuHighlights();
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
    schedule(() => triggerEl.focus());
  };

  const onViewportChange = () => {
    if (rootClosing) return;
    if (dropdown.getAttribute("data-state") !== "open") return;
    updateRootPosition();
    submenuRecords.forEach((record) => {
      if (!record.isOpen) return;
      updateSubmenuPosition(record);
    });
  };

  syncState();

  const observer = new MutationObserver(syncState);
  observer.observe(dropdown, {
    attributes: true,
    attributeFilter: ["data-state"],
  });

  contentEl.addEventListener("click", onContentClickCapture, true);
  contentEl.addEventListener("click", onContentClick);
  contentEl.addEventListener("pointerover", onRootMenuPointerOver);
  contentEl.addEventListener("focusin", onRootMenuFocusIn);
  document.addEventListener("pointerdown", onDocumentPointerDown);
  document.addEventListener("keydown", onDocumentKeyDown);
  document.addEventListener("wheel", preventOutsideScroll, scrollLockOptions);
  document.addEventListener("touchmove", preventOutsideScroll, scrollLockOptions);
  window.addEventListener("resize", onViewportChange);
  window.addEventListener("scroll", onViewportChange, true);

  if (window.visualViewport) {
    window.visualViewport.addEventListener("resize", onViewportChange);
    window.visualViewport.addEventListener("scroll", onViewportChange);
  }

  return () => {
    cancelFrame();
    cancelCloseTimer();
    closeAllSubmenus(false);
    unlockPageScroll();
    observer.disconnect();
    contentEl.removeEventListener("click", onContentClickCapture, true);
    contentEl.removeEventListener("click", onContentClick);
    contentEl.removeEventListener("pointerover", onRootMenuPointerOver);
    contentEl.removeEventListener("focusin", onRootMenuFocusIn);
    document.removeEventListener("pointerdown", onDocumentPointerDown);
    document.removeEventListener("keydown", onDocumentKeyDown);
    document.removeEventListener("wheel", preventOutsideScroll, scrollLockOptions);
    document.removeEventListener("touchmove", preventOutsideScroll, scrollLockOptions);
    window.removeEventListener("resize", onViewportChange);
    window.removeEventListener("scroll", onViewportChange, true);

    if (window.visualViewport) {
      window.visualViewport.removeEventListener("resize", onViewportChange);
      window.visualViewport.removeEventListener("scroll", onViewportChange);
    }

    teardownCallbacks.forEach((cleanup) => cleanup());
  };
}, []);
""".strip()


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
    children = children.replace(_DROPDOWN_MENU_ID_PLACEHOLDER, dropdown_menu_id)
    children = children.replace(
        _DROPDOWN_MENU_TRIGGER_ID_PLACEHOLDER,
        dropdown_menu_trigger_id,
    )

    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu",
            "class": computed_class,
            "data-state": '{open ? "open" : "closed"}',
            "data-dropdown-menu-event-id": dropdown_menu_event_id,
            "data-close-on-outside-click": str(parse_bool(closeOnOutsideClick, True)).lower(),
            "data-close-on-select": str(parse_bool(closeOnSelect, True)).lower(),
            "pp-ref": "rootRef",
        },
        props,
    )

    return html(r"""
<div is-open="{{ open }}" on-open-change="{{ onOpenChange }}">
  <div {{ attributes }}>{{ children }}</div>

  <script>
    const resolveRuntimeDropdownIds = (dropdown) => {
      if (!(dropdown instanceof HTMLElement)) return null;

      const ownerBoundary =
        dropdown.parentElement?.closest("[pp-component]")
        || dropdown.closest("[pp-component]");
      const ownerComponentId = ownerBoundary?.getAttribute("pp-component") || "";
      if (!ownerComponentId) return null;

      const normalizedId = ownerComponentId.replace(/[^a-zA-Z0-9_-]+/g, "_");
      const runtimeIds = {
        eventId: `dropdown-event-${normalizedId}`,
        contentId: `dropdown-content-${normalizedId}`,
        triggerId: `dropdown-trigger-${normalizedId}`,
      };

      dropdown.setAttribute("data-dropdown-menu-event-id", runtimeIds.eventId);
      dropdown.setAttribute("data-dropdown-menu-content-id", runtimeIds.contentId);
      dropdown.setAttribute("data-dropdown-menu-trigger-id", runtimeIds.triggerId);

      return runtimeIds;
    };

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

    const parseBool = (value) => {
      if (value === true) return true;
      if (typeof value !== "string") return false;

      const normalized = value.trim().toLowerCase();
      return normalized === "" || ["true", "1", "yes", "on"].includes(normalized);
    };

    const { isOpen: rawIsOpen, onOpenChange } = pp.props;
    const controlledIsOpen = normalizeControlledValue(rawIsOpen);
    const isControlled = controlledIsOpen !== undefined;

    const [internalOpen, setInternalOpen] = pp.state(false);
    const open = isControlled ? parseBool(controlledIsOpen) : internalOpen;
    const rootRef = pp.ref();

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

    const openMenu = () => updateOpen(true);
    const closeMenu = () => updateOpen(false);
    const toggleMenu = () => {
      const currentState = rootRef.current?.getAttribute("data-state") === "open";
      updateOpen(!currentState);
    };

    const onOpen = (event) => {
      event.stopPropagation();
      openMenu();
    };

    const onClose = (event) => {
      event.stopPropagation();
      closeMenu();
    };

    const onToggle = (event) => {
      event.stopPropagation();
      toggleMenu();
    };

    pp.effect(() => {
      const el = rootRef.current;
      if (!(el instanceof HTMLElement)) return;
      const dropdownMenuId = resolveRuntimeDropdownIds(el)?.eventId;
      if (!dropdownMenuId) return;

      el.addEventListener(`dropdown-open:${dropdownMenuId}`, onOpen);
      el.addEventListener(`dropdown-close:${dropdownMenuId}`, onClose);
      el.addEventListener(`dropdown-toggle:${dropdownMenuId}`, onToggle);

      return () => {
        el.removeEventListener(`dropdown-open:${dropdownMenuId}`, onOpen);
        el.removeEventListener(`dropdown-close:${dropdownMenuId}`, onClose);
        el.removeEventListener(`dropdown-toggle:${dropdownMenuId}`, onToggle);
      };
    }, []);
  </script>
</div>
""",
        attributes=attrs,
        children=children,
        open=open,
        onOpenChange=onOpenChange,
    )


@component
def DropdownMenuTrigger(asChild: bool | str | None = False, **props) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
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
        "aria-controls": _DROPDOWN_MENU_ID_PLACEHOLDER,
        "data-state": "closed",
        "pp-ref": "triggerRef",
        "class": trigger_class,
        "id": _DROPDOWN_MENU_TRIGGER_ID_PLACEHOLDER,
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

    return html(r"""
<div>
  {{ trigger }}

  <script>
    const triggerRef = pp.ref();

    const resolveRuntimeDropdownIds = (dropdown) => {
      if (!(dropdown instanceof HTMLElement)) return null;

      const ownerBoundary =
        dropdown.parentElement?.closest("[pp-component]")
        || dropdown.closest("[pp-component]");
      const ownerComponentId = ownerBoundary?.getAttribute("pp-component") || "";
      if (!ownerComponentId) return null;

      const normalizedId = ownerComponentId.replace(/[^a-zA-Z0-9_-]+/g, "_");
      const runtimeIds = {
        eventId: `dropdown-event-${normalizedId}`,
        contentId: `dropdown-content-${normalizedId}`,
        triggerId: `dropdown-trigger-${normalizedId}`,
      };

      dropdown.setAttribute("data-dropdown-menu-event-id", runtimeIds.eventId);
      dropdown.setAttribute("data-dropdown-menu-content-id", runtimeIds.contentId);
      dropdown.setAttribute("data-dropdown-menu-trigger-id", runtimeIds.triggerId);

      return runtimeIds;
    };

    const scheduleFocus = (callback) => {
      if (typeof requestAnimationFrame === "function") {
        requestAnimationFrame(() => requestAnimationFrame(() => callback()));
        return;
      }

      setTimeout(callback, 0);
    };

    const getMenuItems = (container) => {
      if (!(container instanceof HTMLElement)) return [];

      return Array.from(
        container.querySelectorAll(
          '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
        ),
      ).filter((item) => {
        if (!(item instanceof HTMLElement)) return false;
        if (item.getAttribute("data-disabled") === "true") return false;
        return item.offsetParent !== null;
      });
    };

    pp.effect(() => {
      const el = triggerRef.current;
      const dropdown = el?.closest('[data-slot="dropdown-menu"]');
      if (!(el instanceof HTMLElement) || !(dropdown instanceof HTMLElement)) return;

      const runtimeIds = resolveRuntimeDropdownIds(dropdown);
      const dropdownMenuId = runtimeIds?.eventId;
      if (!dropdownMenuId) return;

      const syncTriggerState = () => {
        const state = dropdown.getAttribute("data-state") || "closed";
        el.setAttribute("data-state", state);
        el.setAttribute("aria-expanded", state === "open" ? "true" : "false");
        if (runtimeIds?.contentId) {
          el.setAttribute("aria-controls", runtimeIds.contentId);
        }
        if (runtimeIds?.triggerId) {
          el.setAttribute("id", runtimeIds.triggerId);
        }
      };

      const focusMenuItemAt = (index) => {
        const contentId = el.getAttribute("aria-controls");
        const contentEl = contentId
          ? document.getElementById(contentId)
          : document.querySelector('[data-slot="dropdown-menu-content"]');
        if (!(contentEl instanceof HTMLElement)) return;

        const items = getMenuItems(contentEl);
        if (!items.length) return;

        const normalizedIndex = ((index % items.length) + items.length) % items.length;
        items[normalizedIndex]?.focus();
      };

      const handleClick = (event) => {
        event.stopPropagation();
        el.dispatchEvent(
          new CustomEvent(`dropdown-toggle:${dropdownMenuId}`, {
            bubbles: true,
            composed: true,
          }),
        );
      };

      const handleKeyDown = (event) => {
        if (["Enter", " ", "ArrowDown", "ArrowUp"].includes(event.key)) {
          event.preventDefault();
        }

        if (event.key === "Enter" || event.key === " ") {
          el.dispatchEvent(
            new CustomEvent(`dropdown-toggle:${dropdownMenuId}`, {
              bubbles: true,
              composed: true,
            }),
          );
          return;
        }

        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          el.dispatchEvent(
            new CustomEvent(`dropdown-open:${dropdownMenuId}`, {
              bubbles: true,
              composed: true,
            }),
          );

          scheduleFocus(() => {
            const contentEl = dropdown.querySelector('[data-slot="dropdown-menu-content"]');
            const items = getMenuItems(contentEl);
            if (!items.length) return;
            focusMenuItemAt(event.key === "ArrowDown" ? 0 : items.length - 1);
          });
        }
      };

      syncTriggerState();

      const observer = new MutationObserver(syncTriggerState);
      observer.observe(dropdown, {
        attributes: true,
        attributeFilter: ["data-state"],
      });

      el.addEventListener("click", handleClick);
      el.addEventListener("keydown", handleKeyDown);

      return () => {
        observer.disconnect();
        el.removeEventListener("click", handleClick);
        el.removeEventListener("keydown", handleKeyDown);
      };
    }, []);
  </script>
</div>
""",
        trigger=trigger,
    )


@component
def DropdownMenuContent(
    side: DropdownMenuSide | str = "bottom",
    align: DropdownMenuAlign | str = "center",
    sideOffset: int | str = 4,
    **props,
) -> str:
    normalized_side = _normalize_choice(side, {"top", "right", "bottom", "left"}, "bottom")
    normalized_align = _normalize_choice(align, {"start", "center", "end"}, "center")

    try:
        normalized_side_offset = max(float(sideOffset), 0)
    except TypeError, ValueError:
        normalized_side_offset = 4.0

    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    attrs = get_attributes(
        {
            "data-slot": "dropdown-menu-content",
            "role": "menu",
            "class": merge_classes(
                "fixed z-50 min-w-56 overflow-visible rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md outline-none pointer-events-auto "
                "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 "
                "data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95 "
                "data-[side=bottom]:data-[state=open]:slide-in-from-top-2 data-[side=bottom]:data-[state=closed]:slide-out-to-top-2 "
                "data-[side=top]:data-[state=open]:slide-in-from-bottom-2 data-[side=top]:data-[state=closed]:slide-out-to-bottom-2 "
                "data-[side=left]:data-[state=open]:slide-in-from-right-2 data-[side=left]:data-[state=closed]:slide-out-to-right-2 "
                "data-[side=right]:data-[state=open]:slide-in-from-left-2 data-[side=right]:data-[state=closed]:slide-out-to-left-2",
                incoming_class,
            ),
            "id": _DROPDOWN_MENU_ID_PLACEHOLDER,
            "aria-orientation": "vertical",
            "aria-labelledby": _DROPDOWN_MENU_TRIGGER_ID_PLACEHOLDER,
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
    script = _dropdown_menu_content_script()

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
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
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
    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)


@component
def DropdownMenuItem(
    inset: bool = False,
    asChild: bool | str | None = False,
    disabled: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    as_child = parse_bool(pop_prop_alias(props, "asChild", asChild))
    is_disabled = parse_bool(pop_prop_alias(props, "disabled", disabled))

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
    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)


@component
def DropdownMenuCheckboxItem(
    checked: bool | str = False,
    onCheckedChange: Optional[str] = None,
    disabled: bool | str | None = False,
    **props,
) -> str:
    incoming_class = props.pop("class", "")
    children = props.pop("children", "")
    is_checked = parse_bool(checked)
    is_disabled = parse_bool(pop_prop_alias(props, "disabled", disabled))

    indicator = Check(class_name="h-4 w-4")
    indicator_html = Markup(
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

    return html(r"""
<div {{ attributes }}
     pp-ref="rootRef"
     checked-value="{{ rawChecked }}"
     disabled-value="{{ disabled }}"
     on-checked-change="{{ onCheckedChange }}">
  {{ indicator }}
  {{ children }}

  <script>
    const rootRef = pp.ref();

    const parseBoolish = (value, fallback = false) => {
      if (value == null) return fallback;
      if (typeof value === "boolean") return value;
      if (typeof value !== "string") return Boolean(value);

      const normalized = value.trim().toLowerCase();
      if (["", "true", "1", "yes", "on"].includes(normalized)) return true;
      if (["false", "0", "no", "off", "none", "null", "undefined"].includes(normalized)) {
        return false;
      }

      return fallback;
    };

    pp.effect(() => {
      const el = rootRef.current;
      if (!(el instanceof HTMLElement)) return;

      const nextChecked = parseBoolish(pp.props.checkedValue, {{ checked | json }});
      const nextDisabled = parseBoolish(pp.props.disabledValue, {{ disabled | json }});

      el._ppOnCheckedChange =
        typeof pp.props.onCheckedChange === "function"
          ? pp.props.onCheckedChange
          : null;

      el.setAttribute("aria-checked", nextChecked ? "true" : "false");
      el.setAttribute("data-checked", nextChecked ? "true" : "false");
      el.setAttribute("data-disabled", nextDisabled ? "true" : "false");

      const indicator = el.querySelector("[data-checkbox-indicator]");
      if (indicator instanceof HTMLElement) {
        indicator.classList.toggle("hidden", !nextChecked);
      }
    }, [pp.props.checkedValue, pp.props.disabledValue, pp.props.onCheckedChange]);
  </script>
</div>
""",
        attributes=attrs,
        children=children,
        indicator=Markup(indicator_html),
        checked=is_checked,
        rawChecked=checked,
        disabled=is_disabled,
        onCheckedChange=onCheckedChange,
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

    return html(r"""
<div {{ attributes }}
     pp-ref="rootRef"
     value-prop="{{ value }}"
     on-value-change="{{ onValueChange }}">
  {{ children }}

  <script>
    const rootRef = pp.ref();

    const normalizeValue = (value) => {
      if (value == null) return "";
      if (typeof value !== "string") return String(value);

      const normalized = value.trim().toLowerCase();
      if (["null", "undefined"].includes(normalized)) return "";
      return value;
    };

    const syncRadioItems = (group, nextValue) => {
      group
        .querySelectorAll('[data-slot="dropdown-menu-radio-item"]')
        .forEach((item) => {
          if (!(item instanceof HTMLElement)) return;

          const itemValue = normalizeValue(
            item.getAttribute("data-value"),
          );
          const isChecked = nextValue !== "" && itemValue === nextValue;

          item.setAttribute("aria-checked", isChecked ? "true" : "false");
          item.setAttribute("data-checked", isChecked ? "true" : "false");

          const indicator = item.querySelector("[data-radio-indicator]");
          if (indicator instanceof HTMLElement) {
            indicator.classList.toggle("hidden", !isChecked);
          }
        });
    };

    pp.effect(() => {
      const el = rootRef.current;
      if (!(el instanceof HTMLElement)) return;

      const nextValue = normalizeValue(pp.props.valueProp);
      el._ppOnValueChange =
        typeof pp.props.onValueChange === "function"
          ? pp.props.onValueChange
          : null;
      el.setAttribute("value", nextValue);
      el.setAttribute("data-value", nextValue);
      syncRadioItems(el, nextValue);
    }, [pp.props.valueProp, pp.props.onValueChange]);
  </script>
</div>
""",
        attributes=attrs,
        children=children,
        value=value,
        onValueChange=onValueChange,
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
    is_checked = parse_bool(checked)
    is_disabled = parse_bool(pop_prop_alias(props, "disabled", disabled))

    indicator_html = Markup(
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

    return html(r"""<div {{ attrs }}>{{ indicator_html }}{{ children }}</div>""",
        attrs=attrs,
        indicator_html=indicator_html,
        children=children,
    )


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

    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)


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

    return html(r"""<div {{ attrs }}></div>""", attrs=attrs)


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

    return html(r"""<span {{ attrs }}>{{ children }}</span>""", attrs=attrs, children=children)


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

    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)


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

    return html(r"""
<div {{ attrs }}>
  {{ children }}
  {{ chevron_right_icon }}
</div>
""",
        attrs=attrs,
        children=children,
        chevron_right_icon=chevron_right_icon,
    )


@component
def DropdownMenuSubContent(
    side: DropdownMenuSide | str = "right",
    align: DropdownMenuAlign | str = "start",
    **props,
) -> str:
    normalized_side = _normalize_choice(side, {"top", "right", "bottom", "left"}, "right")
    normalized_align = _normalize_choice(align, {"start", "center", "end"}, "start")
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
                "fixed z-[60] min-w-[8rem] rounded-md border bg-popover p-1 text-popover-foreground shadow-lg outline-hidden "
                "data-[state=open]:animate-in data-[state=closed]:animate-out "
                "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 "
                "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 "
                "data-[side=bottom]:data-[state=open]:slide-in-from-top-2 data-[side=bottom]:data-[state=closed]:slide-out-to-top-2 "
                "data-[side=top]:data-[state=open]:slide-in-from-bottom-2 data-[side=top]:data-[state=closed]:slide-out-to-bottom-2 "
                "data-[side=left]:data-[state=open]:slide-in-from-right-2 data-[side=left]:data-[state=closed]:slide-out-to-right-2 "
                "data-[side=right]:data-[state=open]:slide-in-from-left-2 data-[side=right]:data-[state=closed]:slide-out-to-left-2",
                incoming_class,
            ),
        },
        props,
    )

    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)
