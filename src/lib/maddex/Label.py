from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Label(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "flex items-center gap-2 text-sm leading-none font-medium select-none group-data-[disabled=true]:pointer-events-none group-data-[disabled=true]:opacity-50 peer-disabled:cursor-not-allowed peer-disabled:opacity-50", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "label",
        "class": final_class
    }, props)

    return f"<label {attributes}>{children}</label>"
