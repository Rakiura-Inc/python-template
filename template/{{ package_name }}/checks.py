"""Checks the notebooks run on a member's answers, so the feedback reads the same everywhere."""

from dataclasses import dataclass

__all__ = ("Feedback", "check_close")


@dataclass(frozen=True)
class Feedback:
    """The outcome of a check: whether it passed, and one line to show the member."""

    passed: bool
    message: str

    def __str__(self) -> str:
        return self.message


def check_close(name: str, value: float | None, expected: float, tolerance: float) -> Feedback:
    """Compare a member's number with the expected one, within an absolute tolerance."""
    if value is None:
        return Feedback(passed=False, message=f"{name}: not answered yet. Fill in the cell above, then run this one.")
    difference = abs(value - expected)
    if difference <= tolerance:
        return Feedback(passed=True, message=f"{name}: {value:g} is right (within {tolerance:g} of {expected:g}).")
    return Feedback(
        passed=False,
        message=f"{name}: {value:g} is {difference:g} away from the expected value. Look again at the step above.",
    )
