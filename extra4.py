# E4 - loyalty card
#
# E4.2 Customer creates the NoLoyalty object in its own __init__: if it gets loyalty=None
#      (for example from the database) it puts NoLoyalty() there. So there is one single
#      None check in the whole program, in one place, and not fifteen.
# E4.4 Null Object is wrong when "nothing" must stay visible and the code has to react to it.
#      A customer without a saved bank card is not "a card with 0 money": if we used a NoCard object,
#      the payment would go on, try to charge it and fail in a strange place, or even look like
#      a successful payment. There we want an error or a question "add a card first", so a
#      None (or an exception) is better, because the program is forced to handle it.

import pytest


class LoyaltyCard:
    def __init__(self, level):
        self.level = level

    def discount_percent(self):
        return {"silver": 3, "gold": 5, "platinum": 10}[self.level]

    def points_for(self, amount):
        return amount // 10_000


class NoLoyalty:
    def discount_percent(self):
        return 0

    def points_for(self, amount):
        return 0


class Customer:
    def __init__(self, name, loyalty=None):
        self.name = name
        self.loyalty = loyalty if loyalty is not None else NoLoyalty()


def checkout_summary(customer, amount):
    discount = amount * customer.loyalty.discount_percent() // 100
    points = customer.loyalty.points_for(amount)
    return discount, points


def test_customer_with_card():
    c = Customer("Ali", LoyaltyCard("gold"))
    assert checkout_summary(c, 200_000) == (10_000, 20)


def test_customer_without_card():
    c = Customer("Vali")
    assert checkout_summary(c, 200_000) == (0, 0)


def test_loyalty_is_never_none():
    assert Customer("Vali").loyalty is not None
    assert Customer("Vali", None).loyalty is not None


def test_each_level():
    assert checkout_summary(Customer("a", LoyaltyCard("silver")), 100_000) == (3_000, 10)
    assert checkout_summary(Customer("b", LoyaltyCard("platinum")), 100_000) == (10_000, 10)


def test_small_amount_gives_no_points():
    assert checkout_summary(Customer("a", LoyaltyCard("gold")), 9_999) == (499, 0)
