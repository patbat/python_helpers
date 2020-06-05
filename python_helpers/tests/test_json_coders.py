from dataclasses import dataclass
import json
import os
from typing import List

import numpy as np
import pytest
from scipy.optimize import root

from python_helpers import json_coders


class Dummy(json_coders.JsonSerializable):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def from_json(cls, json_string: str):
        return cls(**json.loads(json_string))

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def test_file_handling(tmp_path):
    file_path = (tmp_path / 'test.js').name
    instance = Dummy(lis=[1, 2, 3], s='string')
    instance.safe(file_path)
    instance2 = Dummy.load(file_path)
    os.remove(file_path)
    assert instance == instance2


@dataclass
class Data:
    number: float
    values: List[int]


@pytest.fixture
def datacls():
    return Data(3.141, [1, 2, 3])


def test_dataclass_encoding(datacls):
    json_string = json.dumps(datacls, cls=json_coders.DataclassEncoder)
    data2 = Data(**json.loads(json_string))
    assert datacls == data2


def test_numpy_array_encoding():
    data = np.random.random((2, 2))
    json_string = json.dumps(data, cls=json_coders.NumpyEncoder)
    data2 = np.array(json.loads(json_string))
    assert np.all(data == data2)


def test_optimize_result_encoding():
    res = root(lambda x: x**2, 0.5)
    json_string = json.dumps(res, cls=json_coders.NumpyEncoder)
    res2 = json.loads(json_string,
                      object_hook=json_coders.optimize_result_decode)
    assert res == res2


class NumpyData(json_coders.JsonSerializable):
    def __init__(self, datacl, ndarray):
        self.datacl = datacl
        self.ndarray = ndarray

    @classmethod
    def from_json(cls, json_string: str):
        dictionary = json.loads(json_string)
        dictionary['ndarray'] = np.array(dictionary['ndarray'])
        dictionary['datacl'] = Data(**dictionary['datacl'])
        return cls(**dictionary)

    def to_json(self):
        encoders = json_coders.DataclassEncoder, json_coders.NumpyEncoder
        DataclassAndNumpy = json_coders.combine_encoders('DataclassAndNumpy',
                                                         encoders)
        return json.dumps(vars(self), cls=DataclassAndNumpy)

    def __eq__(self, other):
        return (self.datacl == other.datacl
                and np.all(self.ndarray == other.ndarray))


def test_combine_encoders(datacls):
    data = NumpyData(datacls, np.random.random((2, 2)))
    data2 = NumpyData.from_json(data.to_json())
    assert data == data2
