from casp.component_decorator import component, html

from src.lib.ppicons import ChevronLeft, ChevronRight


@component
def UsersPagination():
    return html(r"""
<footer class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
  <p class="text-base text-muted-foreground">Page {userPage.pagination.currentPage} of {userPage.pagination.totalPages}</p>
  <div class="flex items-center justify-end gap-3">
    <a href="{userPage.pagination.previousHref}"
       hidden="{!userPage.pagination.hasPrevious}"
       class="inline-flex h-9 items-center gap-2 rounded-xl border border-border bg-background px-4 text-sm font-medium shadow-xs hover:bg-accent"><x-chevron-left class="size-4" />Previous</a>
    <span hidden="{userPage.pagination.hasPrevious}"
          class="inline-flex h-9 cursor-not-allowed items-center gap-2 rounded-xl border border-border px-4 text-sm font-medium text-muted-foreground/50"
          aria-disabled="true"><x-chevron-left class="size-4" />Previous</span>
    <a href="{userPage.pagination.nextHref}"
       hidden="{!userPage.pagination.hasNext}"
       class="inline-flex h-9 items-center gap-2 rounded-xl border border-border bg-background px-4 text-sm font-semibold shadow-xs hover:bg-accent">Next<x-chevron-right class="size-4" /></a>
    <span hidden="{userPage.pagination.hasNext}"
          class="inline-flex h-9 cursor-not-allowed items-center gap-2 rounded-xl border border-border px-4 text-sm font-semibold text-muted-foreground/50"
          aria-disabled="true">Next<x-chevron-right class="size-4" /></span>
  </div>
</footer>
""")
