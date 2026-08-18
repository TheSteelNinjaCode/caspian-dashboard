from casp.component_decorator import component, html

from src.components.dashboard.users.CreateUpdateDialog import CreateUpdateDialog
from src.components.dashboard.users.DeleteUserDialog import DeleteUserDialog
from src.lib.maddex.AlertDialog import AlertDialog, AlertDialogContent
from src.lib.maddex.Button import Button
from src.lib.maddex.Dialog import Dialog, DialogContent
from src.lib.ppicons import Pencil, Trash2


@component
def UsersTable(users: list[dict[str, str]]):
    return html(r"""
<div>
  <div class="overflow-hidden rounded-2xl border border-border bg-background shadow-xs">
    <div class="overflow-x-auto">
      <table class="w-full min-w-4xl text-left">
        <thead><tr class="border-b border-border"><th class="px-4 py-4 text-base font-semibold">Name</th><th class="px-4 py-4 text-base font-semibold">Email</th><th class="px-4 py-4 text-base font-semibold">Created at</th><th class="px-4 py-4 text-right text-base font-semibold">Options</th></tr></thead>
        <tbody>
          <template pp-for="user in visibleUsers">
            <tr key="{user.id}" class="border-b border-border last:border-b-0">
              <td class="px-4 py-4 text-base font-medium">{user.name}</td>
              <td class="px-4 py-4 text-base">{user.email}</td>
              <td class="px-4 py-4 text-base">{user.created_at}</td>
              <td class="px-4 py-3"><div class="flex justify-end"><x-button type="button" variant="outline" size="icon-sm" class="rounded-r-none border-r-0" aria-label="{`Edit ${user.name}`}" onclick="openEditDialog(user)"><x-pencil /></x-button><x-button type="button" variant="destructive" size="icon-sm" class="rounded-l-none" aria-label="{`Delete ${user.name}`}" onclick="openDeleteDialog(user)"><x-trash2 /></x-button></div></td>
            </tr>
          </template>
          <tr hidden="{visibleUsers.length !== 0}"><td colspan="4" class="px-4 py-10 text-center text-base text-muted-foreground">No users found.</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <x-dialog open="{editDialogOpen}" on-open-change="{handleEditDialogOpenChange}" reset-on-open="true">
    <x-dialog-content class="sm:max-w-lg">
      <x-create-update-dialog selected-item="{selectedUser}" on-success="{handleEditSuccess}" />
    </x-dialog-content>
  </x-dialog>

  <x-alert-dialog open="{deleteDialogOpen}" on-open-change="{handleDeleteDialogOpenChange}" close-on-overlay-click="false">
    <x-alert-dialog-content>
      <x-delete-user-dialog selected-item="{selectedUser}" is-deleting="{isDeleting}" error="{deleteError}" on-confirm="{confirmDelete}" />
    </x-alert-dialog-content>
  </x-alert-dialog>
</div>
""")
