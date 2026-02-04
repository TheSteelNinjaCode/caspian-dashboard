from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component, render_html


@component
def TopMenu():
    return render_html(__file__)
