from casp.component_decorator import component, html


@component
def ProfileDetails():
    return html(r"""
<div class="space-y-6">
  <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
    <div class="rounded-xl border border-border bg-background p-4"><p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Display name</p><p class="mt-2 text-sm font-medium">{{ auth.user.name if auth and auth.user and auth.user.name else 'Guest' }}</p></div>
    <div class="rounded-xl border border-border bg-background p-4"><p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Email</p><p class="mt-2 text-sm font-medium">{{ auth.user.email if auth and auth.user and auth.user.email else 'No active session' }}</p></div>
    <div class="rounded-xl border border-border bg-background p-4"><p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Role</p><p class="mt-2 text-sm font-medium">{{ auth.user.userRole.name if auth and auth.user and auth.user.userRole else 'Not signed in' }}</p></div>
    <div class="rounded-xl border border-border bg-background p-4"><p class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Joined</p><p class="mt-2 text-sm font-medium">{{ auth.user.createdAt.strftime('%b %d, %Y') if auth and auth.user and auth.user.createdAt else 'Unavailable' }}</p></div>
  </section>
  <section class="rounded-2xl border border-border bg-card p-5">
    <div class="flex items-center justify-between gap-3 border-b border-border pb-4">
      <div><h3 class="text-base font-semibold">Session summary</h3><p class="text-sm text-muted-foreground">Values sourced from the authenticated user record.</p></div>
      <a href="/dashboard" class="text-sm font-medium text-primary hover:underline">Back to dashboard</a>
    </div>
    <dl class="grid gap-4 pt-4 sm:grid-cols-2">
      <div class="rounded-xl border border-border/70 bg-background p-4"><dt class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Name</dt><dd class="mt-2 text-sm font-medium">{{ auth.user.name if auth and auth.user and auth.user.name else 'Guest' }}</dd></div>
      <div class="rounded-xl border border-border/70 bg-background p-4"><dt class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Email</dt><dd class="mt-2 text-sm font-medium">{{ auth.user.email if auth and auth.user and auth.user.email else 'No active session' }}</dd></div>
      <div class="rounded-xl border border-border/70 bg-background p-4"><dt class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Account role</dt><dd class="mt-2 text-sm font-medium">{{ auth.user.userRole.name if auth and auth.user and auth.user.userRole else 'Not signed in' }}</dd></div>
      <div class="rounded-xl border border-border/70 bg-background p-4"><dt class="text-xs uppercase tracking-[0.2em] text-muted-foreground">Email verification</dt><dd class="mt-2 text-sm font-medium">{{ 'Verified' if auth and auth.user and auth.user.emailVerified else 'Unavailable' }}</dd></div>
    </dl>
  </section>
</div>
""")
