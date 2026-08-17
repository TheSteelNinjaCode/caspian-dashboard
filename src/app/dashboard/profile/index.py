from casp.component_decorator import html
from casp.layout import Metadata

from src.components.dashboard.profile.ProfileDetails import ProfileDetails
from src.components.dashboard.profile.ProfileSummary import ProfileSummary


metadata = Metadata(
    title="Profile | Caspian Dashboard",
    description="Review the signed-in account details.",
)


def page():
    return html(r"""
<div class="space-y-6">
  <header class="space-y-2">
    <h1 class="text-2xl font-semibold tracking-tight">Profile</h1>
    <p class="max-w-2xl text-sm text-muted-foreground">Review the account data pulled from your signed-in session.</p>
  </header>
  <x-profile-summary />
  <x-profile-details />
</div>
""")
