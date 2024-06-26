from pycatdetector.NeuralNetPyTorch import NeuralNetPyTorch
import os


def test_main():
    nn = NeuralNetPyTorch("FasterRCNN_MobileNet_V3_Large_320_FPN")
    assert 'cat' in nn.get_classes()
    print()
    dirname = os.path.join(os.curdir, 'pycatdetector', 'tests', 'images')
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        scored_labels = nn.get_scored_labels(nn.analyze(fullpath), 0.9)
        print(fullpath + " => " + repr(scored_labels))
        labels = [label['label'] for label in scored_labels]
        if len(labels) == 0:
            assert False
        else:
            assert 'cat' in labels
