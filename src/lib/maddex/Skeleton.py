from casp.component_decorator import component, html
from casp.html_attrs import get_attributes, merge_classes


@component
def Skeleton(**props) -> str:
    incoming_class = props.pop("class", "")
    final_class = merge_classes("bg-accent animate-pulse rounded-md", incoming_class)

    children = props.pop("children", "")

    attrs = get_attributes(
        {
            "data-slot": "skeleton",
            "class": final_class,
        },
        props,
    )

    return html(r"""<div {{ attrs }}>{{ children }}</div>""", attrs=attrs, children=children)
