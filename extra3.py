# E3 - classes or functions
#
# E3.1 The third rule (free delivery) does not fit apply(total) -> int. It does not change the total
#      of the goods, it changes the delivery price. So the interface was too small: a rule
#      must get the whole order (goods and delivery) and return a new order. I changed
#      apply(total) to apply(order) in both styles.
# E3.2 The "never below 0" rule lives in Cart.total(). It is about the result of all rules
#      together, and one rule does not know what the others did. If it lived in every discount, a new
#      discount could forget it (like the None checks in E4).
# E3.3 Code review comment:
#      "For now functions are enough: each rule is one small pure function and the tests are short.
#      But when a rule also needs a name for the receipt and a validity period, a class is easier,
#      because the data (name, dates) and the behaviour live together in one object and we can add
#      is_valid(date) next to apply(). With functions we would attach attributes to them or keep
#      three parallel lists, which is worse. So: plain functions/partial for rules that are only a
#      calculation, a class when the rule has its own data or more than one method."

from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from functools import partial


@dataclass(frozen=True)
class Order:
    goods: int
    delivery: int = 15_000


# style 1: classes

class DiscountRule(ABC):
    @abstractmethod
    def apply(self, order):
        pass


class PercentOff(DiscountRule):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, order):
        return replace(order, goods=order.goods * (100 - self.percent) // 100)


class AmountOffAbove(DiscountRule):
    def __init__(self, limit, amount):
        self.limit, self.amount = limit, amount

    def apply(self, order):
        if order.goods > self.limit:
            return replace(order, goods=order.goods - self.amount)
        return order


class FreeDeliveryAbove(DiscountRule):
    def __init__(self, limit):
        self.limit = limit

    def apply(self, order):
        if order.goods > self.limit:
            return replace(order, delivery=0)
        return order


# style 2: plain functions (with partial)

def percent_off(percent, order):
    return replace(order, goods=order.goods * (100 - percent) // 100)


def amount_off_above(limit, amount, order):
    if order.goods > limit:
        return replace(order, goods=order.goods - amount)
    return order


def free_delivery_above(limit, order):
    if order.goods > limit:
        return replace(order, delivery=0)
    return order


class Cart:
    def __init__(self, goods, rules, delivery=15_000):
        self.goods = goods
        self.rules = rules  # list of functions: order -> order
        self.delivery = delivery

    def total(self):
        order = Order(self.goods, self.delivery)
        for rule in self.rules:
            order = rule(order)
            order = replace(order, goods=max(0, order.goods))
        return order.goods + order.delivery


def class_rules():
    rules = [PercentOff(10), AmountOffAbove(200_000, 20_000), FreeDeliveryAbove(150_000)]
    return [r.apply for r in rules]


def function_rules():
    return [
        partial(percent_off, 10),
        partial(amount_off_above, 200_000, 20_000),
        partial(free_delivery_above, 150_000),
    ]


def both_styles():
    return [class_rules(), function_rules()]


def test_big_order():
    # 300 000 -> 270 000 -> 250 000, delivery is free
    for rules in both_styles():
        assert Cart(300_000, rules).total() == 250_000


def test_small_order():
    # 100 000 -> 90 000, no other rule works, delivery 15 000
    for rules in both_styles():
        assert Cart(100_000, rules).total() == 105_000


def test_middle_order():
    # 160 000 -> 144 000 (not above 200 000 and not above 150 000 anymore after discount)
    for rules in both_styles():
        assert Cart(160_000, rules).total() == 144_000 + 15_000


def test_limit_is_strict():
    # only the 20 000 rule, exactly 200 000 is not "above"
    for rules in [[AmountOffAbove(200_000, 20_000).apply], [partial(amount_off_above, 200_000, 20_000)]]:
        assert Cart(200_000, rules).total() == 200_000 + 15_000
        assert Cart(200_001, rules).total() == 180_001 + 15_000


def test_never_below_zero():
    for rules in [[AmountOffAbove(0, 50_000).apply], [partial(amount_off_above, 0, 50_000)]]:
        assert Cart(10_000, rules, delivery=0).total() == 0


def test_no_rules():
    assert Cart(50_000, []).total() == 65_000


def test_free_delivery_does_not_fit_old_interface():
    # with only a total number we can not say "delivery is free"
    order = FreeDeliveryAbove(100).apply(Order(500))
    assert order.delivery == 0 and order.goods == 500
