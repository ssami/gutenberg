from abc import ABC, abstractmethod
import time


class HashGenerator(ABC):

    @abstractmethod
    def generate(self):
        pass

    @abstractmethod
    def generate_with_input(self, input):
        pass


class ModelHashGenerator(HashGenerator):

    def generate(self):
        return str(int(time.time()))

    def generate_with_input(self, input):
        raise NotImplementedError("ModelHashGenerator does not "
                                  "support generation with input")