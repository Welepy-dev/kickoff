import pytest
from bigscore import render_score


def test_line_count():
    result = render_score(1, 0)
    assert result.count("\n") == 2  # 3 lines → 2 newlines


def test_single_digit_width():
    lines = render_score(0, 0).splitlines()
    widths = {len(line) for line in lines}
    assert len(widths) == 1, "all rows should have equal width for single-digit score"


def test_multi_digit_wider_than_single():
    single = render_score(9, 9).splitlines()[0]
    multi = render_score(10, 9).splitlines()[0]
    assert len(multi) > len(single)


def test_multi_digit_both_sides():
    lines = render_score(12, 34).splitlines()
    assert len(lines) == 3
    widths = {len(line) for line in lines}
    assert len(widths) == 1


def test_zero_zero():
    result = render_score(0, 0)
    assert result  # non-empty
    assert len(result.splitlines()) == 3
