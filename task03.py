# Task 3 - subscriptions
#
# 3.1 The missing line is super().__init__(user, months) in FamilySubscription.__init__.
#     Python does not check attributes when the object is created, base_monthly is just not set.
#     The error comes only when price() reads self.base_monthly, so it fails late.
# 3.4 Only Subscription, one line: VAT_PERCENT = 15. I did not open StudentSubscription or
#     FamilySubscription at all because they only override net().

import pytest


class Subscription:
    VAT_PERCENT = 12

    def __init__(self, user, months):
        self.user = user
        self.months = months
        self.base_monthly = 50_000

    def net(self):
        return self.base_monthly * self.months

    def price(self):
        return self.net() * (100 + self.VAT_PERCENT) // 100


class StudentSubscription(Subscription):
    def net(self):
        return super().net() // 2


class FamilySubscription(Subscription):
    def __init__(self, user, months, members):
        super().__init__(user, months)
        self.members = members

    def net(self):
        extra = 20_000 * (len(self.members) - 1) * self.months
        return super().net() + extra


def test_standard_3_months():
    assert Subscription("ali", 3).price() == 168_000


def test_student_3_months():
    # net 75 000, with vat 84 000
    assert StudentSubscription("vali", 3).price() == 84_000


def test_family_4_members_3_months():
    # net 150 000 + 20 000 * 3 * 3 = 330 000, with vat 369 600
    fam = FamilySubscription("karimov", 3, ["a", "b", "c", "d"])
    assert fam.price() == 369_600


def test_family_has_base_monthly():
    fam = FamilySubscription("karimov", 1, ["a"])
    assert fam.base_monthly == 50_000


def test_vat_change_affects_all():
    old = Subscription.VAT_PERCENT
    Subscription.VAT_PERCENT = 15
    try:
        assert Subscription("ali", 3).price() == 172_500
        assert StudentSubscription("vali", 3).price() == 86_250
        fam = FamilySubscription("karimov", 3, ["a", "b", "c", "d"])
        assert fam.price() == 379_500
    finally:
        Subscription.VAT_PERCENT = old
