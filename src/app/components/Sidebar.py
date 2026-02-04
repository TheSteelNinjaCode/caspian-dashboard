from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component, render_html
from src.lib.ppicons.House import House
from src.lib.ppicons.ChartBar import ChartBar
from src.lib.ppicons.Users import Users


def _icon_svg(Icon, class_name: str = "size-4.5"):
    return Icon(class_name=class_name)


def _sidebar_items():
    sidebar_items = [
        {"name": "Dashboard", "href": "/dashboard", "icon": House},
        {"name": "Analytics", "href": "/dashboard/analytics", "icon": ChartBar},
        {"name": "Customers", "href": "/dashboard/customers", "icon": Users},
    ]

    def to_json(item):
        out = {
            "name": item["name"],
            "href": item["href"],
            "icon": _icon_svg(item["icon"]),
        }

        return out
    return [to_json(item) for item in sidebar_items]


@component
def Sidebar():
    sidebar_items = _sidebar_items()
    return render_html(__file__, sidebar_items=sidebar_items)
