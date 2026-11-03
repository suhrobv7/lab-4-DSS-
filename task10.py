# Task 10 - registry
#
# 10.4 At the edge of the system (where the HTTP string comes in) we really have a string and must
#      turn it into an object once, so one dictionary is fine, and it is the only place that knows
#      the names. Inside Checkout we already have an object, and the if/elif there repeated the
#      same choice again and again and had to be changed for every new method.
# 10.5 One place: one new line in the REGISTRY dictionary (and the BankTransfer class itself, which
#      was already written in Task 1). Checkout and other code did not change.

import pytest
from task01 import PaymentMethod, Card, Click, Payme, Cash, BankTransfer, Checkout


class UnknownPaymentMethodError(ValueError):
    pass


REGISTRY = {
    "card": Card,
    "click": Click,
    "payme": Payme,
    "cash": Cash,
    "bank_transfer": BankTransfer,
}


def create_payment_method(name):
    key = str(name).strip().lower()
    cls = REGISTRY.get(key)
    if cls is None:
        supported = ", ".join(sorted(REGISTRY))
        raise UnknownPaymentMethodError(f"unknown payment method {name!r}, supported: {supported}")
    return cls()


def test_creates_right_class():
    assert isinstance(create_payment_method("click"), Click)
    assert isinstance(create_payment_method("card"), Card)
    assert isinstance(create_payment_method("cash"), Cash)


def test_result_is_payment_method():
    assert isinstance(create_payment_method("payme"), PaymentMethod)


def test_name_is_normalised():
    for raw in [" Payme ", "PAYME", "payme", "pAyMe\n"]:
        assert isinstance(create_payment_method(raw), Payme)


def test_unknown_name():
    with pytest.raises(UnknownPaymentMethodError) as err:
        create_payment_method("bitcoin")
    msg = str(err.value)
    assert "bitcoin" in msg
    for name in ["card", "click", "payme", "cash", "bank_transfer"]:
        assert name in msg


def test_empty_and_none():
    with pytest.raises(UnknownPaymentMethodError):
        create_payment_method("")
    with pytest.raises(UnknownPaymentMethodError):
        create_payment_method(None)


def test_bank_transfer_from_string():
    method = create_payment_method("Bank_Transfer")
    assert Checkout().pay(method, 100_000) == {"charged": 105_000, "refundable": True}
