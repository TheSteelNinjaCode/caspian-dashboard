from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.maddex.Card import Card, CardContent, CardDescription, CardHeader, CardTitle
from src.lib.ppicons import ArrowRight


@component
def RecentSales():
    return html(r"""
<x-card class="lg:col-span-2">
  <x-card-header class="flex flex-row items-start justify-between gap-4">
    <div><x-card-title>Recent Sales</x-card-title><x-card-description>Latest orders from the dummy sales feed</x-card-description></div>
    <x-button size="sm" variant="outline" class="gap-2">View report <x-arrow-right class="size-4" /></x-button>
  </x-card-header>
  <x-card-content>
    <div class="overflow-x-auto">
      <table class="w-full min-w-140 text-sm">
        <thead><tr class="border-b border-border text-left text-muted-foreground"><th class="px-3 py-2 font-medium">Order ID</th><th class="px-3 py-2 font-medium">Customer</th><th class="px-3 py-2 font-medium">Status</th><th class="px-3 py-2 font-medium">Amount</th></tr></thead>
        <tbody>
          <tr class="border-b border-border/60"><td class="px-3 py-3">#10432</td><td class="px-3 py-3">Sophie Martin</td><td class="px-3 py-3"><span class="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">Paid</span></td><td class="px-3 py-3">$1,240.00</td></tr>
          <tr class="border-b border-border/60"><td class="px-3 py-3">#10431</td><td class="px-3 py-3">Jordan Lee</td><td class="px-3 py-3"><span class="rounded-full bg-amber-100 px-2 py-1 text-xs font-medium text-amber-700">Pending</span></td><td class="px-3 py-3">$890.00</td></tr>
          <tr class="border-b border-border/60"><td class="px-3 py-3">#10430</td><td class="px-3 py-3">Amelia Green</td><td class="px-3 py-3"><span class="rounded-full bg-rose-100 px-2 py-1 text-xs font-medium text-rose-700">Refunded</span></td><td class="px-3 py-3">$320.00</td></tr>
          <tr><td class="px-3 py-3">#10429</td><td class="px-3 py-3">Noah Patel</td><td class="px-3 py-3"><span class="rounded-full bg-emerald-100 px-2 py-1 text-xs font-medium text-emerald-700">Paid</span></td><td class="px-3 py-3">$2,140.00</td></tr>
        </tbody>
      </table>
    </div>
  </x-card-content>
</x-card>
""")
