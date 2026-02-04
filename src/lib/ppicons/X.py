from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def X(**props):
    incoming_class = props.get("class", "")
    final_class = merge_classes("", incoming_class)
    attributes = get_attributes({
        "class": final_class
    }, props)

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {attributes}><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>'
