# pyright: reportMissingImports=false

from .AbstractNeuralNet import AbstractNeuralNet
import os
import PIL
from torchvision.io import read_image
from torchvision.transforms import ToTensor, ToPILImage
from torchvision.utils import draw_bounding_boxes

# https://pytorch.org/vision/main/models.html
# https://pytorch.org/vision/stable/_modules/torchvision/models/detection/ssdlite.html
# https://pytorch.org/vision/stable/_modules/torchvision/models/detection/faster_rcnn.html
from torchvision.models.detection import \
    fasterrcnn_mobilenet_v3_large_fpn, \
    fasterrcnn_mobilenet_v3_large_320_fpn, \
    FasterRCNN_MobileNet_V3_Large_320_FPN_Weights, \
    FasterRCNN_MobileNet_V3_Large_FPN_Weights


class NeuralNetPyTorch(AbstractNeuralNet):
    weights = None
    model = None
    preprocess = None
    MIN_FORCED_SCORE = 0.7  # Avoid low confidence detections

    def __init__(self, model_name):

        if model_name == "FasterRCNN_MobileNet_V3_Large_FPN":
            self.weights = FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT
            self.model = fasterrcnn_mobilenet_v3_large_fpn(
                weights=self.weights, box_score_thresh=self.MIN_FORCED_SCORE)
        elif model_name == "FasterRCNN_MobileNet_V3_Large_320_FPN":
            self.weights = FasterRCNN_MobileNet_V3_Large_320_FPN_Weights.DEFAULT
            self.model = fasterrcnn_mobilenet_v3_large_320_fpn(
                weights=self.weights, box_score_thresh=self.MIN_FORCED_SCORE)
        else:
            raise ValueError("Invalid model_name" + repr(model_name))

        self.model.eval()
        self.preprocess = self.weights.transforms()

    def analyze(self, image):
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

    def get_classes(self):
        return self.weights.meta["categories"]

    def get_scored_labels(self, min_score, result):
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
        img = result["image"]
        labels = result["labels"]
        boxes = result["boxes"]
        img_tensor = ToTensor()(img)  # Convert PIL Image to tensor
        img_tensor = img_tensor.mul(255).byte()  # Convert to tensor (uint8)
        img_tensor = draw_bounding_boxes(img_tensor, boxes,
                                         labels=labels, width=1)
        img = ToPILImage()(img_tensor)
        return img
