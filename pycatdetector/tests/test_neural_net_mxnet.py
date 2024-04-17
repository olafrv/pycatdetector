# pyright: reportMissingImports=false

from pycatdetector.NeuralNetMXNet import NeuralNetMXNet
import mxnet as mx
import os


def test_main():
    nn = NeuralNetMXNet()
    assert 'cat' in nn.get_classes()
    print()
    dirname = os.path.join(os.curdir, 'pycatdetector', 'tests', 'images')
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)

        # Use analyze() + in memory image
        with open(fullpath, 'rb') as fp:
            str_image = fp.read()
            image = mx.img.imdecode(str_image)
            scored_labels = nn.get_scored_labels(0.5, nn.analyze(image))
            print(fullpath + " => " + repr(scored_labels))
            labels = [label['label'] for label in scored_labels]
            if len(labels) == 0:
                assert False
            else:
                assert 'cat' in labels

        # Use analyze() + image file path
        scored_labels = nn.get_scored_labels(0.5, nn.analyze(fullpath))
        print(fullpath + " => " + repr(scored_labels))
        labels = [label['label'] for label in scored_labels]
        if len(labels) == 0:
            assert False
        else:
            assert 'cat' in labels
