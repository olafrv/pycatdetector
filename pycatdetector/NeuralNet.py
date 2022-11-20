import os
import numpy as np
import mxnet as mx
from gluoncv import model_zoo, data, utils
import warnings

class NeuralNet:
    net = None

    def __init__(self, modelName='ssd_512_resnet50_v1_voc', pretrained=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore") # https://github.com/apache/mxnet/issues/15281
            self.net = model_zoo.get_model(name=modelName, pretrained=pretrained)

    def analyze(self, image):
        if isinstance(image, str):
            if os.path.exists(image):
                x, img = data.transforms.presets.ssd.load_test(image, short=512)
            else:
                raise FileNotFoundError
        else:
            imageNDArray = mx.nd.array(image) # From NumPy Array
            x, img = data.transforms.presets.ssd.transform_test(imgs=imageNDArray, short=512)     

        class_IDs, scores, bounding_boxes = self.net(x)

        return { 
            "image": img, 
            "classes": class_IDs, 
            "scores": scores, 
            "boxes": bounding_boxes 
        }

    def getClasses(self):
        return self.net.classes

    def get_scored_labels(self, minScore, result):
        classes = result["classes"][0]
        scores = result["scores"][0]
        boxes = result["boxes"][0]
        scored_labels = []

        # As in https://cv.gluon.ai/_modules/gluoncv/utils/viz/bbox.html
        if mx is not None:
            if isinstance(boxes, mx.nd.NDArray):
                boxes = boxes.asnumpy()
            if isinstance(classes, mx.nd.NDArray):
                classes = classes.asnumpy()
            if isinstance(scores, mx.nd.NDArray):
                scores = scores.asnumpy()

        for i, box in enumerate(boxes):
            if scores.flat[i]>=minScore and classes.flat[i]>=0:
                label = self.net.classes[int(classes.flat[i])]
                score = scores.flat[i]
                scored_labels.append({
                    "label": label,
                    "score": score
                })
        return scored_labels

    def plot(self, result, ax):
        img = result["image"]
        classes = result["classes"][0]
        scores = result["scores"][0]
        boxes = result["boxes"][0]

        # https://cv.gluon.ai/api/utils.html#gluoncv.utils.viz.plot_bbox
        # https://cv.gluon.ai/_modules/gluoncv/utils/viz/bbox.html
        utils.viz.plot_bbox(img=img, bboxes=boxes, scores=scores, 
            labels=classes, class_names=self.net.classes, ax=ax)
