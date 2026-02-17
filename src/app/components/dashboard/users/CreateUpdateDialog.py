from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component, render_html


@component
def CreateUpdateDialog(openDialog: str, setOpenDialog: str):
    print("🚀 ~ CreateUpdateDialog ~ openDialog:", openDialog)
    print("🚀 ~ CreateUpdateDialog ~ setOpenDialog:", setOpenDialog)
    return render_html(__file__, {
        "openDialog": openDialog,
        "setOpenDialog": setOpenDialog,
    })