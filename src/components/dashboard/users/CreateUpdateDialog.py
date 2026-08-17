from casp.component_decorator import component, html

from src.lib.maddex.Dialog import DialogClose, DialogDescription, DialogFooter, DialogHeader, DialogTitle
from src.lib.maddex.Input import Input


@component
def CreateUpdateDialog(mode: str = "user", **props):
        dialog_mode = (mode or "user").lower()
        is_user_mode = dialog_mode == "user"
        action_label = "Create user" if is_user_mode else "Save changes"

        return html(r"""
<div class="space-y-6">
    <x-dialog-header class="space-y-2">
        <x-dialog-title>{{ title }}</x-dialog-title>
        <x-dialog-description>{{ description }}</x-dialog-description>
    </x-dialog-header>

    <div class="space-y-4">
        <div class="space-y-2">
            <label for="user-name" class="text-sm font-medium text-foreground">Name</label>
            <x-input id="user-name" name="name" type="text" placeholder="Jane Doe" class="w-full" />
        </div>

        <div class="space-y-2">
            <label for="user-email" class="text-sm font-medium text-foreground">Email</label>
            <x-input id="user-email" name="email" type="email" placeholder="jane.doe@example.com" class="w-full" />
        </div>

        <div class="space-y-2">
            <label for="user-password" class="text-sm font-medium text-foreground">Password</label>
            <x-input id="user-password" name="password" type="password" placeholder="••••••••" class="w-full" />
        </div>
    </div>

    <x-dialog-footer class="mt-2">
        <x-dialog-close as-child>
            <x-button type="button" variant="outline">Cancel</x-button>
        </x-dialog-close>
        <x-dialog-close as-child>
            <x-button type="button">{{ action_label }}</x-button>
        </x-dialog-close>
    </x-dialog-footer>
</div>
""",
                title="Create user" if is_user_mode else "Update user",
                description="Add a new account and send the user a secure profile invitation." if is_user_mode else "Update the selected account details.",
                action_label=action_label,
        )
