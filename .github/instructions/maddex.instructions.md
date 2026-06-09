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

This project uses `maddex` to generate reusable Python UI component modules.

- Config file: maddex.json
- Maddex instructions file: .github/instructions/maddex.instructions.md
- Components directory: src/lib/maddex
- Configured Python source path: src/lib/maddex
- Suggested module path: src.lib.maddex
- Tailwind CSS file: src/app/globals.css
- Icon library: ppicons
- Installed component count: 4
- Installed component inventory and project metadata: `maddex.json` (under `manifest`)

## Installing Components

When a requested UI component does not exist yet, install it with `maddex` instead of hand-writing generated component modules.

- Add one component: `npx maddex add <component-name>`
- Add multiple components: `npx maddex add <component-a> <component-b>`
- Add the full catalogue: `npx maddex add --all`
- Refresh installed components: `npx maddex update`

## Discovering Available Components

Use the Maddex catalogue API to find component names before installing them.

- Fetch all available components: `GET https://maddex.tsnc.tech/cli?component=all`
- Fetch one component by name: `GET https://maddex.tsnc.tech/cli?component=Button`
- The `component=all` endpoint returns a JSON array of component names.
- The single-component endpoint may return a `files` array for multi-file components or a legacy `content` string for a single Python module.

Single component response example:

```json
{
  "name": "Button",
  "files": [
    {
      "name": "Button.py",
      "content": "class Button:\n    ...generated Python source..."
    },
    {
      "name": "Button.html",
      "content": "<button>...generated template...</button>"
    }
  ]
}
```

## Importing and Using Components

Use the installed Python module as the source for template `@import` comments, then copy the live docs example for the component you are rendering.

- Adjust the relative `@import` path to match the current file location.
- Maddex docs URLs use kebab-case component names such as `https://maddex.tsnc.tech/docs/button` and `https://maddex.tsnc.tech/docs/alert-dialog`.
- For any installed component, derive the docs page as `https://maddex.tsnc.tech/docs/<component-kebab-name>`.

Button example:

```html
<!-- @import { Button } from ../../../../lib/maddex/Button.py -->

<div class="flex w-full flex-wrap items-center justify-center gap-3">
  <x-button>Default</x-button>
  <x-button variant="secondary">Secondary</x-button>
  <x-button variant="destructive">Destructive</x-button>
  <x-button variant="outline">Outline</x-button>
  <x-button variant="ghost">Ghost</x-button>
  <x-button variant="link">Link</x-button>
</div>
```

## Installed Components

- Button: `src/lib/maddex/Button.py` (docs: `https://maddex.tsnc.tech/docs/button`)
- Portal: `src/lib/maddex/Portal.py` (docs: `https://maddex.tsnc.tech/docs/portal`)
- Slot: `src/lib/maddex/Slot.py` (docs: `https://maddex.tsnc.tech/docs/slot`)
- utils: `src/lib/maddex/utils.py` (docs: `https://maddex.tsnc.tech/docs/utils`)

## Usage Notes

- Generated Python files follow this pattern: `src/lib/maddex/<ComponentName>.py`
- Prefer the configured module path `src.lib.maddex` when the host project exposes that package path for imports.
- Some components may include sidecar template or asset files next to the main Python module.
- Manual content outside this managed block is preserved.
<!-- maddex:end -->
