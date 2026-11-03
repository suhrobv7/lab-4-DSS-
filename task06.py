# Task 6 - exporter
#
# 6.1 export_report only needs one thing from target: a write() method that takes bytes.
#     It does not care if it is a real file, so the isinstance check was too strict.
# 6.2 Writable is a Protocol, so any class with write(data: bytes) -> int fits, no parent needed.
#     (the / after data is there so the parameter name does not have to be the same as in BytesIO)
# 6.4 Without any check, an object with no write() fails only when the program gets to
#     target.write(...) and raises AttributeError at runtime, maybe after half of the data is
#     processed. mypy does find it before running: see bad_example() at the bottom, mypy says
#     the argument has incompatible type (no attribute "write").

from typing import Any, Protocol
import io
import pytest


class Writable(Protocol):
    def write(self, data: bytes, /) -> int: ...


def export_report(rows: list, target: Writable) -> None:
    for r in rows:
        target.write((",".join(map(str, r)) + "\n").encode())


class S3Upload:
    def __init__(self, bucket, key):
        self.bucket, self.key = bucket, key
        self.parts = []

    def write(self, data: bytes) -> int:
        self.parts.append(data)  # real code uploads them later
        return len(data)


class FakeTarget:
    def __init__(self):
        self.chunks = []

    def write(self, data: bytes) -> int:
        self.chunks.append(data)
        return len(data)


rows = [(1, "ali", 5000), (2, "vali", 7000)]
expected = b"1,ali,5000\n2,vali,7000\n"


def test_bytesio():
    buf = io.BytesIO()
    export_report(rows, buf)
    assert buf.getvalue() == expected


def test_s3():
    s3 = S3Upload("reports", "march.csv")
    export_report(rows, s3)
    assert b"".join(s3.parts) == expected


def test_own_fake():
    fake = FakeTarget()
    export_report(rows, fake)
    assert b"".join(fake.chunks) == expected


def test_object_without_write_fails_at_runtime():
    bad: Any = object()  # Any, so mypy does not complain here
    with pytest.raises(AttributeError):
        export_report(rows, bad)


class NoWrite:
    def read(self):
        return b""


def bad_example():
    # not called anywhere, it is only here so mypy can show the error
    export_report(rows, NoWrite())
