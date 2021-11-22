"""
====================================================================
Custom json encoders/decoders for numpy/scipy/dataclass objects etc.
====================================================================

This module enables one to encode certain objects to json
and vice versa, which cannot be encoded/decoded by default.
Moreover, it provides facilities to json encode/decode custom types with
greater ease.
"""
from __future__ import annotations
import abc
from collections.abc import Callable, Iterable
import json
import dataclasses
from typing import Any, Union

import numpy as np
from scipy.optimize import Bounds, OptimizeResult  # type: ignore


class JsonSerializable(abc.ABC):
    """Objects that can be read from/stored into json strings and files."""

    @classmethod
    @abc.abstractmethod
    def from_json(cls, json_string: str) -> JsonSerializable:
        """Generate an object from a json string."""

    @abc.abstractmethod
    def to_json(self) -> str:
        """Convert an object into a json string."""

    @classmethod
    def load(cls, file_path: str) -> JsonSerializable:
        """Load an object from a json file."""
        with open(file_path, 'r') as input_file:
            return cls.from_json(input_file.read())

    def safe(self, file_path: str) -> None:
        """Store an object as a json file."""
        with open(file_path, 'w') as output:
            output.write(self.to_json())


def combine_encoders(name: str,
                     encoders: Iterable[type]) -> type:
    """Combine several Encoders to a new one.

    Use this e.g. as
    >>> DataclassAndNumpy = combine_encoders('DataclassAndNumpy',
    ...                                      (DataclassEncoder, NumpyEncoder))
    """
    return type(name, tuple(encoders), {})


def combine_decoders(decoders: Iterable[Callable[[dict], Any]]
                     ) -> Callable[[dict], Any]:
    """Combine several decoders to a new one.

    Use this e.g. as
    >>> string = "[...]"  # a string containing json content
    >>> decoder = combine_decoders([complex_decode, bounds_decode])
    >>> json.loads(string, object_hook=decoder)
    """
    functions = tuple(decoders)

    def dec(dictionary):
        for func in functions:
            res = func(dictionary)
            if type(res) != dict:
                return res
        return dictionary

    return dec


# this is very similar to the example in the official python documentation
class ComplexEncoder(json.JSONEncoder):
    """Encode complex numbers.

    Use this as the optional `cls` argument to `json.dump` or `json.dumps` to
    encode complex numbers."""

    def default(self, obj):
        if isinstance(obj, complex):
            return {'complex': True, 'real': obj.real, 'imag': obj.imag}
        return super().default(obj)


# this is adapted from the example in the official python documentation,
# but has a more stringent test criterion
def complex_decode(dictionary: dict) -> Union[complex, dict]:
    """Restore a `complex` object from a json dictionary.

    Use this as the optional `object_hook` argument to `json.load` or
    `json.loads` to restore a `complex` object."""
    if tuple(dictionary.keys()) == ('complex', 'real', 'imag'):
        return complex(dictionary['real'], dictionary['imag'])
    return dictionary


class DataclassEncoder(json.JSONEncoder):
    """Encode a dataclass object.

    Use this as the optional `cls` argument to `json.dump` or `json.dumps` to
    encode dataclasses.

    To revert this operation, just feed the dict resulting from a call
    to `json.load` or `json.loads` back into the
    __init__ of the desired dataclass via `**`.
    """

    def default(self, obj):
        if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
            return dataclasses.asdict(obj)
        return super().default(obj)


class NumpyEncoder(json.JSONEncoder):
    """Encode basic numpy types.

    Use this as the optional `cls` argument to `json.dump` or `json.dumps` to
    encode numpy types.
    """

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def optimize_result_decode(dictionary: dict) -> Any:
    """Restore a `scipy.optimize.OptimizeResult` from a json dictionary.

    Use this as the optional `object_hook` argument to `json.load` or
    `json.loads` to restore an `OptimizeResult` object.

    Warnings
    --------
    This assumes that `dictionary` represents only a single `OptimizeResult`
    and nothing else.
    """
    # `OptimizeResult` inherits from `dict`, due to the inner workings of
    # the `json` module this makes it impossible to encode/decode
    # `OptimizeResult`s  via a custom class inheriting from
    # `json.JSONEncoder` like, e.g., complex numbers or `Bounds` instances.
    content = dict(dictionary)
    for key, value in content.items():
        if isinstance(value, list):
            content[key] = np.array(value)
        if key == 'x' and isinstance(value, float):
            content[key] = np.array(value)
    return OptimizeResult(content)


class BoundsEncoder(json.JSONEncoder):
    """Encode `Bounds`.

    Use this as the optional `cls` argument to `json.dump` or `json.dumps` to
    encode `Bounds`.
    """

    def default(self, obj):
        if isinstance(obj, Bounds):
            res = {'Bounds': True}
            res.update(vars(obj))
            return res
        return super().default(obj)


def bounds_decode(dictionary: dict) -> Union[Bounds, dict]:
    """Restore a `Bounds` object from a json dictionary.

    Use this as the optional `object_hook` argument to `json.load` or
    `json.loads` to restore a `Bounds` object."""
    if tuple(dictionary.keys()) == ('Bounds', 'lb', 'ub', 'keep_feasible'):
        return Bounds(dictionary['lb'], dictionary['ub'],
                      dictionary['keep_feasible'])
    return dictionary
