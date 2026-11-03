# Task 1 - payment methods
#
# 1.2 I made one class per method, so Click and Payme are two classes. Today the rule is the
#     same, but if Payme changes its fee next month I only edit Payme and Click stays safe.
#     With one class and two objects I would need a parameter or an if for the difference.
# 1.3 Checkout only calls method.fee() and method.refundable, so there is no if/elif left.
# 1.4 BankTransfer is a new class only. I changed 0 lines in Checkout (and 0 in other classes).

from abc import ABC, abstractmethod
import pytest


class PaymentMethod(ABC):
    refundable = True

    @abstractmethod
    def fee(self, amount):
        pass


class Card(PaymentMethod):
    def fee(self, amount):
        return amount * 15 // 1000  # 1.5 %


class Click(PaymentMethod):
    def fee(self, amount):
        return amount * 10 // 1000  # 1 %


class Payme(PaymentMethod):
    def fee(self, amount):
        return amount * 10 // 1000  # 1 %


class Cash(PaymentMethod):
    refundable = False

    def fee(self, amount):
        return 0


class BankTransfer(PaymentMethod):
    def fee(self, amount):
        return 5_000


class Checkout:
    def pay(self, method, amount):
        fee = method.fee(amount)
        return {"charged": amount + fee, "refundable": method.refundable}


def test_card():
    res = Checkout().pay(Card(), 100_000)
    assert res == {"charged": 101_500, "refundable": True}


def test_click():
    res = Checkout().pay(Click(), 100_000)
    assert res == {"charged": 101_000, "refundable": True}


def test_payme():
    res = Checkout().pay(Payme(), 100_000)
    assert res == {"charged": 101_000, "refundable": True}


def test_cash():
    res = Checkout().pay(Cash(), 100_000)
    assert res == {"charged": 100_000, "refundable": False}


def test_bank_transfer():
    res = Checkout().pay(BankTransfer(), 100_000)
    assert res == {"charged": 105_000, "refundable": True}


def test_abstract_class_cannot_be_created():
    with pytest.raises(TypeError):
        PaymentMethod()


def test_method_without_fee_is_not_allowed():
    class Broken(PaymentMethod):
        pass

    with pytest.raises(TypeError):
        Broken()
