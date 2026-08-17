from casp.component_decorator import component, html


@component
def ProfileSummary():
    return html(r"""
<section class="rounded-2xl border border-border bg-card p-5 shadow-sm">
  <div class="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
    <div class="flex items-center gap-4">
      <div class="flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-full bg-primary/15 text-lg font-semibold text-primary">
        {% if auth and auth.user and auth.user.image %}
          <img src="{{ auth.user.image }}"
               alt="{{ auth.user.name if auth.user.name else auth.user.email if auth.user.email else 'User' }}"
               class="size-full object-cover" />
        {% else %}
          {{ (auth.user.name if auth and auth.user and auth.user.name else 'Guest')[:2].upper() }}
        {% endif %}
      </div>
      <div class="min-w-0">
        <p class="text-xs uppercase tracking-[0.24em] text-muted-foreground">Signed in user</p>
        <h2 class="truncate text-xl font-semibold">{{ auth.user.name if auth and auth.user and auth.user.name else 'Guest' }}</h2>
        <p class="truncate text-sm text-muted-foreground">{{ auth.user.email if auth and auth.user and auth.user.email else 'No active session' }}</p>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-2">
      <span class="rounded-full border border-border bg-muted px-3 py-1 text-xs font-medium">{{ auth.user.userRole.name if auth and auth.user and auth.user.userRole else 'Not signed in' }}</span>
      <span class="rounded-full border border-border bg-background px-3 py-1 text-xs font-medium text-muted-foreground">{{ 'Verified' if auth and auth.user and auth.user.emailVerified else 'Unavailable' }}</span>
    </div>
  </div>
</section>
""")
