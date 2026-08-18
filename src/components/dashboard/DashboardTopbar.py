from casp.component_decorator import component, html

from src.lib.maddex.Sidebar import SidebarTrigger
from src.lib.ppicons import ChevronRight


@component
def DashboardTopbar(currentSection: str = "Overview"):
    return html(r"""
<header class="sticky top-0 z-20 h-12 border-b border-border bg-background/90 px-4 py-2.5 backdrop-blur md:px-6">
  <div class="flex items-center justify-between gap-3">
    <div class="flex items-center gap-3">
      <x-sidebar-trigger />
      <nav class="flex items-center gap-2 text-sm text-muted-foreground"
           aria-label="Breadcrumb">
        <a href="/dashboard" class="hover:text-foreground">Dashboard</a>
        <x-chevron-right class="size-3" />
        <span class="font-medium text-foreground">{{ current_section }}</span>
      </nav>
    </div>
  </div>
</header>
""",
        current_section=currentSection,
    )
