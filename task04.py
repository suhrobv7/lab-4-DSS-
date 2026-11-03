# Task 4 - audit log
#
# 4.1 No. An audit log is not a list, because a list can be changed and the log can not. Methods of
#     list that break the rule: clear(), pop(), sort() (also remove, insert, reverse and log[3] = ...).
# 4.3 One entry is a NamedTuple (a tuple), so it can not be changed after it is created.
# 4.4 It is worse because list has 11 public methods (dir(list) shows them, plus the magic ones like
#     __setitem__ and __delitem__). I would have to block all of them and I would forget one, and
#     a new python version can add another method that is open again. With composition
#     only 4 things are open and nothing else exists.

from typing import NamedTuple
import pytest


class Entry(NamedTuple):
    user: str
    action: str


class AuditLog:
    def __init__(self):
        self._entries = []

    def record(self, user, action):
        self._entries.append(Entry(user, action))

    def __len__(self):
        return len(self._entries)

    def __iter__(self):
        return iter(tuple(self._entries))

    def last(self, n):
        if n <= 0:
            return []
        return self._entries[-n:]


def test_record_and_len():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    log.record("ali", "login")
    assert len(log) == 2


def test_iteration():
    log = AuditLog()
    log.record("admin", "approve_loan#77")
    log.record("ali", "login")
    users = [e.user for e in log]
    assert users == ["admin", "ali"]


def test_last():
    log = AuditLog()
    for i in range(5):
        log.record("u", f"action{i}")
    assert [e.action for e in log.last(2)] == ["action3", "action4"]
    assert log.last(0) == []
    assert len(log.last(100)) == 5


def test_clear_is_impossible():
    log = AuditLog()
    log.record("admin", "x")
    with pytest.raises(AttributeError):
        log.clear()
    assert len(log) == 1


def test_sort_and_pop_are_impossible():
    log = AuditLog()
    log.record("admin", "x")
    with pytest.raises(AttributeError):
        log.sort()
    with pytest.raises(AttributeError):
        log.pop()


def test_item_assignment_is_impossible():
    log = AuditLog()
    log.record("admin", "x")
    with pytest.raises(TypeError):
        log[0] = ("hacker", "y")


def test_entry_can_not_change():
    log = AuditLog()
    log.record("admin", "x")
    entry = log.last(1)[0]
    with pytest.raises(AttributeError):
        entry.action = "something else"


def test_public_methods_of_list():
    public = [name for name in dir(list) if not name.startswith("_")]
    assert len(public) == 11
    print(public)
