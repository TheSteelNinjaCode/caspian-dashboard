from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.maddex.Input import Input
from src.lib.ppicons import Plus, Search


@component
def UsersToolbar(search_term: str):
    return html(r"""
<header class="space-y-4">
  <h1 class="text-3xl font-semibold tracking-tight">Users</h1>
  <div class="flex items-center justify-between gap-4">
    <label class="relative block max-w-md flex-1">
      <span class="sr-only">Search users</span>
      <x-search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <x-input type="search" name="q" value="{{ search_term }}" placeholder="Search users..." class="w-full rounded-xl pl-9" oninput="queueSearch(event.target.value)" />
    </label>
    <x-button type="button" size="icon" class="shrink-0 rounded-xl bg-zinc-900 text-white shadow-sm hover:bg-zinc-800" aria-label="Add user"><x-plus /></x-button>
  </div>
</header>
""",
        search_term=search_term,
    )
