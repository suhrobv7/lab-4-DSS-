# Task 5 - promotion
#
# 5.1 No, it is true only for the type of the object, not for its whole life. The person is the same
#     employee all the time, only the role (how the pay is counted) changes on promotion.
#     So the role must be a part of Employee, not a subclass.
# 5.4 Employee HAS a role history: composition, one employee to many (role, start_date) records,
#     and the history lives and dies with the employee.

from datetime import date
import pytest


class LecturerRole:
    def __init__(self, hours):
        self.hours = hours

    def monthly_pay(self):
        return self.hours * 120_000


class HeadRole:
    def __init__(self, salary):
        self.salary = salary

    def monthly_pay(self):
        return self.salary + 3_000_000  # management bonus


class Employee:
    def __init__(self, emp_id, name, role, start_date):
        self.emp_id = emp_id
        self.name = name
        self.role_history = [(role, start_date)]

    @property
    def role(self):
        return self.role_history[-1][0]

    def change_role(self, new_role, start_date):
        if start_date < self.role_history[-1][1]:
            raise ValueError("new role can not start before the old one")
        self.role_history.append((new_role, start_date))

    def role_on(self, day):
        found = None
        for role, start in self.role_history:
            if start <= day:
                found = role
        if found is None:
            raise ValueError("employee did not work on " + str(day))
        return found

    def monthly_pay(self, on=None):
        if on is None:
            return self.role.monthly_pay()
        return self.role_on(on).monthly_pay()


def test_pay_of_lecturer():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    assert e.monthly_pay() == 9_600_000


def test_promotion_keeps_same_object_and_id():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    same = e
    e.change_role(HeadRole(14_000_000), date(2025, 2, 1))
    assert e is same
    assert e.emp_id == 1
    assert e.monthly_pay() == 17_000_000


def test_other_objects_still_point_to_employee():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    payroll = {e: ["jan"]}
    timesheet = [e]
    e.change_role(HeadRole(14_000_000), date(2025, 2, 1))
    assert payroll[e] == ["jan"]
    assert timesheet[0].monthly_pay() == 17_000_000


def test_last_month_uses_old_role():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    e.change_role(HeadRole(14_000_000), date(2025, 2, 1))
    assert e.monthly_pay(on=date(2025, 1, 15)) == 9_600_000
    assert e.monthly_pay(on=date(2025, 2, 1)) == 17_000_000
    assert e.monthly_pay(on=date(2025, 3, 10)) == 17_000_000


def test_before_first_role():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    with pytest.raises(ValueError):
        e.monthly_pay(on=date(2024, 1, 1))


def test_role_can_not_start_in_the_past():
    e = Employee(1, "Ali", LecturerRole(80), date(2024, 9, 1))
    e.change_role(HeadRole(14_000_000), date(2025, 2, 1))
    with pytest.raises(ValueError):
        e.change_role(LecturerRole(10), date(2024, 12, 1))
