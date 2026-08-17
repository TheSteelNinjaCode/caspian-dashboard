from casp.component_decorator import component, html
from casp.html_attrs import get_attributes

from src.lib.maddex.Button import Button
from src.lib.maddex.Dialog import DialogClose, DialogDescription, DialogFooter, DialogHeader, DialogTitle
from src.lib.maddex.Input import Input


@component
def CreateUpdateDialog(selectedItem: str | None = None, **props):
    attributes = get_attributes({"selectedItem": selectedItem}, props)

    return html(r"""
<div {{ attributes }} class="space-y-6">
    <x-dialog-header class="space-y-2">
        <x-dialog-title>{isEditing ? "Update user" : "Create user"}</x-dialog-title>
        <x-dialog-description>{isEditing ? "Update the selected account details." : "Add a new account and send the user a secure profile invitation."}</x-dialog-description>
    </x-dialog-header>

    <div class="space-y-4">
        <div class="space-y-2">
            <label for="user-name" class="text-sm font-medium text-foreground">Name</label>
            <x-input id="user-name" name="name" type="text" placeholder="Jane Doe" class="w-full" value="{name}" oninput="setName(event.target.value)" />
        </div>

        <div class="space-y-2">
            <label for="user-email" class="text-sm font-medium text-foreground">Email</label>
            <x-input id="user-email" name="email" type="email" placeholder="jane.doe@example.com" class="w-full" value="{email}" oninput="setEmail(event.target.value)" />
        </div>

        <div class="space-y-2">
            <label for="user-password" class="text-sm font-medium text-foreground">{isEditing ? "New password" : "Password"}</label>
            <x-input id="user-password" name="password" type="password" placeholder="{isEditing ? 'Leave blank to keep the current password' : 'Enter a secure password'}" class="w-full" value="{password}" oninput="setPassword(event.target.value)" />
        </div>
    </div>

    <x-dialog-footer class="mt-2">
        <x-dialog-close as-child>
            <x-button type="button" variant="outline">Cancel</x-button>
        </x-dialog-close>
        <x-dialog-close as-child>
            <x-button type="button">{isEditing ? "Save changes" : "Create user"}</x-button>
        </x-dialog-close>
    </x-dialog-footer>

    <script>
        const selectedItem = pp.props.selectedItem ?? null;
        const isEditing = !!selectedItem?.id;
        const [name, setName] = pp.state(selectedItem?.name ?? "");
        const [email, setEmail] = pp.state(selectedItem?.email ?? "");
        const [password, setPassword] = pp.state("");

        pp.effect(() => {
            setName(selectedItem?.name ?? "");
            setEmail(selectedItem?.email ?? "");
            setPassword("");
        }, [selectedItem]);
    </script>
</div>
""",
        attributes=attributes,
    )
