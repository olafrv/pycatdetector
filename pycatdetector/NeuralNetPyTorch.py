# pyright: reportMissingImports=false

import os
import PIL
from torchvision.io import read_image
from torchvision.transforms import ToTensor, ToPILImage
from torchvision.utils import draw_bounding_boxes
from torchvision.models.detection import \
    fasterrcnn_mobilenet_v3_large_fpn, \
    fasterrcnn_mobilenet_v3_large_320_fpn, \
    FasterRCNN_MobileNet_V3_Large_320_FPN_Weights, \
    FasterRCNN_MobileNet_V3_Large_FPN_Weights
from .AbstractNeuralNet import AbstractNeuralNet


class NeuralNetPyTorch(AbstractNeuralNet):
    """
    NeuralNetPyTorch is a class that represents a neural network
    model implemented using PyTorch, references:
    - https://pytorch.org/vision/main/models.html
    - https://pytorch.org/vision/stable/_modules/torchvision/models/detection/ssdlite.html  # noqa
    - https://pytorch.org/vision/stable/_modules/torchvision/models/detection/faster_rcnn.html  # noqa

    Args:
        model_name (str): The name of the model to use.
        min_score (float, optional): The minimum score threshold for 
                                     object detection. Defaults to 0.7.

    Raises:
        ValueError: If an invalid model_name is provided.

    Attributes:
        weights: The weights of the model.
        model: The PyTorch model.
        preprocess: The preprocessing steps for the input image.

    """

    def __init__(self, model_name, min_score=0.7):
        """
        Initializes a NeuralNetPyTorch object.

        Args:
            model_name (str): The name of the model to use.
            min_score (float, optional): The minimum score threshold for
                                         object detection. Defaults to 0.7.

        Raises:
            ValueError: If an invalid model_name is provided.

        """

        if model_name == "FasterRCNN_MobileNet_V3_Large_FPN":
            self.weights = \
                FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT
            self.model = fasterrcnn_mobilenet_v3_large_fpn(
                weights=self.weights, box_score_thresh=min_score)
        elif model_name == "FasterRCNN_MobileNet_V3_Large_320_FPN":
            self.weights = \
                FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT
            self.model = fasterrcnn_mobilenet_v3_large_320_fpn(
                weights=self.weights, box_score_thresh=min_score)
        else:
            raise ValueError("Invalid model_name" + repr(model_name))

        self.model.eval()
        self.preprocess = self.weights.transforms()

    def analyze(self, image) -> dict:
        """
        Analyzes an image using the neural network model.

        Args:
            image (str or PIL.Image.Image or numpy.ndarray):
                The input image to analyze.

        Returns:
            dict: A dictionary containing the analysis results,
                  including the image, labels, scores, and boxes.

        Raises:
            FileNotFoundError: If the input image file is not found.

        """

        img = None
        if isinstance(image, str):
            if os.path.exists(image):
                img = read_image(image)  # PIL Image
            else:
                raise FileNotFoundError
        else:
            if not isinstance(image, PIL.Image.Image):
                img = PIL.Image.fromarray(image)  # PIL Image

        batch = [self.preprocess(img)]
        prediction = self.model(batch)[0]
        labels = [
            self.weights.meta["categories"][i] for i in prediction["labels"]
        ]

        return {
            "image": img,  # PIL Image
            "labels": labels,
            "scores": prediction["scores"],
            "boxes": prediction["boxes"]
        }

    def get_classes(self) -> list:
        """
        Returns the classes/categories used by the model.

        Returns:
            list: A list of class/category names.

        """

        return self.weights.meta["categories"]

    def get_scored_labels(self, result, min_score=-1) -> list:
        """
        Filters the labels based on the minimum score threshold.

        Args:
            result (dict): The analysis result dictionary.
            min_score (float, optional): The minimum score threshold.
                                         Defaults to -1.

        Returns:
            list: A list of scored labels.

        """

        labels = result["labels"]
        scores = result["scores"].detach().numpy()
        boxes = result["boxes"].detach().numpy()
        scored_labels = []

        for i, box in enumerate(boxes):
            if scores[i] >= min_score:
                scored_labels.append({
                    "label": labels[i],
                    "score": scores[i]
                })
        return scored_labels

    def plot(self, result) -> PIL.Image.Image:
        """
        Plots the bounding boxes on the image.

        Args:
            result (dict): The analysis result dictionary.

        Returns:
            PIL.Image.Image: The image with bounding boxes plotted.

        """

        img = result["image"]
        labels = result["labels"]
        boxes = result["boxes"]
        img_tensor = ToTensor()(img)  # Convert PIL Image to tensor
        img_tensor = img_tensor.mul(255).byte()  # Convert to tensor (uint8)
        img_tensor = draw_bounding_boxes(img_tensor, boxes,
                                         labels=labels, width=1)
        img = ToPILImage()(img_tensor)
        return img
