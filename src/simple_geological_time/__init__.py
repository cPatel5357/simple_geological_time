"""Package init — re-exports the public API."""
from .core import to_scientific, from_scientific, GeologicalDateError

__all__ = ["to_scientific", "from_scientific", "GeologicalDateError"]
