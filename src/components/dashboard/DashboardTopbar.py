from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.maddex.Sidebar import SidebarTrigger
from src.lib.ppicons import Calendar, ChevronRight, Search


@component
def DashboardTopbar(currentSection: str = "Overview"):
    return html(r"""
<header class="sticky top-0 z-20 border-b border-border bg-background/90 px-4 py-3 backdrop-blur md:px-6">
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
    <div class="flex items-center gap-2">
      <label class="relative hidden sm:block">
        <span class="sr-only">Search dashboard</span>
        <x-search class="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <input type="search"
               placeholder="Search..."
               class="h-9 w-56 rounded-md border border-input bg-background pl-9 pr-3 text-sm outline-none transition focus:border-primary" />
      </label>
      <x-button variant="outline" size="sm" class="gap-2">
        <x-calendar class="size-4" />
        Jun 2026
      </x-button>
    </div>
  </div>
</header>
""",
        current_section=currentSection,
    )
