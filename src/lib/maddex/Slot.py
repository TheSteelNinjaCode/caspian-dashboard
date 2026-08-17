from bs4 import BeautifulSoup
from bs4.element import AttributeValueList, Tag
from casp.component_decorator import component, html
from casp.html_attrs import get_attributes, merge_classes


def _apply_props_to_tag(tag: Tag, slot_class: str, props: dict) -> None:
    existing_class = tag.get("class", AttributeValueList())
    if isinstance(existing_class, list):
        existing_class_value = " ".join(str(part) for part in existing_class if part)
    else:
        existing_class_value = str(existing_class or "")

    final_class = merge_classes(slot_class, existing_class_value)
    if final_class:
        tag["class"] = AttributeValueList(final_class.split())
    elif tag.has_attr("class"):
        del tag["class"]

    for key, value in props.items():
        if key in ["children", "asChild", "class"]:
            continue
        if value is True:
            tag.attrs[key] = ""
        elif value is False or value is None:
            tag.attrs.pop(key, None)
        else:
            tag.attrs[key] = str(value)


def _render_fragment(soup: BeautifulSoup) -> str:
    return "".join(str(node) for node in soup.contents)


@component
def Slot(children="", asChild=False, **props):
    """
    Renders children directly, merging props and classes onto the first child element.
    Uses BeautifulSoup to safely parse HTML fragments instead of editing tags with regex.
    """

    slot_class = props.pop("class", "")
    children = str(children or "")

    if not asChild:
        merged_props = {**props, "class": slot_class}
        attributes = get_attributes(merged_props)
        return html(r"""<div {{ attributes }}>{{ children }}</div>""",
            attributes=attributes,
            children=children,
        )

    if not children or not children.strip():
        return ""

    soup = BeautifulSoup(children, "html.parser")
    first_tag = next((node for node in soup.contents if isinstance(node, Tag)), None)
    if first_tag is None:
        return children

    # Children projected through the compiler can be wrapped in template[pp-owner].
    # Apply merged slot attrs to the first rendered child element, not to the owner template.
    if first_tag.name == "template":
        nested_tag = next((node for node in first_tag.contents if isinstance(node, Tag)), None)
        if nested_tag is not None:
            _apply_props_to_tag(nested_tag, slot_class, props)
            return _render_fragment(soup)

    _apply_props_to_tag(first_tag, slot_class, props)
    return _render_fragment(soup)
