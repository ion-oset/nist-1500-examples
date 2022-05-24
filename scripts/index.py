"""Document index."""


from collections.abc import Mapping

from utility import walk_document


class Index:

    """Indexes of all elements by their '@id' and '@type'.

    Provides a limited DOM-like interface.
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
        for item in walk_document(self._document):
            if isinstance(item, Mapping):
                if "@id" in item:
                    self._by_id[item["@id"]] = item
                if "@type" in item:
                    self._by_type.setdefault(item["@type"], []).append(item)
