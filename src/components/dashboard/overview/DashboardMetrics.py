from casp.component_decorator import component, html

from src.lib.maddex.Card import Card, CardContent, CardDescription, CardHeader, CardTitle


@component
def DashboardMetrics():
    return html(r"""
<section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
  <x-card>
    <x-card-header class="pb-2"><x-card-description>Revenue</x-card-description><x-card-title>$128,400</x-card-title></x-card-header>
    <x-card-content class="flex items-center justify-between text-sm"><span class="text-emerald-600">+12.4%</span><span class="text-muted-foreground">vs last month</span></x-card-content>
  </x-card>
  <x-card>
    <x-card-header class="pb-2"><x-card-description>New Customers</x-card-description><x-card-title>2,184</x-card-title></x-card-header>
    <x-card-content class="flex items-center justify-between text-sm"><span class="text-emerald-600">+8.1%</span><span class="text-muted-foreground">active this month</span></x-card-content>
  </x-card>
  <x-card>
    <x-card-header class="pb-2"><x-card-description>Open Orders</x-card-description><x-card-title>352</x-card-title></x-card-header>
    <x-card-content class="flex items-center justify-between text-sm"><span class="text-amber-600">14 delayed</span><span class="text-muted-foreground">watch list</span></x-card-content>
  </x-card>
  <x-card>
    <x-card-header class="pb-2"><x-card-description>Conversion Rate</x-card-description><x-card-title>4.6%</x-card-title></x-card-header>
    <x-card-content class="flex items-center justify-between text-sm"><span class="text-emerald-600">+0.7%</span><span class="text-muted-foreground">7-day average</span></x-card-content>
  </x-card>
</section>
""")
