from abc import ABCMeta, abstractclassmethod, abstractmethod, abstractstaticmethod
from typing import Type, TypeVar, Union
class IJSONSerializable(metaclass=ABCMeta):
    @abstractmethod
    def serialize_to_json(self) -> str:
        raise NotImplementedError
