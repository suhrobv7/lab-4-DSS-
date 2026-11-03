# Task 7 - Money
#
# 7.1 With order=True python compares the fields as a tuple (amount, currency). So
#     Money(100, 'USD') > Money(1, 'UZS') is True because 100 > 1, but it compares dollars with
#     sums and this makes no sense. My __lt__ raises CurrencyMismatchError in this case.
# 7.2 sum() starts with 0, so it does 0 + Money(...). int.__add__ does not know Money, and Money has
#     no __radd__, so python raises: unsupported operand type(s) for +: 'int' and 'Money'.
#     For production I choose sum(items, start=Money(0, 'UZS')). With __radd__ accepting 0,
#     the line 0 + price would become legal everywhere and hide bugs, and sum of an empty
#     list would return 0 and not Money. With start= the currency is written clearly.
# 7.3 They must return NotImplemented (not raise and not return False). Then python tries
#     the reflected method of the other operand, and if nobody knows it, python raises TypeError
#     itself (for == it falls back to False).
# 7.4 Money * Money: no, 5 sum * 5 sum is "square sums", it has no meaning. Money / Money:
#     also no for now, the result would be a plain number and not Money, and it is not obvious
#     what people expect. Only Money * int (quantity) is obvious, so only this is supported.

from dataclasses import dataclass
from functools import total_ordering
import pytest


class CurrencyMismatchError(ValueError):
    pass


@total_ordering
@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

    def __post_init__(self):
        if not isinstance(self.amount, int):
            raise TypeError("amount must be int (minor units)")
        if not (isinstance(self.currency, str) and len(self.currency) == 3):
            raise ValueError("currency must be a 3-letter code")

    def _check(self, other):
        if self.currency != other.currency:
            raise CurrencyMismatchError(f"{self.currency} and {other.currency}")

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return Money(self.amount + other.amount, self.currency)

    def __mul__(self, qty):
        if not isinstance(qty, int):
            return NotImplemented
        return Money(self.amount * qty, self.currency)

    __rmul__ = __mul__

    def __lt__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        self._check(other)
        return self.amount < other.amount


def test_add_same_currency():
    assert Money(100, "UZS") + Money(250, "UZS") == Money(350, "UZS")


def test_add_different_currency():
    with pytest.raises(CurrencyMismatchError):
        Money(100, "UZS") + Money(100, "USD")


def test_add_not_money():
    with pytest.raises(TypeError):
        Money(100, "UZS") + 5


def test_multiply_both_sides():
    price = Money(25_000, "UZS")
    assert price * 3 == Money(75_000, "UZS")
    assert 3 * price == Money(75_000, "UZS")


def test_multiply_money_by_money_not_allowed():
    with pytest.raises(TypeError):
        Money(5, "UZS") * Money(5, "UZS")


def test_equal_to_other_type_is_false():
    assert (Money(500, "UZS") == 500) is False
    assert Money(5, "UZS") != 5


def test_same_amount_different_currency_not_equal():
    assert Money(100, "UZS") != Money(100, "USD")


def test_compare():
    assert Money(100, "UZS") < Money(200, "UZS")
    assert Money(300, "UZS") > Money(200, "UZS")
    assert Money(200, "UZS") <= Money(200, "UZS")
    assert Money(200, "UZS") >= Money(200, "UZS")


def test_compare_different_currency():
    with pytest.raises(CurrencyMismatchError):
        Money(100, "USD") > Money(1, "UZS")


def test_order_true_is_wrong():
    @dataclass(frozen=True, order=True)
    class BadMoney:
        amount: int
        currency: str

    # this is True and it is nonsense, dollars vs sums
    assert BadMoney(100, "USD") > BadMoney(1, "UZS")


def test_sum_plain_fails():
    items = [Money(100, "UZS"), Money(200, "UZS")]
    with pytest.raises(TypeError):
        sum(items)


def test_sum_with_start():
    items = [Money(100, "UZS"), Money(200, "UZS"), Money(300, "UZS")]
    assert sum(items, start=Money(0, "UZS")) == Money(600, "UZS")


def test_sum_empty_list():
    assert sum([], start=Money(0, "UZS")) == Money(0, "UZS")


def test_sum_mixed_currency():
    items = [Money(100, "UZS"), Money(100, "USD")]
    with pytest.raises(CurrencyMismatchError):
        sum(items, start=Money(0, "UZS"))


def test_hash_and_dict_key():
    prices = {Money(100, "UZS"): "tea", Money(100, "USD"): "coffee"}
    assert prices[Money(100, "UZS")] == "tea"
    assert len({Money(1, "UZS"), Money(1, "UZS")}) == 1


def test_frozen():
    m = Money(100, "UZS")
    with pytest.raises(Exception):
        m.amount = 5


def test_bad_values():
    with pytest.raises(TypeError):
        Money(1.5, "UZS")
    with pytest.raises(ValueError):
        Money(100, "SUM2")
