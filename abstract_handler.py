import abc
from PIL import Image


class AbstractHandler(abc.ABC):
    """Abstract Handler: Implement this for 
    """

    @abc.abstractmethod
    def __init__(self, config):
        pass

    @abc.abstractmethod
    def render(self) -> Image:
        pass
