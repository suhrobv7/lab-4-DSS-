# E1 - headers
#
# E1.1 Output of the original: {'Accept': 'application/json', 'content-type': 'text/plain',
#      'Content-Type': 'application/json', 'X-Request-Id': '42'}. The constructor Headers({...}),
#      update() and setdefault() do not go through my __setitem__, because dict does these things
#      in C code and never calls the overridden method of the child.
# E1.2 This is the fragile base class problem, the child relied on how dict works inside, and dict
#      never promised that. UserDict is written in python and its __init__, update() and
#      setdefault() really call self[key] = value, so my rule works for all of them.
# E1.3 For reading I override __getitem__ and __contains__ (and __delitem__ so that
#      del h["CONTENT-TYPE"] works too). get(), pop() and setdefault() from MutableMapping use these
#      methods, so they follow the rule without extra code.

from collections import UserDict
import pytest


class Headers(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key.lower(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.lower())

    def __delitem__(self, key):
        super().__delitem__(key.lower())

    def __contains__(self, key):
        return isinstance(key, str) and key.lower() in self.data


def test_constructor_lowercases():
    h = Headers({"Accept": "application/json"})
    assert list(h) == ["accept"]


def test_constructor_with_kwargs():
    h = Headers(Accept="a", CONTENT_TYPE="b")
    assert sorted(h) == ["accept", "content_type"]


def test_update_replaces_not_duplicates():
    h = Headers()
    h["Content-Type"] = "text/plain"
    h.update({"Content-Type": "application/json"})
    assert len(h) == 1
    assert h["content-type"] == "application/json"


def test_setdefault():
    h = Headers()
    h.setdefault("X-Request-Id", "42")
    h.setdefault("x-request-id", "43")
    assert dict(h) == {"x-request-id": "42"}


def test_reading_is_case_insensitive():
    h = Headers({"Content-Type": "text/plain"})
    assert h["CONTENT-TYPE"] == "text/plain"
    assert "CONTENT-TYPE" in h
    assert "Accept" not in h
    assert h.get("Content-TYPE") == "text/plain"
    assert h.get("accept") is None


def test_missing_key():
    with pytest.raises(KeyError):
        Headers()["Accept"]


def test_delete_and_pop():
    h = Headers({"Accept": "a", "X-Id": "1"})
    del h["ACCEPT"]
    assert h.pop("X-ID") == "1"
    assert len(h) == 0


def test_only_one_key_per_name():
    h = Headers({"Accept": "a"})
    h["ACCEPT"] = "b"
    h.update(accept="c")
    h.setdefault("Accept", "d")
    assert len(h) == 1
    assert h["accept"] == "c"
