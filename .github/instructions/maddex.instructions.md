---
description: "Use when working with Maddex, Maddex CLI-managed Python UI components, CRUD pages and dialogs, maddex.json manifest metadata, component installation, component updates, or generated component imports."
name: "Maddex AI Context"
applyTo: "maddex.json, .github/instructions/maddex.instructions.md, src/lib/maddex/**, src/utils/maddex-ai-context.ts, src/utils/maddex-manifest.ts, tests/utils/maddex-ai-context.test.ts, tests/utils/maddex-manifest.test.ts"
---

# Maddex Instructions

Keep Maddex-specific AI guidance here instead of in `.github/copilot-instructions.md`.

- Use `maddex.json` under the `manifest` key as the source of truth for installed component inventory, configured paths, and registry metadata.
- Prefer `maddex add ...` or `maddex update` for registry-backed components instead of hand-writing generated Python modules.
- Preserve manual content outside the managed Maddex block because refreshes replace only that managed section.

## First-Party CRUD Pattern

When a user asks AI to build CRUD with Maddex or Caspian, use this composition pattern first unless the host repo already has a stronger local convention.

- Let the page `index.py` and `index.html` own the list shell, search, pagination, lookup data, and dialog state.
- Create one composition component such as `CreateUpdateDialog` for both create and update flows, built with Maddex `Dialog` primitives.
- Drive create versus update from `selectedItem` or `selectedItem.id`, and map that value into local form state when the dialog opens.
- Keep create and update mutations in one `save_*` RPC next to the dialog component, branching on the presence of an `id`.
- After a successful save, update the parent `items` collection in place and close the dialog before falling back to a full refetch.
- Put delete in a dedicated `DeleteDialog` confirmation component built with Maddex `AlertDialog` primitives.
- Keep the delete mutation in a `delete_*` RPC next to that delete component and remove the deleted record from the parent `items` collection after confirmation.
- Pass `openDialog`, `setOpenDialog`, `selectedItem`, `items`, and `setItems` as composition props instead of introducing ad-hoc global state for simple CRUD flows.
- Use Maddex primitives such as `Button`, `Input`, `Dialog`, and `AlertDialog` instead of custom overlay implementations when generating first-party CRUD screens.

<!-- maddex:start -->
# Maddex AI Context

This project uses `maddex` to install reusable Caspian Python UI component modules.

- Read `maddex.json` under the `manifest` key when you need the current installed-component inventory, configured paths, commands, registry metadata, Tailwind file, or icon library.
- Do not duplicate that mutable inventory in agent instructions; `maddex.json` is the source of truth.

## Installing Components

When a requested UI component does not exist yet, install it with `maddex` instead of hand-writing generated component modules.

- Add one component: `npx maddex add <component-name>`.
- Add multiple components: `npx maddex add <component-a> <component-b>`.
- Refresh installed components: `npx maddex update`.

## Discovering Available Components

Use the Maddex catalogue API only when the requested component is not already listed in `maddex.json`.

- `GET https://maddex.tsnc.tech/cli?component=all` returns an array of available component names.
- `GET https://maddex.tsnc.tech/cli?component=<component-name>` returns the requested component payload. Let the CLI process it; do not copy registry response content into app code.

## Importing and Using Components

Use real Python imports in the rendering module to make Maddex component tags available.

- Import the component from its generated `.py` module into the Python page, layout, or component that renders its `<x-*>` tag.
- For package imports that bind a submodule, Caspian resolves the same-named component from that module; one component lives in one Python file.

## Usage Notes

- Use the matching Maddex documentation page for component markup and props when an example is needed.
- Keep application composition and RPC logic in app-owned Python modules; generated Maddex modules are registry-managed and should be refreshed through the CLI.
- This guidance is intentionally stable. Component changes update only `maddex.json`.
<!-- maddex:end -->
