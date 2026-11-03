# Task 8 - search
#
# 8.1 A class body is just a block where names are assigned. The second "def search" assigns the
#     name search again, so it replaces the first one and the class keeps only the version with
#     (self, query, filters). Calling search("iphone") then misses the argument filters -> TypeError.
#     Python has no overloading by number of arguments.
# 8.2 I use filters=None as the default. filters={} is a mutable default, it is created once when
#     the function is defined and shared by all calls (the same trap as in Task 1 of Lab 4A). Here we
#     only read it, but someone will write to it later and the bug will be hard to find.
# 8.3 I chose keyword-only dictionary: search("iphone", filters={"brand": "Apple"}). The filters
#     come from an HTTP request as a dict anyway, so I can pass it without any unpacking, and a
#     filter called "query" or "self" can not clash with the real arguments of the function.
#     Keyword arguments (brand="Apple") look nicer but break on such names.
# 8.4 pyflakes on the original code (task08_original.py) says:
#     task08_original.py:10:5: redefinition of unused 'search' from line 6
#     so the linter sees that the first search() is never used, and it is found before the review.

import pytest


class ProductSearch:
    def __init__(self, products):
        self.products = products

    def search(self, query, *, filters=None):
        q = query.lower()
        result = [p for p in self.products if q in p["title"].lower()]
        if filters:
            for key, value in filters.items():
                result = [p for p in result if p.get(key) == value]
        return result


products = [
    {"title": "iPhone 15", "brand": "Apple", "color": "black"},
    {"title": "iPhone 15 Pro", "brand": "Apple", "color": "gray"},
    {"title": "Galaxy S24", "brand": "Samsung", "color": "black"},
    {"title": "Phone case for iPhone", "brand": "Spigen", "color": "black"},
]


def test_without_filters():
    ps = ProductSearch(products)
    res = ps.search("iphone")
    assert [p["title"] for p in res] == ["iPhone 15", "iPhone 15 Pro", "Phone case for iPhone"]


def test_with_filters():
    ps = ProductSearch(products)
    res = ps.search("iphone", filters={"brand": "Apple", "color": "gray"})
    assert [p["title"] for p in res] == ["iPhone 15 Pro"]


def test_empty_filters_same_as_none():
    ps = ProductSearch(products)
    assert ps.search("galaxy", filters={}) == ps.search("galaxy")


def test_nothing_found():
    assert ProductSearch(products).search("nokia") == []


def test_filters_must_be_keyword():
    ps = ProductSearch(products)
    with pytest.raises(TypeError):
        ps.search("iphone", {"brand": "Apple"})


def test_default_is_not_mutable():
    defaults = ProductSearch.search.__kwdefaults__
    assert defaults["filters"] is None
