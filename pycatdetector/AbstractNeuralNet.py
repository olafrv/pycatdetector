from abc import ABC, abstractmethod


class AbstractNeuralNet(ABC):
    @abstractmethod
    def analyze(self, image):
        pass

    @abstractmethod
    def get_classes(self):
        pass

    @abstractmethod
    def get_scored_labels(self, min_score, result):
        pass

    @abstractmethod
    def plot(self, result):
        pass
