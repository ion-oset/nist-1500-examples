"""Document index."""


from collections.abc import Mapping

from utility import walk_document


class IndexNode:

    """Entry in the index describing an item and its container.

    Allows tracking the parent and key of an item so it can be removed.
    """

    # Note: The field that stores the "current" item is `value`, not `parent`.

    def __init__(self, parent, key, value):
        """Create an index node.

        Parameters:
            parent: The container that holds the item with the value.
                It has one of the following types:
                - A mapping (a class defined in the JSON Schema)
                - A sequence (a list)
            key: The key used to get the value from the parent.
                If the parent is a mapping the key is the field name.
                If the parent is a sequence the key is a numeric index.
            value: The item being examined for reachability.
                Can be of any type.
        """
        self._parent = parent
        self._key = key
        self._value = value


    def __str__(self):
        """String form of the item.

        Note: This is not JSON.
        """
        return str(self._value)


    # Access to properties is read-only.

    @property
    def parent(self):
        """Item containing the value."""
        return self._parent


    @property
    def key(self):
        """Key (field name or index) used to access the value from the parent."""
        return self._key


    @property
    def value(self):
        """Item being examined for reachability."""
        return self._value


class Index:

    """Indexes of all elements by their '@id' and '@type'.

    Provides a limited DOM-like interface.

    Note that only elements (mappings) are indexed: Lists and scalars have no
    '@id' or '@type'.
    """

    def __init__(self, document, namespace):
        # Document to index
        self._document = document
        # Namespace prefix
        self._namespace = namespace
        # Index of elements by '@id'
        self._by_id = {}
        # Index of elements by '@type'
        self._by_type = {}
        self._build_indexes()


    def by_id(self, id, strict = False):
        """Return element whose '@id' is 'id'.

        Preserves document order.
        """
        id_ = id
        item = self._by_id.get(id_, None)
        if not item and strict:
            raise KeyError(f"No item in index with '@id': {id_}")
        return item


    def by_type(self, type, strict = False, with_namespace = True):
        """Yield all elements whose '@type' is 'type'.

        Preserves document order.
        """

        type_ = type
        if with_namespace and "." not in type_:
            type_ = f"{self._namespace}.{type_}"
        items = self._by_type.get(type_, [])
        if not items and strict:
            raise KeyError(f"No items in index with '@type': {type_}")
        for item in items:
            yield item


    def _build_indexes(self):
        """Build the ID and type indexes."""
        for item, key, value in walk_document(self._document):
            if isinstance(value, Mapping):
                node = IndexNode(item, key, value)
                if "@id" in value:
                    self._by_id[value["@id"]] = node
                if "@type" in value:
                    self._by_type.setdefault(value["@type"], []).append(node)
