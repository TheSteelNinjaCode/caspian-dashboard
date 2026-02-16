from casp.component_decorator import component, render_html
from src.lib.ppicons.House import House
from src.lib.ppicons.Users import Users
from src.lib.ppicons.Settings import Settings


def _icon_svg(Icon):
    return Icon()


def _sidebar_sections():
    sections = [
        {
            "title": "Overview",
            "items": [
                {"name": "Dashboard", "href": "/dashboard", "icon": House},
                {"name": "Users", "href": "/dashboard/users", "icon": Users},
            ],
        },
        {
            "title": "Settings",
            "items": [
                {"name": "Settings", "href": "/dashboard/settings", "icon": Settings},
            ],
        },
    ]

    def normalize_badge(b):
        if not b:
            return None
        label = b.get("label", "")
        tone = b.get("tone", "muted")
        if tone not in ("ok", "warn", "muted"):
            tone = "muted"
        return {"label": label, "tone": tone}

    def normalize_item(item):
        out = {"name": item["name"], "href": item.get("href", "#")}

        if item.get("icon"):
            out["icon"] = _icon_svg(item["icon"])

        badge = normalize_badge(item.get("badge"))
        if badge:
            out["badge"] = badge

        children = item.get("children") or []
        if children:
            out["children"] = [normalize_item(c) for c in children]

        return out

    return [
        {"title": s["title"], "items": [
            normalize_item(i) for i in s.get("items", [])]}
        for s in sections
    ]


@component
def Sidebar():
    sidebar_sections = _sidebar_sections()
    return render_html(__file__, sidebar_sections=sidebar_sections)
