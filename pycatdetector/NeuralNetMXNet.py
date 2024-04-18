# pyright: reportMissingImports=false

from .AbstractNeuralNet import AbstractNeuralNet
import os
import mxnet as mx
from gluoncv import model_zoo, data, utils
import warnings


class NeuralNetMXNet(AbstractNeuralNet):
    """
    A class representing a neural network for object detection.

    Attributes:
        net: The neural network model.

    Methods:
        __init__(self, model_name):
            Initializes the NeuralNet object.

        analyze(self, image):
            Analyzes an image and returns the detected objects.

        get_classes(self):
            Returns the classes of the detected objects.

        get_scored_labels(self, min_score, result):
            Returns the labels of the detected objects with scores above a
            minimum threshold.

        plot(self, result, ax):
            Plots the detected objects on the image.
    """
    net = None

    def __init__(self, model_name):
        """
        Initializes the NeuralNet object.

        Args:
            model_name (str): Name of the model to use for object detection.
            pretrained (bool): Use pretrained model. Default: True.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.net = model_zoo.get_model(
                                           name=model_name,
                                           pretrained=True
                                          )

    def analyze(self, image):
        """
        Analyzes an image and returns the detected objects.

        Args:
            image (str or numpy.ndarray): The image to analyze. Can be a file
            path or a numpy array.

        Returns:
            dict: A dictionary containing the analyzed image, the classes of
            the detected objects, the scores of the detected objects, and
            the bounding boxes of the detected objects.
        """
        img = None
        if isinstance(image, str):
            if os.path.exists(image):
                short = 256
                x, img = data.transforms.presets.ssd.load_test(
                            image, short=short
                         )
            else:
                raise FileNotFoundError
        else:
            imageNDArray = mx.nd.array(image)
            short = image.shape[0] if image.shape[0] <= 256 else 256
            x, img = data.transforms.presets.ssd.transform_test(
                        imgs=imageNDArray, short=short
                     )

        class_IDs, scores, bounding_boxes = self.net(x)

        return {
            "image": img,
            "classes": class_IDs,
            "scores": scores,
            "boxes": bounding_boxes
        }

    def get_classes(self):
        """
        Returns the classes of the detected objects.

        Returns:
            list: A list of strings of the classes of the detected objects.
        """
        return self.net.classes

    def get_scored_labels(self, min_score, result):
        """
        Returns the labels of the detected objects with a minimun score.

        Args:
            min_score (float): The minimum score threshold.
            result (dict): The result dict returned by the analyze method.

        Returns:
            list: List of dicts with labels and scores of the detected objects.
        """
        classes = result["classes"][0]
        scores = result["scores"][0]
        boxes = result["boxes"][0]
        scored_labels = []

        if mx is not None:
            if isinstance(boxes, mx.nd.NDArray):
                boxes = boxes.asnumpy()
            if isinstance(classes, mx.nd.NDArray):
                classes = classes.asnumpy()
            if isinstance(scores, mx.nd.NDArray):
                scores = scores.asnumpy()

        for i, box in enumerate(boxes):
            if scores.flat[i] >= min_score and classes.flat[i] >= 0:
                label = self.net.classes[int(classes.flat[i])]
                score = scores.flat[i]
                scored_labels.append({
                    "label": label,
                    "score": score
                })
        return scored_labels

    def plot(self, result):
        """
        Plots the detected objects on the image.
        https://cv.gluon.ai/_modules/gluoncv/utils/viz/bbox.html

        Args:
            result (dict): The result dict returned by the analyze method.

        Returns:
            numpy.ndarray: The image with the detected objects plotted.
        """
        img = result["image"]
        classes = result["classes"][0]
        scores = result["scores"][0]
        boxes = result["boxes"][0]

        return utils.viz.cv_plot_bbox(
            img=img, bboxes=boxes, scores=scores,
            labels=classes, class_names=self.net.classes)
