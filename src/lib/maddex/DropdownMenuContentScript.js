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

const updateFloatingPosition = (anchorEl, menuEl, preferredSide, preferredAlign, sideOffset) => {
  if (!(anchorEl instanceof HTMLElement) || !(menuEl instanceof HTMLElement)) return;

  const viewportPadding = 8;
  const anchorRect = anchorEl.getBoundingClientRect();
  menuEl.style.maxHeight = "";
  menuEl.style.overflowY = "";
  menuEl.style.overscrollBehavior = "";

  const menuRect = menuEl.getBoundingClientRect();
  const naturalWidth = menuEl.scrollWidth || menuEl.offsetWidth || menuRect.width;
  const naturalHeight = menuEl.scrollHeight || menuEl.offsetHeight || menuRect.height;
  const availableTop = Math.max(0, anchorRect.top - viewportPadding - sideOffset);
  const availableBottom = Math.max(
    0,
    window.innerHeight - anchorRect.bottom - viewportPadding - sideOffset,
  );
  const availableLeft = Math.max(0, anchorRect.left - viewportPadding - sideOffset);
  const availableRight = Math.max(
    0,
    window.innerWidth - anchorRect.right - viewportPadding - sideOffset,
  );

  const availableForSide = (side) => {
    if (side === "top") return availableTop;
    if (side === "bottom") return availableBottom;
    if (side === "left") return availableLeft;
    return availableRight;
  };

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
    if (side === "top") return coords.top < viewportPadding;
    if (side === "right") return coords.left + renderedWidth > window.innerWidth - viewportPadding;
    if (side === "left") return coords.left < viewportPadding;
    return coords.top + renderedHeight > window.innerHeight - viewportPadding;
  };

  const oppositeSide = {
    top: "bottom",
    right: "left",
    bottom: "top",
    left: "right",
  };

  let actualSide = preferredSide;

  const naturalMainAxis =
    preferredSide === "left" || preferredSide === "right" ? naturalWidth : naturalHeight;
  const preferredAvailable = availableForSide(preferredSide);
  const oppositeAvailable = availableForSide(oppositeSide[preferredSide] || preferredSide);

  if (naturalMainAxis > preferredAvailable && oppositeAvailable > preferredAvailable) {
    actualSide = oppositeSide[preferredSide] || preferredSide;
  }

  let renderedWidth = naturalWidth;
  let renderedHeight = naturalHeight;

  if (actualSide === "top" || actualSide === "bottom") {
    const availableHeight = Math.max(
      120,
      Math.min(window.innerHeight - viewportPadding * 2, availableForSide(actualSide)),
    );
    if (naturalHeight > availableHeight) {
      menuEl.style.maxHeight = `${Math.round(availableHeight)}px`;
      menuEl.style.overflowY = "auto";
      menuEl.style.overscrollBehavior = "contain";
      renderedHeight = availableHeight;
    }
  } else {
    const availableHeight = Math.max(120, window.innerHeight - viewportPadding * 2);
    if (naturalHeight > availableHeight) {
      menuEl.style.maxHeight = `${Math.round(availableHeight)}px`;
      menuEl.style.overflowY = "auto";
      menuEl.style.overscrollBehavior = "contain";
      renderedHeight = availableHeight;
    }
    const availableWidth = Math.max(
      160,
      Math.min(window.innerWidth - viewportPadding * 2, availableForSide(actualSide)),
    );
    renderedWidth = Math.min(naturalWidth, availableWidth);
  }

  let coords = placeForSide(actualSide);

  if (shouldFlip(actualSide, coords)) {
    actualSide = oppositeSide[actualSide] || preferredSide;
    menuEl.style.maxHeight = "";
    menuEl.style.overflowY = "";
    menuEl.style.overscrollBehavior = "";
    renderedWidth = naturalWidth;
    renderedHeight = naturalHeight;
    if (actualSide === "top" || actualSide === "bottom") {
      const availableHeight = Math.max(
        120,
        Math.min(window.innerHeight - viewportPadding * 2, availableForSide(actualSide)),
      );
      if (naturalHeight > availableHeight) {
        menuEl.style.maxHeight = `${Math.round(availableHeight)}px`;
        menuEl.style.overflowY = "auto";
        menuEl.style.overscrollBehavior = "contain";
        renderedHeight = availableHeight;
      }
    }
    coords = placeForSide(actualSide);
  }

  const maxLeft = Math.max(viewportPadding, window.innerWidth - renderedWidth - viewportPadding);
  const maxTop = Math.max(viewportPadding, window.innerHeight - renderedHeight - viewportPadding);
  coords.left = clamp(coords.left, viewportPadding, maxLeft);
  coords.top = clamp(coords.top, viewportPadding, maxTop);

  menuEl.setAttribute("data-side", actualSide);
  menuEl.style.position = "fixed";
  menuEl.style.left = `${Math.round(coords.left)}px`;
  menuEl.style.top = `${Math.round(coords.top)}px`;
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

  const triggerEl = dropdown.querySelector('[data-slot="dropdown-menu-trigger"]');
  if (!(triggerEl instanceof HTMLElement)) return;

  const dropdownMenuId = dropdown.getAttribute("data-dropdown-menu-event-id");
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
  const previousBodyOverflow = document.body.style.overflow;
  const submenuRecords = [];
  const teardownCallbacks = [];

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
    updateFloatingPosition(
      triggerEl,
      contentEl,
      preferredSide,
      preferredAlign,
      sideOffset,
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
    const alreadyClosing =
      !record.isOpen && record.content.getAttribute("data-state") === "closed";

    if (alreadyClosing && !immediate) {
      return;
    }

    if (record.hideCleanup) {
      record.hideCleanup();
      record.hideCleanup = null;
    }

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

  const closeSubtree = (record, immediate = false, stagger = true) => {
    if (!record) return;
    const branch = [record, ...collectDescendants(record)].sort(
      (left, right) => getRecordDepth(right) - getRecordDepth(left),
    );

    if (immediate) {
      branch.forEach((entry) => closeSubmenuRecord(entry, true));
      return;
    }

    branch.forEach((entry, index) => {
      const delay = stagger ? index * 28 : 0;
      if (entry.closeTimer !== null) {
        clearTimeout(entry.closeTimer);
        entry.closeTimer = null;
      }
      entry.closeTimer = setTimeout(() => {
        entry.closeTimer = null;
        closeSubmenuRecord(entry, false);
      }, delay);
    });
  };

  const closeSiblingSubmenus = (record) => {
    submenuRecords.forEach((candidate) => {
      if (candidate === record) return;
      if (candidate.parentMenu !== record.parentMenu) return;
      closeSubtree(candidate, false, false);
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

    record.isOpen = true;
    if (lockOpen) {
      record.lockedOpen = true;
    }
    record.trigger.setAttribute("data-state", "open");
    record.trigger.setAttribute("aria-expanded", "true");
    record.content.hidden = false;
    record.content.style.pointerEvents = "auto";

    schedule(() => {
      updateFloatingPosition(
        record.trigger,
        record.content,
        record.preferredSide,
        record.preferredAlign,
        0,
      );
      void record.content.offsetWidth;
      record.content.setAttribute("data-state", "open");
      record.content.setAttribute("aria-hidden", "false");
    });
  };

  const closeAllSubmenus = (immediate = false) => {
    const ordered = [...submenuRecords].sort(
      (left, right) => getRecordDepth(right) - getRecordDepth(left),
    );

    ordered.forEach((record) => {
      if (record.closeTimer !== null) {
        clearTimeout(record.closeTimer);
        record.closeTimer = null;
      }
      if (record.hoverCloseTimer !== null) {
        clearTimeout(record.hoverCloseTimer);
        record.hoverCloseTimer = null;
      }
      closeSubmenuRecord(record, immediate);
    });
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
        focusItemAt(menuEl, items, currentIndex >= 0 ? currentIndex + 1 : 0);
      }

      if (event.key === "ArrowUp") {
        event.preventDefault();
        focusItemAt(menuEl, items, currentIndex >= 0 ? currentIndex - 1 : items.length - 1);
      }

      if (event.key === "Home") {
        event.preventDefault();
        focusItemAt(menuEl, items, 0);
      }

      if (event.key === "End") {
        event.preventDefault();
        focusItemAt(menuEl, items, items.length - 1);
      }

      if (event.key === "Enter" || event.key === " ") {
        if (focusedItem instanceof HTMLElement) {
          event.preventDefault();
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

    menuEl.addEventListener("focusin", onFocusIn);
    teardownCallbacks.push(() => menuEl.removeEventListener("focusin", onFocusIn));
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

      const isWithinBranch = (node) => branchContainsNode(record, node);
      const getSubmenuSide = () =>
        (
          record.content.getAttribute("data-resolved-side")
          || record.content.getAttribute("data-side")
          || record.preferredSide
          || "right"
        ).toLowerCase();
      const getSubmenuOpenKey = () => {
        const side = getSubmenuSide();
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
            closeSubtree(record, false, false);
            return;
          }
        }
        if (!shouldKeepHoverGracePeriod(event)) {
          closeSubtree(record, false, false);
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

      const onTriggerEnter = () => {
        record.lockedOpen = false;
        openSubmenuRecord(record);
      };
      const onContentEnter = () => openSubmenuRecord(record, { lockOpen: true });
      const onTriggerLeave = (event) => scheduleHoverClose(event.relatedTarget, event);
      const onContentLeave = (event) => {
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
        openSubmenuRecord(record, { lockOpen: true });
        schedule(() => {
          const items = getMenuItems(subContent);
          items[0]?.focus();
        });
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

      teardownCallbacks.push(() => subTrigger.removeEventListener("mouseenter", onTriggerEnter));
      teardownCallbacks.push(() => subContent.removeEventListener("mouseenter", onContentEnter));
      teardownCallbacks.push(() => subTrigger.removeEventListener("mouseleave", onTriggerLeave));
      teardownCallbacks.push(() => subContent.removeEventListener("mouseleave", onContentLeave));
      teardownCallbacks.push(() => subTrigger.removeEventListener("focusin", onTriggerFocus));
      teardownCallbacks.push(() => subContent.removeEventListener("focusin", onContentFocus));
      teardownCallbacks.push(() => subTrigger.removeEventListener("focusout", onTriggerFocusOut));
      teardownCallbacks.push(() => subContent.removeEventListener("focusout", onContentFocusOut));
      teardownCallbacks.push(() => subTrigger.removeEventListener("keydown", onTriggerKeyDown));

      bindMenuKeyboard(subContent, (reason) => {
        if (getSubmenuCloseReason(reason)) {
          closeSubmenuRecord(record, false);
          schedule(() => subTrigger.focus());
          return;
        }

        closeAllSubmenus(false);
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

      const onSubMenuPointerOver = (event) => syncBranchForInteraction(subContent, event.target);
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
      document.body.style.overflow = "hidden";
      portalEl.style.display = "";
      contentEl.style.pointerEvents = "auto";
      contentEl.setAttribute("data-state", "closed");
      updateRootPosition();
      void contentEl.offsetWidth;
      frameId = requestAnimationFrame(() => {
        updateRootPosition();
        bindSubmenus();
        contentEl.setAttribute("data-state", "open");
        syncItemState(dropdown);
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
      document.body.style.overflow = "hidden";
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
        document.body.style.overflow = previousBodyOverflow;
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
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
    schedule(() => triggerEl.focus());
  });

  const onContentClick = (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const item = target.closest(
      '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
    );

    if (!(item instanceof HTMLElement) || !contentEl.contains(item)) return;
    activateItem(item);
  };

  const onRootMenuPointerOver = (event) => {
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
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
    schedule(() => triggerEl.focus());
  };

  const onViewportChange = () => {
    if (dropdown.getAttribute("data-state") !== "open") return;
    updateRootPosition();
    submenuRecords.forEach((record) => {
      if (!record.isOpen) return;
      updateFloatingPosition(
        record.trigger,
        record.content,
        record.preferredSide,
        record.preferredAlign,
        0,
      );
    });
  };

  syncState();

  const observer = new MutationObserver(syncState);
  observer.observe(dropdown, {
    attributes: true,
    attributeFilter: ["data-state"],
  });

  contentEl.addEventListener("click", onContentClick);
  contentEl.addEventListener("pointerover", onRootMenuPointerOver);
  contentEl.addEventListener("focusin", onRootMenuFocusIn);
  document.addEventListener("pointerdown", onDocumentPointerDown);
  document.addEventListener("keydown", onDocumentKeyDown);
  window.addEventListener("resize", onViewportChange);
  window.addEventListener("scroll", onViewportChange, true);

  return () => {
    cancelFrame();
    cancelCloseTimer();
    closeAllSubmenus(false);
    document.body.style.overflow = previousBodyOverflow;
    observer.disconnect();
    contentEl.removeEventListener("click", onContentClick);
    contentEl.removeEventListener("pointerover", onRootMenuPointerOver);
    contentEl.removeEventListener("focusin", onRootMenuFocusIn);
    document.removeEventListener("pointerdown", onDocumentPointerDown);
    document.removeEventListener("keydown", onDocumentKeyDown);
    window.removeEventListener("resize", onViewportChange);
    window.removeEventListener("scroll", onViewportChange, true);
    teardownCallbacks.forEach((cleanup) => cleanup());
  };
}, []);
