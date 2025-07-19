from .NeuralNetPyTorch import NeuralNetPyTorch


def preload():

    print('Preloading: PyTorch models...')
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_FPN')
    NeuralNetPyTorch('FasterRCNN_MobileNet_V3_Large_320_FPN')

    print('Preloading: Done.')
