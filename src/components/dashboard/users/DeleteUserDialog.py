from casp.component_decorator import component, html
from casp.html_attrs import get_attributes

from src.lib.maddex.AlertDialog import (
    AlertDialogCancel,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
)
from src.lib.maddex.Button import Button


@component
def DeleteUserDialog(
    selectedItem: str | None = None,
    isDeleting: str | None = None,
    error: str | None = None,
    onConfirm: str | None = None,
    **props,
):
    attributes = get_attributes(
        {
            "selectedItem": selectedItem,
            "isDeleting": isDeleting,
            "error": error,
            "onConfirm": onConfirm,
        },
        props,
    )

    return html(r"""
<div {{ attributes }}>
  <x-alert-dialog-header>
    <x-alert-dialog-title>Delete {selectedItem?.name ?? "this user"}?</x-alert-dialog-title>
    <x-alert-dialog-description>
      This permanently deletes the account for {selectedItem?.email ?? "the selected user"}. This action cannot be undone.
    </x-alert-dialog-description>
  </x-alert-dialog-header>

  <p class="text-sm text-destructive" role="alert" hidden="{!error}">{error}</p>

  <x-alert-dialog-footer>
    <x-alert-dialog-cancel disabled="{isDeleting}">Cancel</x-alert-dialog-cancel>
    <x-button type="button" variant="destructive" disabled="{isDeleting}" onclick="confirmDelete()">
      {isDeleting ? "Deleting..." : "Delete user"}
    </x-button>
  </x-alert-dialog-footer>

  <script>
    const selectedItem = pp.props.selectedItem ?? null;
    const isDeleting = !!pp.props.isDeleting;
    const error = pp.props.error ?? "";
    const onConfirm = pp.props.onConfirm;

    function confirmDelete() {
      if (!isDeleting && typeof onConfirm === "function") {
        onConfirm();
      }
    }
  </script>
</div>
""",
        attributes=attributes,
    )
