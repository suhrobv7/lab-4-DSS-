# E5 - events
#
# E5.4 from_dict is a @classmethod because it gets the class as cls and builds cls(...). If a subclass
#      calls it (for example PromoOrderPlaced.from_dict(data)) cls is that subclass and we get an object
#      of the subclass, not of the parent. A @staticmethod does not know the class, so I would have to
#      write OrderPlaced(...) inside and every subclass would give a wrong type.

import json
import logging
from dataclasses import dataclass, fields, asdict
from typing import Optional
import pytest

log = logging.getLogger("events")


class Event:
    registry = {}
    version = 1

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        Event.registry[cls.__name__] = cls

    def to_dict(self):
        data = asdict(self)
        data["type"] = type(self).__name__
        data["version"] = self.version
        return data

    @classmethod
    def from_dict(cls, data):
        # take only the fields this class knows, other keys are ignored
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class OrderPlaced(Event):
    order_id: int
    total_tiyin: int
    currency: str
    promo_code: Optional[str] = None  # new in version 2
    version = 2


@dataclass
class OrderCancelled(Event):
    order_id: int
    reason: str


def decode(payload):
    try:
        data = json.loads(payload)
    except ValueError:
        log.warning("bad json, skipped")
        return None
    cls = Event.registry.get(data.get("type")) if isinstance(data, dict) else None
    if cls is None:
        log.warning("unknown event type %r, skipped", data.get("type") if isinstance(data, dict) else data)
        return None
    return cls.from_dict(data)


# what the old consumer had before the deploy (it does not know promo_code)
@dataclass
class OldOrderPlaced:
    order_id: int
    total_tiyin: int
    currency: str

    @classmethod
    def from_dict(cls, data):
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in known})


def test_to_dict_has_type_and_version():
    e = OrderPlaced(1, 500_000, "UZS")
    d = e.to_dict()
    assert d["type"] == "OrderPlaced"
    assert d["version"] == 2
    cancelled = OrderCancelled(7, "changed my mind").to_dict()
    assert cancelled == {"order_id": 7, "reason": "changed my mind", "type": "OrderCancelled", "version": 1}


def test_round_trip():
    e = OrderPlaced(1, 500_000, "UZS", promo_code="NEWYEAR")
    again = decode(json.dumps(e.to_dict()))
    assert again == e


def test_decode_picks_right_class():
    c = decode(json.dumps(OrderCancelled(3, "late").to_dict()))
    assert isinstance(c, OrderCancelled)
    assert c.reason == "late"


def test_unknown_type_is_skipped():
    assert decode(json.dumps({"type": "OrderTeleported", "version": 1, "order_id": 5})) is None
    assert decode('{"order_id": 5}') is None
    assert decode("not json at all") is None


def test_consumer_goes_on_after_unknown_event():
    messages = [
        json.dumps({"type": "Strange", "version": 1}),
        json.dumps(OrderCancelled(9, "x").to_dict()),
    ]
    got = [decode(m) for m in messages]
    assert got[0] is None
    assert got[1].order_id == 9


def test_old_code_reads_version_2():
    v2 = json.dumps(OrderPlaced(1, 500_000, "UZS", promo_code="NEWYEAR").to_dict())
    old = OldOrderPlaced.from_dict(json.loads(v2))
    assert old == OldOrderPlaced(1, 500_000, "UZS")


def test_new_code_reads_version_1():
    v1 = json.dumps({"type": "OrderPlaced", "version": 1, "order_id": 2, "total_tiyin": 1000, "currency": "USD"})
    e = decode(v1)
    assert e == OrderPlaced(2, 1000, "USD", promo_code=None)


def test_classmethod_gives_subclass():
    @dataclass
    class PromoOrderPlaced(OrderPlaced):
        pass

    e = PromoOrderPlaced.from_dict({"order_id": 1, "total_tiyin": 5, "currency": "UZS"})
    assert type(e) is PromoOrderPlaced
