"""Utilities."""

from collections.abc import Sequence, Mapping


def ids_of(items):
    """Get JSON Schema '@id's from a list of elements."""
    return [item["@id"] for item in items]


def walk_document(parent):
    """Walk all objects in a document, depth first.

    Yields the objects and their parent objects, to allow basic mutations at
    each step.
    - Mappings yield key, value pairs.
    - Sequences yield index, value pairs.
    - Scalars yield themselves.

    Parameters:
        parent: The object being walked.

    Yields:
        parent: Parent item of the value
        - For a mapping or sequence: the input 'parent'.
        - For a scalar: None
        key: The key used to access the value.
        - For a mapping: key
        - For a sequence: numeric index
        - For a scalar: None
        value: The value.
        - For a mapping or sequence: 'parent[key]'
        - For a scalar: the 'parent'
    """
    if isinstance(parent, Mapping):
        for name, value in parent.items():
            yield parent, name, value
            yield from walk_document(value)
    elif isinstance(parent, Sequence) and not isinstance(parent, (str, bytes)):
        for index, value in enumerate(parent):
            yield parent, index, value
            yield from walk_document(value)
    else:
        parent, key, value = None, None, parent
        yield parent, key, value
