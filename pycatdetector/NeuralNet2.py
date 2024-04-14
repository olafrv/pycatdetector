# pyright: reportMissingImports=false

import os
import PIL
from torchvision.io import read_image
from torchvision.transforms import ToTensor, ToPILImage
from torchvision.utils import draw_bounding_boxes
from torchvision.models.detection import \
    fasterrcnn_mobilenet_v3_large_fpn, \
    FasterRCNN_MobileNet_V3_Large_FPN_Weights


# References
# https://pytorch.org/vision/stable/index.html
# https://pytorch.org/vision/stable/models.html#classification
# https://pytorch.org/vision/main/models/faster_rcnn.html
# https://pytorch.org/vision/stable/auto_examples/others/
#   plot_visualization_utils.html

class NeuralNet2:
    weights = None
    model = None
    preprocess = None

    def __init__(self, model_name=None, pretrained=True):
        ###
        # https://pytorch.org/vision/0.17/_modules/torchvision/models/detection/
        #   faster_rcnn.html#FasterRCNN_MobileNet_V3_Large_FPN_Weights
        # https://pytorch.org/vision/main/_modules/torchvision/models/detection/
        #   faster_rcnn.html#fasterrcnn_resnet50_fpn
        # https://github.com/pytorch/vision/blob/main/torchvision/
        #   models/detection/faster_rcnn.py
        ###
        self.weights = FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT
        self.model = fasterrcnn_mobilenet_v3_large_fpn(weights=self.weights,
                                                       box_score_thresh=0.7)
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
            "image": img,
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

    def plot(self, result, ax):
        img = result["image"]
        labels = result["labels"]
        boxes = result["boxes"]
        img_tensor = ToTensor()(img)  # Convert PIL Image to tensor
        img_tensor = img_tensor.mul(255).byte()  # Convert to tensor (uint8)
        img_tensor = draw_bounding_boxes(img_tensor, boxes,
                                         labels=labels, width=20)
        img = ToPILImage()(img_tensor)
        ax.imshow(img)
