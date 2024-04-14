from pycatdetector.NeuralNet2 import NeuralNet2
import os


def test_main():
    nn = NeuralNet2()
    assert 'cat' in nn.get_classes()
    print()
    dirname = os.path.join(os.curdir, 'pycatdetector', 'tests', 'images')
    for filename in os.listdir(dirname):
        fullpath = os.path.join(dirname, filename)
        scored_labels = nn.get_scored_labels(0.5, nn.analyze(fullpath))
        print(fullpath + " => " + repr(scored_labels))
        labels = [label['label'] for label in scored_labels]
        if len(labels) == 0:
            assert False
        else:
            assert 'cat' in labels
