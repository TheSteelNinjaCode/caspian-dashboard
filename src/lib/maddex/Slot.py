import re
from casp.component_decorator import component
from casp.html_attrs import merge_classes, get_attributes

TAG_REGEX = re.compile(r'<([a-zA-Z][a-zA-Z0-9:-]*)([^>]*?)(/?)>')
ATTR_REGEX = re.compile(
    r'([a-zA-Z_][\w\-]*)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')
BOOL_ATTR_REGEX = re.compile(r'\s([a-zA-Z_][\w\-]*)(?=\s|/?>|$)(?!=)')


@component
def Slot(children="", asChild=False, **props):
    """
    Renders children directly, merging props and classes onto the first child element.
    Uses Regex to avoid BeautifulSoup lowercasing Component tags (preserves <Button> as <Button>).
    """

    slot_class = props.pop("class", "")

    if not asChild:
        merged_props = {**props, "class": slot_class}
        attributes = get_attributes(merged_props)
        return f'<div {attributes}>{children}</div>'

    if not children or not children.strip():
        return ""

    match = TAG_REGEX.search(children)
    if not match:
        return children

    tag_name = match.group(1)
    attrs_str = match.group(2)
    is_self_closing = match.group(3)

    existing_props = {}

    for attr_match in ATTR_REGEX.finditer(attrs_str):
        name = attr_match.group(1)
        val = attr_match.group(2) or attr_match.group(
            3) or attr_match.group(4) or ""
        existing_props[name] = val

    for bool_match in BOOL_ATTR_REGEX.finditer(attrs_str):
        name = bool_match.group(1)
        if name not in existing_props:
            existing_props[name] = True

    existing_class = existing_props.get("class", "")
    final_class = merge_classes(slot_class, existing_class)

    if final_class:
        existing_props["class"] = final_class

    for key, value in props.items():
        if key in ['children', 'asChild']:
            continue
        if value is True:
            existing_props[key] = "true"
        elif value is False or value is None:
            continue
        else:
            existing_props[key] = str(value)

    new_attrs = get_attributes(existing_props)

    slash = " /" if is_self_closing.strip() == "/" else ""

    new_tag = f"<{tag_name} {new_attrs}{slash}>"

    final_html = children[:match.start()] + new_tag + children[match.end():]

    return final_html
