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

pp.effect(() => {
  const portalEl = portalRef.current;
  const contentEl = contentBoxRef.current;
  const dropdown = portal.sourceParent?.closest('[data-slot="dropdown-menu"]');
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
  const preferredAlign = (contentEl.getAttribute("data-align") || "end").toLowerCase();
  const sideOffset = parseNumber(contentEl.getAttribute("data-side-offset"), 4);
  const closeOnOutsideClick = parseBool(
    dropdown.getAttribute("data-close-on-outside-click"),
  );
  const closeOnSelect = parseBool(dropdown.getAttribute("data-close-on-select"));

  let frameId = null;

  const cancelFrame = () => {
    if (frameId !== null) {
      cancelAnimationFrame(frameId);
      frameId = null;
    }
  };

  const updatePosition = () => {
    const viewportPadding = 8;
    const triggerRect = triggerEl.getBoundingClientRect();

    contentEl.style.left = "0px";
    contentEl.style.top = "0px";

    const contentRect = contentEl.getBoundingClientRect();
    const maxLeft = Math.max(
      viewportPadding,
      window.innerWidth - contentRect.width - viewportPadding,
    );
    const maxTop = Math.max(
      viewportPadding,
      window.innerHeight - contentRect.height - viewportPadding,
    );

    const alignedLeft = () => {
      if (preferredAlign === "start") return triggerRect.left;
      if (preferredAlign === "end") return triggerRect.right - contentRect.width;

      return triggerRect.left + (triggerRect.width - contentRect.width) / 2;
    };

    const alignedTop = () => {
      if (preferredAlign === "start") return triggerRect.top;
      if (preferredAlign === "end") return triggerRect.bottom - contentRect.height;

      return triggerRect.top + (triggerRect.height - contentRect.height) / 2;
    };

    const placeForSide = (side) => {
      if (side === "top") {
        return {
          top: triggerRect.top - contentRect.height - sideOffset,
          left: alignedLeft(),
        };
      }

      if (side === "right") {
        return {
          top: alignedTop(),
          left: triggerRect.right + sideOffset,
        };
      }

      if (side === "left") {
        return {
          top: alignedTop(),
          left: triggerRect.left - contentRect.width - sideOffset,
        };
      }

      return {
        top: triggerRect.bottom + sideOffset,
        left: alignedLeft(),
      };
    };

    const shouldFlip = (side, coords) => {
      if (side === "top") return coords.top < viewportPadding;
      if (side === "right") {
        return coords.left + contentRect.width > window.innerWidth - viewportPadding;
      }
      if (side === "left") return coords.left < viewportPadding;

      return coords.top + contentRect.height > window.innerHeight - viewportPadding;
    };

    const oppositeSide = {
      top: "bottom",
      right: "left",
      bottom: "top",
      left: "right",
    };

    let actualSide = preferredSide;
    let coords = placeForSide(actualSide);

    if (shouldFlip(actualSide, coords)) {
      actualSide = oppositeSide[actualSide] || preferredSide;
      coords = placeForSide(actualSide);
    }

    coords.left = clamp(coords.left, viewportPadding, maxLeft);
    coords.top = clamp(coords.top, viewportPadding, maxTop);

    contentEl.setAttribute("data-side", actualSide);
    contentEl.style.left = `${Math.round(coords.left)}px`;
    contentEl.style.top = `${Math.round(coords.top)}px`;
  };

  const syncState = () => {
    const state = dropdown.getAttribute("data-state") || "closed";
    contentEl.setAttribute("data-state", state);
    const isHidden = portalEl.style.display === "none";

    if (state === "open" && isHidden) {
      cancelFrame();
      portalEl.style.display = "";
      contentEl.setAttribute("data-state", "closed");
      updatePosition();
      void contentEl.offsetWidth;
      frameId = requestAnimationFrame(() => {
        updatePosition();
        contentEl.setAttribute("data-state", "open");
        frameId = null;
      });
    } else if (state === "open") {
      portalEl.style.display = "";
      contentEl.setAttribute("data-state", "open");
      updatePosition();
      syncItemState(dropdown);
    } else {
      cancelFrame();
      portalEl.style.display = "none";
      contentEl.setAttribute("data-state", "closed");
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
    }

    if (slot === "dropdown-menu-radio-item") {
      const group = item.closest('[data-slot="dropdown-menu-radio-group"]');
      if (group instanceof HTMLElement) {
        group.setAttribute("data-value", item.getAttribute("data-value") || "");
        syncRadioGroup(group);
      }
    }

    const keepOpen = item.getAttribute("data-menu-keep-open") === "true";

    if (!keepOpen && closeOnSelect) {
      dropdown.dispatchEvent(
        new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
          bubbles: false,
        }),
      );
      schedule(() => triggerEl.focus());
    }
  };

  const focusItemAt = (items, index) => {
    if (!items.length) return;
    const normalizedIndex = ((index % items.length) + items.length) % items.length;
    items[normalizedIndex]?.focus();
  };

  const onContentClick = (event) => {
    const target = event.target;
    if (!(target instanceof Element)) return;

    const item = target.closest(
      '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
    );

    if (!(item instanceof HTMLElement) || !contentEl.contains(item)) return;
    activateItem(item);
  };

  const onContentKeyDown = (event) => {
    if (dropdown.getAttribute("data-state") !== "open") return;

    const items = getMenuItems(contentEl);
    const focusedItem =
      event.target instanceof Element
        ? event.target.closest(
            '[role="menuitem"], [role="menuitemcheckbox"], [role="menuitemradio"]',
          )
        : null;
    const currentIndex = items.findIndex((item) => item === focusedItem);

    if (event.key === "ArrowDown") {
      event.preventDefault();
      focusItemAt(items, currentIndex >= 0 ? currentIndex + 1 : 0);
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      focusItemAt(items, currentIndex >= 0 ? currentIndex - 1 : items.length - 1);
    }

    if (event.key === "Home") {
      event.preventDefault();
      focusItemAt(items, 0);
    }

    if (event.key === "End") {
      event.preventDefault();
      focusItemAt(items, items.length - 1);
    }

    if (event.key === "Enter" || event.key === " ") {
      if (focusedItem instanceof HTMLElement) {
        event.preventDefault();
        activateItem(focusedItem);
      }
    }

    if (event.key === "Escape") {
      event.preventDefault();
      dropdown.dispatchEvent(
        new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
          bubbles: false,
        }),
      );
      schedule(() => triggerEl.focus());
    }

    if (event.key === "Tab") {
      dropdown.dispatchEvent(
        new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
          bubbles: false,
        }),
      );
    }
  };

  const onDocumentPointerDown = (event) => {
    if (!closeOnOutsideClick) return;
    if (dropdown.getAttribute("data-state") !== "open") return;

    const target = event.target;
    if (!(target instanceof Node)) return;
    if (contentEl.contains(target) || dropdown.contains(target)) return;

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
    dropdown.dispatchEvent(
      new CustomEvent(`dropdown-close:${dropdownMenuId}`, {
        bubbles: false,
      }),
    );
    schedule(() => triggerEl.focus());
  };

  const onViewportChange = () => {
    if (dropdown.getAttribute("data-state") === "open") {
      updatePosition();
    }
  };

  syncState();

  const observer = new MutationObserver(syncState);
  observer.observe(dropdown, {
    attributes: true,
    attributeFilter: ["data-state"],
  });

  contentEl.addEventListener("click", onContentClick);
  contentEl.addEventListener("keydown", onContentKeyDown);
  document.addEventListener("pointerdown", onDocumentPointerDown, true);
  document.addEventListener("keydown", onDocumentKeyDown);
  window.addEventListener("resize", onViewportChange);
  window.addEventListener("scroll", onViewportChange, true);

  return () => {
    cancelFrame();
    observer.disconnect();
    contentEl.removeEventListener("click", onContentClick);
    contentEl.removeEventListener("keydown", onContentKeyDown);
    document.removeEventListener("pointerdown", onDocumentPointerDown, true);
    document.removeEventListener("keydown", onDocumentKeyDown);
    window.removeEventListener("resize", onViewportChange);
    window.removeEventListener("scroll", onViewportChange, true);
  };
}, []);