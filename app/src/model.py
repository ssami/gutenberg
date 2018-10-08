import time
from src.generator import ModelHashGenerator
from src.exceptions import InvalidDataError
from abc import ABC, abstractmethod
from src.exceptions import ModelException, LoaderException
import fastText

from src.exceptions import InvalidType
from src.model_loader import BaseModelLoader


class ModelInfo():

    def __init__(self, description, metrics, location,
                 hash_generator=ModelHashGenerator()):
        self.__required_checks(
            hash_generator=hash_generator,
            location=location
        )
        self.hash = hash_generator.generate()
        self.timestamp = time.time()
        self.description = description
        self.metrics = metrics
        self.location = location

    def __required_checks(self, **kwargs):
        for k,v in kwargs.items():
            if v is None:
                raise InvalidDataError('{0} cannot be empty'.format(k))

    @property
    def items(self):
        return self.__dict__

    @property
    def live(self):
        return self.live

    @live.setter
    def live(self, is_live):
        self.live = is_live


class FeedbackInfo():

    def __init__(self, model_id, label_actual, label_expected):
        self.model_id = model_id
        self.label_actual = label_actual
        self.label_expected = label_expected


class BaseModel(ABC):

    def __init__(self, loader):
        self.model_loader = loader
        self.model = None

    @abstractmethod
    def load(self):
        self.model = self.model_loader.read()

    @abstractmethod
    def unload(self):
        self.model_loader.unread()
        self.model = None   # unset model

    @abstractmethod
    def predict(self, data):
        pass


class FastTextModel(BaseModel):

    def load(self, local_path=None):
        try:
            self.model = fastText.load_model(
                self.model_loader.read(local_path))
        except LoaderException:
            raise
        except Exception as e:
            raise ModelException(str(e))

        return self.model

    def predict(self, data):
        return self.model.predict(data)

    def unload(self):
        self.model = None


def get_model(model_type, location, loader):
    for clz in BaseModel.__subclasses__():
        if clz.__name__ == model_type:
            for klz in BaseModelLoader.__subclasses__():
                if klz.__name__ == loader:
                    ldr = klz(location)
                    return clz(ldr)
            raise InvalidType('{0} is not a valid loader type'.format(loader))

    raise InvalidType('{0} is not a valid model type'.format(model_type))

