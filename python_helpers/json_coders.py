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
import json
import dataclasses
from typing import Any, Dict, Iterable, Union

import numpy as np
from scipy.optimize import OptimizeResult


class JsonSerializable(abc.ABC):
    """Objects that can be read from/stored into json strings and files."""
    @abc.abstractclassmethod
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
# but has a more stringent test criterium
def complex_decode(dictionary: Dict) -> Union[complex, Dict]:
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


def optimize_result_decode(dictionary: Dict) -> Any:
    """Restore a `scipy.optimize.OptimizeResult` from a json dictionary.

    Use this as the optional `object_hook` argument to `json.load` or
    `json.loads` to restore an `OptimizeResult` object."""
    content = dict(dictionary)
    for key, value in content.items():
        if isinstance(value, list):
            content[key] = np.array(value)
        if key == 'x' and isinstance(value, float):
            content[key] = np.array(value)
    return OptimizeResult(content)
