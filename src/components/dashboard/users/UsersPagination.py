from casp.component_decorator import component, html

from src.lib.ppicons import ChevronLeft, ChevronRight


@component
def UsersPagination(
    current_page: int,
    total_pages: int,
    has_previous: bool,
    has_next: bool,
    previous_href: str,
    next_href: str,
):
    return html(r"""
<footer class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
  <p class="text-base text-muted-foreground">Page {{ current_page }} of {{ total_pages }}</p>
  <div class="flex items-center justify-end gap-3">
    {% if has_previous %}<a href="{{ previous_href }}"
   class="inline-flex h-9 items-center gap-2 rounded-xl border border-border bg-background px-4 text-sm font-medium shadow-xs hover:bg-accent"><x-chevron-left class="size-4" />Previous</a>{% else %}<span class="inline-flex h-9 cursor-not-allowed items-center gap-2 rounded-xl border border-border px-4 text-sm font-medium text-muted-foreground/50"
      aria-disabled="true"><x-chevron-left class="size-4" />Previous</span>{% endif %}
    {% if has_next %}<a href="{{ next_href }}"
   class="inline-flex h-9 items-center gap-2 rounded-xl border border-border bg-background px-4 text-sm font-semibold shadow-xs hover:bg-accent">Next<x-chevron-right class="size-4" /></a>{% else %}<span class="inline-flex h-9 cursor-not-allowed items-center gap-2 rounded-xl border border-border px-4 text-sm font-semibold text-muted-foreground/50"
      aria-disabled="true">Next<x-chevron-right class="size-4" /></span>{% endif %}
  </div>
</footer>
""",
        current_page=current_page,
        total_pages=total_pages,
        has_previous=has_previous,
        has_next=has_next,
        previous_href=previous_href,
        next_href=next_href,
    )
