from pycatdetector.NeuralNet import NeuralNet
import mxnet as mx
import os


def test_main():
    nn = NeuralNet()
    dirname = os.path.join(os.curdir, 'pycatdetector', 'tests', 'images')
    print()
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        with open(fullpath, 'rb') as fp:
            str_image = fp.read()
            image = mx.img.imdecode(str_image)
            labels = nn.get_scored_labels(0.5, nn.analyze(image))
            if len(labels) == 0:
                assert False
            for label in labels:
                print(fullpath + "=>" + str(labels))
                assert label['label'] == 'cat'

            labels = nn.get_scored_labels(0.5, nn.analyze(fullpath))

            if len(labels) == 0:
                assert False
            for label in labels:
                print(fullpath + "=>" + str(labels))
                assert label['label'] == 'cat'

    assert 'cat' in nn.get_classes()
