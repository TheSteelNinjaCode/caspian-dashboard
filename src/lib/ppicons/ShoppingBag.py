from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def ShoppingBag(**props):
    incoming_class = props.get("class", "")
    final_class = merge_classes("", incoming_class)
    attributes = get_attributes({
        "class": final_class
    }, props)

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {attributes}><path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"></path><path d="M3 6h18"></path><path d="M16 10a4 4 0 0 1-8 0"></path></svg>'