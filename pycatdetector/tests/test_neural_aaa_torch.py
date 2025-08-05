# pyright: reportMissingImports=false

import torch
import torchvision
from torchvision.models import list_models


def test_main():
    print()
    print(list_models(module=torchvision.models.detection))
    print()
    print(list_models(module=torchvision.models.quantization))
    print()
    print(torch.__config__.show())  # AVX flag
    if torch.cuda.is_available():
        print(repr(torch.cuda.get_device_name()))
        print(repr(torch.cuda.get_device_properties(0)))
    else:
        print(
            "CUDA not available"
            + ", See tips at: https://github.com/olafrv/ai_chat_llama2"
        )
