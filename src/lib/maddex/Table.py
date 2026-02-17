from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Table(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "w-full caption-bottom text-sm", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table",
        "class": final_class
    }, props)

    return f"""
<div data-slot="table-container" class="relative w-full overflow-x-auto">
    <table {attributes}>
        {children}
    </table>
</div>"""


@component
def TableHeader(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("[&_tr]:border-b", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-header",
        "class": final_class
    }, props)

    return f"<thead {attributes}>{children}</thead>"


@component
def TableBody(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes("[&_tr:last-child]:border-0", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-body",
        "class": final_class
    }, props)

    return f"<tbody {attributes}>{children}</tbody>"


@component
def TableFooter(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "bg-muted/50 border-t font-medium [&>tr]:last:border-b-0", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-footer",
        "class": final_class
    }, props)

    return f"<tfoot {attributes}>{children}</tfoot>"


@component
def TableRow(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-row",
        "class": final_class
    }, props)

    return f"<tr {attributes}>{children}</tr>"


@component
def TableHead(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "text-foreground h-10 px-2 text-left align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-head",
        "class": final_class
    }, props)

    return f"<th {attributes}>{children}</th>"


@component
def TableCell(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-cell",
        "class": final_class
    }, props)

    return f"<td {attributes}>{children}</td>"


@component
def TableCaption(**props):
    incoming_class = props.pop("class", "")
    final_class = merge_classes(
        "text-muted-foreground mt-4 text-sm", incoming_class)

    children = props.pop("children", "")

    attributes = get_attributes({
        "data-slot": "table-caption",
        "class": final_class
    }, props)

    return f"<caption {attributes}>{children}</caption>"
