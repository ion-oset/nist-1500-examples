"""Utilities."""

from collections.abc import Sequence, Mapping


def walk_document(item):
    """Walk all objects in a document, depth first.

    Note: JSON objects are Python dictionaries.

    Parameters:
        item: A mapping to walk the fields of.

    Yields:
        Every object in the walk.
    """
    yield item
    if isinstance(item, Mapping):
        for value in item.values():
            yield from walk_document(value)
    elif isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
        for value in item:
            yield from walk_document(value)
