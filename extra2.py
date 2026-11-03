# E2 - classes that register themselves
#
# E2.2 A class that is abstract still has abstract methods, a concrete one has none. I check this
#      with inspect.isabstract(cls) inside __init_subclass__. It works there (python 3.10+ looks at the
#      methods by hand when ABCMeta did not finish yet). Abstract classes may skip the name and
#      are not registered, a concrete class without name raises TypeError when the module is imported.
# E2.3 A second class with the same name raises ValueError, so it can not replace the old one silently.
# E2.4 The explicit registry from Task 10 is better when we want control: only some methods are
#      enabled for some country or config, the class is in a module that nobody imports (then
#      it is never registered and we get "unknown payment method" again), or the public name
#      must differ from the class, or we want to see all names in one file.

from abc import ABC, abstractmethod
import inspect
import pytest


class UnknownPaymentMethodError(ValueError):
    pass


class PaymentMethod(ABC):
    registry = {}
    refundable = True

    def __init_subclass__(cls, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if inspect.isabstract(cls):
            return
        if name is None:
            raise TypeError(f"{cls.__name__} is concrete, give it a name: class {cls.__name__}(PaymentMethod, name=...)")
        if name in PaymentMethod.registry:
            old = PaymentMethod.registry[name].__name__
            raise ValueError(f"name {name!r} is already used by {old}")
        PaymentMethod.registry[name] = cls

    @abstractmethod
    def fee(self, amount):
        pass

    @classmethod
    def create(cls, name):
        key = name.strip().lower()
        if key not in cls.registry:
            raise UnknownPaymentMethodError(f"unknown {name!r}, supported: {', '.join(sorted(cls.registry))}")
        return cls.registry[key]()


class Card(PaymentMethod, name="card"):
    def fee(self, amount):
        return amount * 15 // 1000


class Click(PaymentMethod, name="click"):
    def fee(self, amount):
        return amount * 10 // 1000


class Payme(PaymentMethod, name="payme"):
    def fee(self, amount):
        return amount * 10 // 1000


class Cash(PaymentMethod, name="cash"):
    refundable = False

    def fee(self, amount):
        return 0


class BankTransfer(PaymentMethod, name="bank_transfer"):
    def fee(self, amount):
        return 5_000


def test_classes_are_registered():
    assert PaymentMethod.registry["click"] is Click
    assert set(PaymentMethod.registry) >= {"card", "click", "payme", "cash", "bank_transfer"}


def test_create():
    assert isinstance(PaymentMethod.create(" Click "), Click)
    assert PaymentMethod.create("bank_transfer").fee(1) == 5_000


def test_unknown():
    with pytest.raises(UnknownPaymentMethodError):
        PaymentMethod.create("bitcoin")


def test_missing_name_fails_at_class_creation():
    with pytest.raises(TypeError):
        class NoName(PaymentMethod):
            def fee(self, amount):
                return 0


def test_abstract_middle_class_needs_no_name():
    class Mobile(PaymentMethod):
        def phone_fee(self):
            return 100

    # Mobile is still abstract (fee is missing), so it is not in the registry
    assert Mobile not in PaymentMethod.registry.values()

    class Uzum(Mobile, name="uzum_test"):
        def fee(self, amount):
            return self.phone_fee()

    try:
        assert PaymentMethod.create("uzum_test").fee(10) == 100
    finally:
        del PaymentMethod.registry["uzum_test"]


def test_duplicate_name_fails_loudly():
    with pytest.raises(ValueError):
        class Click2(PaymentMethod, name="click"):
            def fee(self, amount):
                return 0

    assert PaymentMethod.registry["click"] is Click


def test_new_class_is_enough():
    class Humo(PaymentMethod, name="humo_test"):
        def fee(self, amount):
            return amount // 100

    try:
        assert isinstance(PaymentMethod.create("HUMO_TEST"), Humo)
    finally:
        del PaymentMethod.registry["humo_test"]
