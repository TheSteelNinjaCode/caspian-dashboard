from casp.component_decorator import component, html

from src.lib.maddex.Button import Button
from src.lib.ppicons import Pencil, Trash2


@component
def UsersTable(users: list[dict[str, str]]):
    return html(r"""
<div class="overflow-hidden rounded-2xl border border-border bg-background shadow-xs">
  <div class="overflow-x-auto">
    <table class="w-full min-w-4xl text-left">
      <thead><tr class="border-b border-border"><th class="px-4 py-4 text-base font-semibold">Name</th><th class="px-4 py-4 text-base font-semibold">Email</th><th class="px-4 py-4 text-base font-semibold">Created at</th><th class="px-4 py-4 text-right text-base font-semibold">Options</th></tr></thead>
      <tbody>
        {% for user in users %}
        <tr class="border-b border-border last:border-b-0">
          <td class="px-4 py-4 text-base font-medium">{{ user.name }}</td>
          <td class="px-4 py-4 text-base">{{ user.email }}</td>
          <td class="px-4 py-4 text-base">{{ user.created_at }}</td>
          <td class="px-4 py-3"><div class="flex justify-end"><x-button type="button" variant="outline" size="icon-sm" class="rounded-r-none border-r-0" aria-label="Edit {{ user.name }}"><x-pencil /></x-button><x-button type="button" variant="destructive" size="icon-sm" class="rounded-l-none" aria-label="Delete {{ user.name }}"><x-trash2 /></x-button></div></td>
        </tr>
        {% else %}
        <tr><td colspan="4" class="px-4 py-10 text-center text-base text-muted-foreground">No users found.</td></tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
""",
        users=users,
    )
