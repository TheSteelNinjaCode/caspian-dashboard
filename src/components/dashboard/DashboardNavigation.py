from casp.component_decorator import component, html

from src.lib.maddex.DropdownMenu import (
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
)
from src.lib.maddex.Sidebar import (
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarSeparator,
)
from src.lib.ppicons import ChartColumn, House, PanelLeft, Settings, ShoppingBag, UserRound, Users


@component
def DashboardNavigation(isOverview: str = "False", isUsers: str = "False"):
    return html(r"""
<x-sidebar collapsible="icon">
  <x-sidebar-header class="h-15.25 justify-center p-3 md:items-center xl:items-start group-data-[collapsible=icon]:items-center">
    <div class="flex w-full items-center gap-2 md:justify-center xl:justify-start group-data-[collapsible=icon]:justify-center">
      <div class="flex size-9 items-center justify-center rounded-md bg-primary/15 text-primary group-data-[collapsible=icon]:size-8">
        <x-panel-left class="size-4" />
      </div>
      <p class="font-semibold group-data-[collapsible=icon]:hidden">Caspian Dashboard</p>
    </div>
  </x-sidebar-header>

  <x-sidebar-separator />

  <x-sidebar-content>
    <x-sidebar-group>
      <x-sidebar-group-label>Navigation</x-sidebar-group-label>
      <x-sidebar-group-content>
        <x-sidebar-menu>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button asChild="True"
                                   isActive="{{ isOverview }}"
                                   tooltip="Overview"
                                   class="group-data-[collapsible=icon]:mx-auto group-data-[collapsible=icon]:w-8 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:[&>span]:hidden">
              <a href="/dashboard"><x-house class="size-4" /><span>Overview</span></a>
            </x-sidebar-menu-button>
          </x-sidebar-menu-item>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button tooltip="Analytics"><x-chart-column class="size-4" /><span>Analytics</span></x-sidebar-menu-button>
          </x-sidebar-menu-item>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button tooltip="Orders"><x-shopping-bag class="size-4" /><span>Orders</span></x-sidebar-menu-button>
          </x-sidebar-menu-item>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button tooltip="Customers"><x-user-round class="size-4" /><span>Customers</span></x-sidebar-menu-button>
          </x-sidebar-menu-item>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button asChild="True"
                                   isActive="{{ isUsers }}"
                                   tooltip="Users">
              <a href="/dashboard/users"><x-users class="size-4" /><span>Users</span></a>
            </x-sidebar-menu-button>
          </x-sidebar-menu-item>
          <x-sidebar-menu-item>
            <x-sidebar-menu-button tooltip="Settings"><x-settings class="size-4" /><span>Settings</span></x-sidebar-menu-button>
          </x-sidebar-menu-item>
        </x-sidebar-menu>
      </x-sidebar-group-content>
    </x-sidebar-group>
  </x-sidebar-content>

  <x-sidebar-separator />

  <x-sidebar-footer>
    <x-dropdown-menu class="block w-full">
      <x-dropdown-menu-trigger class="h-auto w-full justify-start gap-3 overflow-hidden border border-input bg-background px-3 py-2 shadow-xs hover:bg-accent group-data-[collapsible=icon]:size-8 group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:gap-0 group-data-[collapsible=icon]:border-0 group-data-[collapsible=icon]:bg-transparent group-data-[collapsible=icon]:p-0 group-data-[collapsible=icon]:shadow-none group-data-[collapsible=icon]:hover:bg-transparent">
        <div class="flex size-8 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-xs font-semibold text-primary group-data-[collapsible=icon]:size-8">
          {% if auth and auth.user and auth.user.image %}
          <img src="{{ auth.user.image }}"
               alt="{{ auth.user.name if auth.user.name else auth.user.email if auth.user.email else 'User' }}"
               class="size-full object-cover" />
          {% else %}
          {{ (auth.user.name if auth and auth.user and auth.user.name else 'Guest')[:1].upper() }}
          {% endif %}
        </div>
        <div class="min-w-0 text-left group-data-[collapsible=icon]:hidden">
          <p class="truncate text-sm font-medium">{{ auth.user.name if auth and auth.user and auth.user.name else "Guest" }}</p>
          <p class="truncate text-xs text-muted-foreground">{{ auth.user.userRole.name if auth and auth.user and auth.user.userRole else "Not signed in" }}</p>
        </div>
      </x-dropdown-menu-trigger>
      <x-dropdown-menu-content align="end" class="w-56">
        <x-dropdown-menu-label>
          <p class="truncate text-sm font-medium">{{ auth.user.name if auth and auth.user and auth.user.name else "Guest" }}</p>
          <p class="truncate text-xs text-muted-foreground">{{ auth.user.email if auth and auth.user and auth.user.email else "No active session" }}</p>
        </x-dropdown-menu-label>
        <x-dropdown-menu-separator />
        <x-dropdown-menu-item onclick="pp.redirect('/dashboard/profile')">Profile</x-dropdown-menu-item>
        <x-dropdown-menu-item onclick="pp.rpc('signout')">Sign out</x-dropdown-menu-item>
      </x-dropdown-menu-content>
    </x-dropdown-menu>
  </x-sidebar-footer>
</x-sidebar>
""",
        isOverview=isOverview,
        isUsers=isUsers,
    )
