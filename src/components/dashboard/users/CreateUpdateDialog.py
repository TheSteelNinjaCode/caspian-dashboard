from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def CreateUpdateDialog(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "class": final_class
    }, props)

    return f'<div {attributes}>{children}</div>'
