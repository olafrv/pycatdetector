# pyright: reportMissingImports=false

from torchvision import models


def test_main():
    print(dir(models))