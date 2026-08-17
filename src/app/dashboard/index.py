from casp.component_decorator import html
from casp.layout import Metadata

from src.components.dashboard.overview.DashboardMetrics import DashboardMetrics
from src.components.dashboard.overview.RecentSales import RecentSales
from src.components.dashboard.overview.TrafficSnapshot import TrafficSnapshot


metadata = Metadata(
    title="Dashboard | Caspian",
    description="Business overview and recent activity.",
)


def page():
    return html(r"""
<div class="flex flex-col gap-6">
  <x-dashboard-metrics />
  <section class="grid gap-4 lg:grid-cols-3">
    <x-recent-sales />
    <x-traffic-snapshot />
  </section>
</div>
""")
