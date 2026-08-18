from casp.component_decorator import component, html
from casp.html_attrs import get_attributes

from src.lib.maddex.Button import Button
from src.lib.maddex.Dialog import DialogDescription, DialogFooter, DialogHeader, DialogTitle
from src.lib.maddex.Input import Input


@component
def CreateUpdateDialog(selectedItem: str | None = None, onSuccess: str | None = None, **props):
    attributes = get_attributes({"selectedItem": selectedItem, "onSuccess": onSuccess}, props)

    return html(r"""
<div {{ attributes }} class="space-y-6">
    <x-dialog-header class="space-y-2">
        <x-dialog-title>{isEditing ? "Update user" : "Create user"}</x-dialog-title>
        <x-dialog-description>{isEditing ? "Update the selected account details." : "Add a new account and send the user a secure profile invitation."}</x-dialog-description>
    </x-dialog-header>

    <form onsubmit="handleSubmit(event)">
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

            <p class="text-sm text-destructive" role="alert" hidden="{!error}">{error}</p>
        </div>

        <x-dialog-footer class="mt-2">
            <x-button type="button" variant="outline" disabled="{isSaving}" onclick="closeDialog()">Cancel</x-button>
            <x-button type="submit" disabled="{isSaving}">{isSaving ? "Saving..." : isEditing ? "Save changes" : "Create user"}</x-button>
        </x-dialog-footer>
    </form>

    <script>
        const selectedItem = pp.props.selectedItem ?? null;
        const onSuccess = pp.props.onSuccess;
        const isEditing = !!selectedItem?.id;
        const [name, setName] = pp.state(selectedItem?.name ?? "");
        const [email, setEmail] = pp.state(selectedItem?.email ?? "");
        const [password, setPassword] = pp.state("");
        const [isSaving, setIsSaving] = pp.state(false);
        const [error, setError] = pp.state("");

        pp.effect(() => {
            setName(selectedItem?.name ?? "");
            setEmail(selectedItem?.email ?? "");
            setPassword("");
            setError("");
        }, [selectedItem]);

        function closeDialog() {
            if (isSaving) return;
            if (typeof onSuccess === "function") onSuccess(null);
        }

        async function handleSubmit(event) {
            event.preventDefault();
            if (isSaving) return;

            setIsSaving(true);
            setError("");
            try {
                const result = await pp.rpc("save_user", {
                    name,
                    email,
                    password,
                    user_id: selectedItem?.id ?? "",
                });

                if (!result?.success) {
                    throw new Error(result?.message || "Unable to save this user.");
                }

                if (typeof onSuccess === "function") onSuccess(result.user);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Unable to save this user.");
            } finally {
                setIsSaving(false);
            }
        }
    </script>
</div>
""",
        attributes=attributes,
    )

