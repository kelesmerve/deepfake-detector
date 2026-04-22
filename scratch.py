import torch
import timm
from torch import nn

class ModelWrapper(nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model('efficientnet_b4', pretrained=False, num_classes=0)
        self.head = nn.Sequential(
            nn.BatchNorm1d(1792),
            nn.ReLU(),
            nn.Linear(1792, 512),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(512, 1)
        )

if __name__ == "__main__":
    sd = torch.load("models/best_model.pth", map_location="cpu")
    m = ModelWrapper()
    missing, unexpected = m.load_state_dict(sd, strict=False)
    print("Missing keys:", len(missing))
    if len(missing) < 10: print(missing)
    print("Unexpected keys:", len(unexpected))
    if len(unexpected) < 10: print(unexpected)
