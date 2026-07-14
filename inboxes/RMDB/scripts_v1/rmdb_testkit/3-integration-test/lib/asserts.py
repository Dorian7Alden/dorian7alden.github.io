"""测试断言与辅助函数。"""
from __future__ import annotations

import re
from typing import Iterable


class TestFailure(Exception):
    pass


class SkipTest(Exception):
    pass


BAD_LOG_RE = re.compile(
    r"assert|terminate|corruption|double free|segfault|InternalError",
    re.IGNORECASE,
)


def table_rows(output: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in output.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells:
            rows.append(cells)
    if len(rows) <= 1:
        return []
    return rows[1:]


def single_int(output: str) -> int:
    for row in table_rows(output):
        if len(row) == 1 and re.fullmatch(r"-?\d+", row[0]):
            return int(row[0])
    raise TestFailure(f"expected one integer row, got:\n{output}")


def single_float(output: str) -> float:
    for row in table_rows(output):
        if len(row) == 1:
            try:
                return float(row[0])
            except ValueError:
                pass
    raise TestFailure(f"expected one numeric row, got:\n{output}")


def assert_no_error(output: str, sql: str = "") -> None:
    lowered = output.lower()
    if "error" in lowered or "failure" in lowered or lowered.strip() == "abort":
        raise TestFailure(f"unexpected error for {sql!r}: {output!r}")


def assert_abort(output: str, sql: str = "") -> None:
    if "abort" not in output.lower():
        raise TestFailure(f"expected abort for {sql!r}, got: {output!r}")


def exec_many(client, sqls: Iterable[str]) -> None:
    for sql in sqls:
        out = client.sql(sql)
        assert_no_error(out, sql)


def stat_value(stats: str, key: str) -> int:
    m = re.search(rf"{re.escape(key)}=(\d+)", stats)
    if not m:
        raise TestFailure(f"missing stat {key!r} in:\n{stats}")
    return int(m.group(1))
