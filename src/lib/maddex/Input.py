from casp.html_attrs import get_attributes, merge_classes
from casp.component_decorator import component


@component
def Input(**props):
    incoming_class = props.pop("class", "")
    base_class = {
        "file:text-foreground placeholder:text-muted-foreground selection:bg-primary selection:text-primary-foreground dark:bg-input/30 border-input flex h-9 w-full min-w-0 rounded-md border px-3 py-1 text-base shadow-xs transition-[color,box-shadow] outline-none file:inline-flex file:h-7 file:border-0 file:bg-transparent file:text-sm file:font-medium disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 md:text-sm focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive",
    }
    final_class = merge_classes(base_class, incoming_class)

    attributes = get_attributes({
        "data-slot": "input",
        "class": final_class
    }, props)

    return f"<input {attributes} />"
