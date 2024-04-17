# pyright: reportMissingImports=false

import torch
from torchvision import models


def test_main():
    print(dir(models))
    print(torch.__config__.show())  # AVX flag
    if torch.cuda.is_available():
        print(repr(torch.cuda.get_device_name()))
        print(repr(torch.cuda.get_device_properties(0)))
    else:
        print("CUDA not available")
