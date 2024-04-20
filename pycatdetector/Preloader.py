from .NeuralNetMXNet import NeuralNetMXNet
from .NeuralNetPyTorch import NeuralNetPyTorch


def preload():
    print('Preloading: MXNet models...')
    NeuralNetMXNet('ssd_512_resnet50_v1_voc')
    NeuralNetMXNet('ssd_512_mobilenet1.0_voc')

    print('Preloading: PyTorch models...')
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_FPN')
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_320_FPN')

    print('Preloading: Done.')
