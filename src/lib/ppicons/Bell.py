from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Bell(**props):
    incoming_class = props.get("class", "")
    final_class = merge_classes("", incoming_class)
    attributes = get_attributes({
        "class": final_class
    }, props)

    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" {attributes}><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>'
