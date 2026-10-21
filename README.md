# simple_geological_time

Converts between human-readable geological age strings (e.g., "65 Ma") and scientific notation in years before present (e.g., 6.5e7).

## Usage

```python
from simple_geological_time import to_scientific, from_scientific

# Human-readable to scientific notation in years BP
age_years = to_scientific("65 Ma")    # -> 65000000.0

# Scientific notation back to human-readable
age_str = from_scientific(1.5e9)       # -> "1.5 Ga"

# Control significant digits
age_str = from_scientific(65432109, significant_digits=3)  # -> "65.4 Ma"
```

## Why this exists

Geological literature expresses ages in a mix of units — years, kilo-annum (ka), mega-annum (Ma), and giga-annum (Ga). When you need to do arithmetic or comparison on these ages programmatically, you need them in a single numeric form. This library does exactly that conversion in two directions, with no dependencies and a small surface.

The trade-off: this library treats inputs as **ages in years before present** (BP, where "present" is the year 2000 CE by the geological convention). It does not convert to or from calendar/ISO dates. That is a deliberate boundary — mixing geological ages with calendar dates on million-year timescales introduces ambiguity this library is not designed to resolve.

## Edge cases

- **Negative ages** are rejected. In the BP convention, a negative age is physically meaningless. If you need to represent a date after the year 2000, this is the wrong library.
- **Rounding** in `from_scientific` uses `ROUND_HALF_UP`. Floating-point coefficients are rounded to the number of significant digits you request (default 2). If you pass a value like `65432109` with the default, you get `"65 Ma"` — the digits after the second significant figure are discarded.
- **Bare numbers** without a unit are treated as years BP, so `"1000"` means 1000 years before present, not a calendar year.
- The unit must be exactly one of `Ga`, `Ma`, `ka`, `a`. Variants like `Myr` or `M` are not accepted.
