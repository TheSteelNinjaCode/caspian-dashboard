from casp.component_decorator import component, html
from markupsafe import Markup


def _as_markup(value) -> Markup:
    if value is None:
        return Markup("")
    if isinstance(value, Markup):
        return value

    return Markup(str(value))


@component
def Portal(
    children="",
    content_attributes="",
    portal_attributes="",
    overlay="",
    close="",
    script="",
):
    # html
    return html(r"""
<div style="display: contents">
  <div pp-ref="portalRef" {{ portal_attributes }}>
    {{ overlay }}
    <div {{ content_attributes }} pp-ref="contentBoxRef">{{ children }} {{ close }}</div>
  </div>

  <script>
    const portalRef = pp.ref();
    const contentBoxRef = pp.ref();
    const portal = pp.portal(portalRef);

    {{ script }}
  </script>
</div>
""",
        children=_as_markup(children),
        content_attributes=_as_markup(content_attributes),
        portal_attributes=_as_markup(portal_attributes),
        overlay=_as_markup(overlay),
        close=_as_markup(close),
        script=_as_markup(script),
    )
