from casp.component_decorator import html

from src.components.dashboard.DashboardNavigation import DashboardNavigation
from src.components.dashboard.DashboardTopbar import DashboardTopbar
from src.lib.maddex.Sidebar import SidebarInset, SidebarProvider


def layout(context_data=None):
    request = context_data.get("request") if context_data else None
    current_path = (request.url.path if request else "/dashboard").rstrip("/") or "/dashboard"

    if current_path == "/dashboard":
        current_section = "Overview"
    elif current_path == "/dashboard/users":
        current_section = "Users"
    elif current_path == "/dashboard/profile":
        current_section = "Profile"
    else:
        current_section = current_path.split("/")[-1].replace("-", " ").title()

    props = {
        "current_section": current_section,
        "is_overview": current_path == "/dashboard",
        "is_users": current_path.startswith("/dashboard/users"),
    }

    return (
        html(r"""
<div class="min-h-screen bg-muted/30 text-foreground">
  <x-sidebar-provider default-open="False" style="--sidebar-width-icon: 3.75rem;">
    <x-dashboard-navigation is-overview="{{ layout.is_overview }}"
                            is-users="{{ layout.is_users }}" />
    <x-sidebar-inset>
      <x-dashboard-topbar current-section="{{ layout.current_section }}" />
      <main class="flex-1 overflow-y-auto p-4 md:p-6" pp-reset-scroll="true"><slot /></main>
    </x-sidebar-inset>
  </x-sidebar-provider>
</div>
"""),
        props,
    )
