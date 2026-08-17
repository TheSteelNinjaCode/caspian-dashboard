from casp.component_decorator import html

from src.components.dashboard.DashboardNavigation import DashboardNavigation
from src.components.dashboard.DashboardTopbar import DashboardTopbar
from src.lib.maddex.Sidebar import SidebarInset, SidebarProvider


def layout(context_data):
    request = context_data.get("request") if context_data else None
    current_path = request.url.path if request else "/dashboard"

    if current_path == "/dashboard":
        current_section = "Overview"
    else:
        current_section = current_path.rstrip("/").split("/")[-1].replace("-", " ").title()

        return (
            html(r"""
<div class="min-h-screen bg-muted/30 text-foreground">
    <x-sidebar-provider default-open="False" style="--sidebar-width-icon: 3.75rem;">
        <x-dashboard-navigation is-overview="{{ 'True' if layout.is_overview else 'False' }}"
                                                        is-users="{{ 'True' if layout.is_users else 'False' }}" />
        <x-sidebar-inset>
            <x-dashboard-topbar current-section="{{ layout.current_section }}" />
            <main class="flex-1 overflow-y-auto p-4 md:p-6" pp-reset-scroll="true"><slot /></main>
        </x-sidebar-inset>
    </x-sidebar-provider>
</div>
"""),
            {
                "current_section": current_section,
                "is_overview": current_path == "/dashboard",
                "is_users": current_path.startswith("/dashboard/users"),
            },
        )
