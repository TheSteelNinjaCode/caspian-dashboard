---
description: "Use when working with ppicons, PPIcons icon components, Prisma PHP/PHPX icons, Caspian icons, icon installation, icon updates, or icon imports."
name: "PPIcons AI Context"
applyTo: "ppicons.json, src/lib/ppicons/**"
---
<!-- ppicons:start -->
# PPIcons AI Context

This project uses `ppicons` to generate reusable icon components.

- Project type: caspian
- Framework: caspian
- Language mode: py
- Framework config file: caspian.config.json
- Manifest file: ppicons.json
- Components directory: src/lib/ppicons
- Icons directory: src/lib/ppicons
- Installed icon count: 24
- Full installed icon inventory: `ppicons.json`

## Installing Icons

When a requested icon does not exist yet, install it with `ppicons` instead of hand-writing a component.

- Add one icon: `npx ppicons add <icon-name>`
- Add multiple icons: `npx ppicons add <icon-a> <icon-b>`
- Add the full set: `npx ppicons add --all`
- Refresh installed icons: `npx ppicons update`

## Discovering Available Icons

Use the catalog API to find icon names before installing them.

- Fetch all available icons: `GET https://ppicons.tsnc.tech/icons?icon=all`
- Fetch one icon by name: `GET https://ppicons.tsnc.tech/icons?icon=search`
- The single-icon endpoint returns one JSON object.
- The `icon=all` endpoint returns a JSON array of objects with the same shape.

Single icon response example:

```json
{
  "id": 166531,
  "name": "search",
  "componentName": "Search",
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"none\" stroke=\"currentColor\" stroke-width=\"2\" stroke-linecap=\"round\" stroke-linejoin=\"round\" class=\"lucide lucide-search\"><circle cx=\"11\" cy=\"11\" r=\"8\"/><path d=\"m21 21-4.3-4.3\"/></svg>",
  "createdAt": 1774923647142,
  "updatedAt": 1774923647142
}
```

## Using Installed Icons

Use HTML-first `x-` icon tags.

- Use the `tagName` values from `settings/component-map.json` as the icon tag contract.
- Keep PPIcons examples and generated markup aligned with those current `x-` tag values.

For Caspian Python components, routes, and layouts:

```python
from src.lib.ppicons import Search
from casp.component_decorator import component, html

@component
def icon_actions():
    return html(r"""
    <div>
        <x-search />
        <x-search class="size-4" />
    </div>
    """)
```

Import every `x-` icon tag from the Python module that authors it. Caspian has no HTML-sidecar or comment import syntax.

## Notes

- Reuse installed icons from `ppicons.json` before adding new ones.
- Generated icon files follow this pattern: `src/lib/ppicons/<ComponentName>.py`
- The import entry for this project is `src.lib.ppicons`

## Local Import Preference

For generated or updated Python imports, prefer grouped imports when two or more icons come from the same `src.lib.ppicons` package.

- Use a grouped import when multiple icons are imported from `src.lib.ppicons`.
- Use a single import when only one icon is needed.
- Do not treat existing separate single imports as wrong unless the task explicitly includes import cleanup.
- When adding a second or third icon from `src.lib.ppicons` to the same file, prefer collapsing those imports into one grouped statement.

Preferred for multiple icons:

```python
from src.lib.ppicons import ArrowRight, Mail, UserRound
```

Fine for one icon:

```python
from src.lib.ppicons import Mail
```

Example usage in Python component:

```python
from src.lib.ppicons import ArrowRight, Mail, UserRound

def render():
    return """
    <div>
        <x-mail class="size-4" />
        <x-user-round class="size-4" />
        <x-arrow-right class="size-4" />
    </div>
    """
```
<!-- ppicons:end -->
