"""
==================================================
An enumeration that goes hand in hand with strings
==================================================
"""
from __future__ import annotations
import enum


class StringEnum(enum.IntEnum):
    """An enumeration that goes hand in hand with strings.

    It allows for construction from strings and comparison with strings.
    For an example, see `python_helpers.tests.test_enumeration`."""
    @classmethod
    def allowed_values(cls) -> str:
        """Return the allowed str values."""
        return ', '.join(x.name for x in cls)

    @classmethod
    def from_str(cls, string: str) -> StringEnum:
        """Generate an instance corresponding to `string`."""
        for value in cls:
            if string == value.name:
                return value
        raise ValueError(f'Unknown value. Needs to be one of'
                         f' {cls.allowed_values()}.')

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, str):
            other = type(self).from_str(other)
        return super().__eq__(other)

    def __hash__(self):
        return hash(self.name)
