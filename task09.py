# Task 9 - mixins
#
# 9.1 I expected all four lines: updated_at, validate, INSERT, audit. But it prints only the first two.
#     Invoice.__mro__ is: Invoice, TimestampMixin, ValidateMixin, AuditMixin, Model, object.
#     super().save() goes to the next class in this list, and ValidateMixin did not call
#     super().save(), so the chain stops there, AuditMixin and Model never run. That is why
#     the invoice was not saved but the API still answered 201.
# 9.2 Order now: set updated_at, validate fields, INSERT/UPDATE, write audit entry.
#     AuditMixin calls super().save() first and prints after it, so its line comes after
#     Model.save (INSERT), it runs on the way back.
# 9.3 It must raise an exception. A silent return looks like a good save for the caller
#     (no error, the code goes on), but nothing was saved and the audit is also skipped,
#     this is the same bug as in the task. An exception can not be missed.
# 9.4 Mro is Invoice, TimestampMixin, AuditMixin, Model, ValidateMixin, object. Model.save
#     does not call super(), so the chain stops at Model and ValidateMixin never runs. My prediction:
#     updated_at, INSERT, audit (and no validate). I ran it and got exactly this.
#     The rule: Model (the base that does not call super) must be the last base, after all mixins.

import io
from contextlib import redirect_stdout
import pytest


class Model:
    def save(self):
        print("Model.save: INSERT/UPDATE")


class TimestampMixin:
    def save(self):
        print("TimestampMixin: set updated_at")
        super().save()


class ValidateMixin:
    def save(self):
        print("ValidateMixin: validate fields")
        if self.amount <= 0:
            raise ValueError("invoice amount must be positive")
        super().save()


class AuditMixin:
    def save(self):
        super().save()
        print("AuditMixin: write audit entry")


class Invoice(TimestampMixin, ValidateMixin, AuditMixin, Model):
    def __init__(self, amount=100):
        self.amount = amount


def run_save(obj):
    buf = io.StringIO()
    with redirect_stdout(buf):
        obj.save()
    return buf.getvalue().splitlines()


def test_mro():
    names = [c.__name__ for c in Invoice.__mro__]
    assert names == ["Invoice", "TimestampMixin", "ValidateMixin", "AuditMixin", "Model", "object"]


def test_all_four_lines_in_order():
    assert run_save(Invoice()) == [
        "TimestampMixin: set updated_at",
        "ValidateMixin: validate fields",
        "Model.save: INSERT/UPDATE",
        "AuditMixin: write audit entry",
    ]


def test_invalid_invoice_raises_and_stops():
    buf = io.StringIO()
    with redirect_stdout(buf):
        with pytest.raises(ValueError):
            Invoice(amount=0).save()
    lines = buf.getvalue().splitlines()
    assert lines == ["TimestampMixin: set updated_at", "ValidateMixin: validate fields"]


def test_model_in_the_middle_breaks_chain():
    class Invoice2(TimestampMixin, AuditMixin, Model, ValidateMixin):
        def __init__(self, amount=100):
            self.amount = amount

    assert run_save(Invoice2()) == [
        "TimestampMixin: set updated_at",
        "Model.save: INSERT/UPDATE",
        "AuditMixin: write audit entry",
    ]
    # and an invalid invoice is saved without any check, which is bad
    assert "Model.save: INSERT/UPDATE" in run_save(Invoice2(amount=-5))


if __name__ == "__main__":
    print(Invoice.__mro__)
    Invoice().save()
