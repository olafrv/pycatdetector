import os
import mxnet as mx
from gluoncv import model_zoo, data, utils
import warnings

class NeuralNet:
    net = None

    def __init__(self, model_name='ssd_512_resnet50_v1_voc', pretrained=True):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore") # https://github.com/apache/mxnet/issues/15281
            self.net = model_zoo.get_model(name=model_name, pretrained=pretrained)

    def analyze(self, image):
        img = None
        if isinstance(image, str):
            if os.path.exists(image):
                # short = image.shape[0] if image.shape[0]<=256 else 256
                short = 256
                x, img = data.transforms.presets.ssd.load_test(image, short=short) # short <=> pixels (Bigger is slower)
            else:
                raise FileNotFoundError
        else:
            imageNDArray = mx.nd.array(image) # From NumPy Array to Apache MX NDArray
            short = image.shape[0] if image.shape[0]<=256 else 256
            x, img = data.transforms.presets.ssd.transform_test(imgs=imageNDArray, short=short) # short <=> pixels (Bigger is slower) 

        class_IDs, scores, bounding_boxes = self.net(x)

        return { 
            "image": img, 
            "classes": class_IDs, 
            "scores": scores, 
            "boxes": bounding_boxes 
        }

    def get_classes(self):
        return self.net.classes

    def get_scored_labels(self, min_score, result):
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
            if scores.flat[i]>=min_score and classes.flat[i]>=0:
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
