"""Convert between human-readable dates and scientific notation for geological time.

This module works with ages expressed as years before present (BP), where
"present" is fixed at the year 2000 CE. Geological ages are conventionally
written as positive numbers (e.g., 65 Ma = 65 million years before present),
while scientific notation is the floating-point form (e.g., 6.5e7).

Design decision: we interpret the input string as a *geological age* (years
BP), not a calendar date. This means the sign convention is geological: a
larger number means older. We do not attempt to convert to or from ISO-8601
calendar dates because the entire point of scientific notation in
stratigraphy is to avoid calendar reckoning on million-year timescales.

Supported human-readable forms:
    - "65 Ma"         -> 65 million years BP  -> 6.5e7
    - "1.5 Ga"        -> 1.5 billion years BP -> 1.5e9
    - "1000 a"        -> 1000 years BP       -> 1.0e3
    - "1000"          -> bare number, treated as years BP -> 1.0e3
    - "1.234e6 a"     -> scientific input with unit -> 1.234e6

The "a" suffix (Latin *annus*) is the SI-accepted unit for year. "Ma" and
"Ga" are standard abbreviations for mega-annum and giga-annum in the
geological sciences. We also accept "ka" (kilo-annum) for completeness.
"""

import re


class GeologicalDateError(ValueError):
    """Raised when a human-readable geological age cannot be parsed."""


# Mapping of geological time unit suffixes to their multiplier in years.
# Order matters: longer suffixes are checked first so "Ma" is not split into "M" + "a".
_UNIT_MULTIPLIERS = {
    "Ga": 1e9,
    "Ma": 1e6,
    "ka": 1e3,
    "a": 1,
}

# Regex for the numeric part: integer, decimal, or scientific notation.
# We intentionally allow an optional leading sign, though geological ages are
# normally non-negative. A negative age BP is physically meaningless, so we
# reject it explicitly after parsing rather than silently producing a negative.
_NUMBER_PATTERN = re.compile(
    r"^\s*"
    r"(?P<number>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"\s*"
)


def to_scientific(human_readable: str) -> float:
    """Convert a human-readable geological age string to scientific notation.

    Returns the age in years BP as a float.

    Raises GeologicalDateError if the string cannot be parsed or if the age is
    negative (which is physically meaningless in the BP convention).
    """
    if not isinstance(human_readable, str):
        raise GeologicalDateError(
            f"Expected a string, got {type(human_readable).__name__}"
        )

    text = human_readable.strip()
    if not text:
        raise GeologicalDateError("Empty input")

    match = _NUMBER_PATTERN.match(text)
    if not match:
        raise GeologicalDateError(f"No numeric value found in: {human_readable!r}")

    number_str = match.group("number")
    remainder = text[match.end():].strip()

    try:
        value = float(number_str)
    except ValueError as exc:
        # This should not happen given the regex, but we guard against it for
        # safety in case the regex is modified later.
        raise GeologicalDateError(
            f"Could not parse numeric value {number_str!r}: {exc}"
        ) from exc

    if remainder:
        # Find a matching unit suffix. Check longer suffixes first.
        multiplier = None
        for unit in ("Ga", "Ma", "ka", "a"):
            if remainder == unit:
                multiplier = _UNIT_MULTIPLIERS[unit]
                break
        if multiplier is None:
            raise GeologicalDateError(
                f"Unrecognised unit suffix {remainder!r} in: {human_readable!r}"
            )
        value *= multiplier

    if value < 0:
        raise GeologicalDateError(
            f"Negative age is physically meaningless in BP convention: {human_readable!r}"
        )

    return value


def from_scientific(years_bp: float, significant_digits: int = 2) -> str:
    """Convert an age in years BP to a human-readable geological string.

    The output uses the largest unit that produces a coefficient of at least 1.0,
    which matches the geological convention of expressing ages as a small number
    with a magnitude-appropriate suffix (e.g., 6.5 Ma rather than 6500000 a).

    Years of exactly 0 return "0 a".

    ``significant_digits`` controls the number of significant digits in the
    coefficient. It must be at least 1.
    """
    if not isinstance(years_bp, (int, float)):
        raise GeologicalDateError(
            f"Expected a number, got {type(years_bp).__name__}"
        )
    if not isinstance(significant_digits, int) or significant_digits < 1:
        raise GeologicalDateError("significant_digits must be a positive integer")

    years_float = float(years_bp)

    if years_float == 0:
        return "0 a"

    if years_float < 0 or (
        years_float == float("inf") or years_float != years_float  # NaN check
    ):
        raise GeologicalDateError(
            f"Age must be a non-negative finite number, got {years_bp!r}"
        )

    # Choose the largest unit whose multiplier does not make the coefficient < 1.
    chosen_unit = "a"
    chosen_multiplier = 1
    for unit in ("Ga", "Ma", "ka", "a"):
        mult = _UNIT_MULTIPLIERS[unit]
        coeff = years_float / mult
        if coeff >= 1.0:
            chosen_unit = unit
            chosen_multiplier = mult
            break

    coeff = years_float / chosen_multiplier

    # Round to the requested significant digits to avoid floating-point noise.
    if coeff != 0:
        from decimal import ROUND_HALF_UP, Decimal

        decimal_coeff = Decimal(str(coeff))
        # Quantize to the specified number of significant digits.
        # Calculate the order of magnitude.
        import math

        order = int(math.floor(math.log10(abs(float(decimal_coeff)))))
        # Decimal places to quantize to: significant_digits - 1 - order
        dp = significant_digits - 1 - order
        quantized = decimal_coeff.quantize(
            Decimal(f"1e{-dp}") if dp > 0 else Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
        # Format: if it's an integer value, show without decimal.
        float_val = float(quantized)
        if float_val == int(float_val):
            coeff_str = str(int(float_val))
        else:
            # Use repr to strip trailing zeros but keep precision.
            coeff_str = repr(float_val)
    else:
        coeff_str = "0"

    return f"{coeff_str} {chosen_unit}"
