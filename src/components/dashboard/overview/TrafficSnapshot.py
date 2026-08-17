from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.maddex.Card import Card, CardContent, CardDescription, CardHeader, CardTitle
from src.lib.ppicons import ChevronUp


@component
def TrafficSnapshot():
    return html(r"""
<x-card>
  <x-card-header><x-card-title>Traffic Snapshot</x-card-title><x-card-description>Weekly trend data (placeholder)</x-card-description></x-card-header>
  <x-card-content class="space-y-4">
    <div class="rounded-lg border border-border p-3">
      <p class="text-sm text-muted-foreground">Organic</p><p class="mt-1 text-2xl font-semibold">18.2k</p>
      <p class="mt-1 flex items-center gap-1 text-xs text-emerald-600"><x-chevron-up class="size-3" />+9.5%</p>
    </div>
    <div class="rounded-lg border border-border p-3"><p class="text-sm text-muted-foreground">Paid</p><p class="mt-1 text-2xl font-semibold">6.9k</p><p class="mt-1 text-xs text-muted-foreground">Campaign refresh in 3 days</p></div>
    <x-button class="w-full" variant="secondary">Open Analytics</x-button>
  </x-card-content>
</x-card>
""")
