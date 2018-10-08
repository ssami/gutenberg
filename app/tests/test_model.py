from src.model import ModelInfo, ModelHashGenerator
from src.location import BaseLocation
from src.exceptions import InvalidDataError
import pytest


class TestGenerator(ModelHashGenerator):

    def generate(self):
        return 5

    def generate_with_input(self, input):
        return input + len(input)


def test_model_info_basic():
    """
    Tests that default inputs will result in successful model object
    """
    model = ModelInfo('test description', {'f1': 0.9},
                      BaseLocation('protoc://something:8080/thingy'))
    assert 'test description' in model.items['description']
    assert model.items['metrics']['f1'] == 0.9
    assert model.items['location'].get_host() == 'something:8080'
    assert model.items['hash'] is not None


def test_model_info_Generator():
    """
    Tests that default inputs will result in successful model object
    """
    model = ModelInfo('test description', {'f1': 0.9},
                      BaseLocation('protoc://something'), TestGenerator())
    assert 'test description' in model.items['description']
    assert model.items['metrics']['f1'] == 0.9
    assert model.items['location'].get_host() == 'something'
    assert model.items['hash'] is 5


def test_model_info():
    """
    Tests that default inputs will result in successful model object
    """
    with pytest.raises(InvalidDataError):
        ModelInfo('test description', {'f1': 0.9},
                          None)
