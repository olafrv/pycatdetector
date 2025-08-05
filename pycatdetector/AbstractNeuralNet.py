from abc import ABC, abstractmethod
from PIL import Image
from typing import Optional


class AbstractNeuralNet(ABC):
    @abstractmethod
    def analyze(self, image) -> dict:
        pass

    @abstractmethod
    def get_classes(self) -> list:
        pass

    @abstractmethod
    def get_scored_labels(self, result: dict, min_score: Optional[float] = -1) -> list:
        pass

    @abstractmethod
    def plot(self, result: dict) -> Image.Image:
        pass
