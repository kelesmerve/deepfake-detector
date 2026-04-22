import torch
import timm

class ModelWrapper(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model('efficientnet_b4', pretrained=False, num_classes=0)
        self.head = torch.nn.Sequential(
            torch.nn.BatchNorm1d(1792),
            torch.nn.ReLU(),
            torch.nn.Linear(1792, 512),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.4),
            torch.nn.Linear(512, 1)
        )
    def forward(self, x):
        f = self.backbone(x)
        out = self.head(f)
        out = out - 0.4
        return torch.cat([torch.zeros_like(out), out], dim=1)

def load_model(weights_path="models/best_model-v3.pth"):
    model = ModelWrapper()
    model.load_state_dict(torch.load(weights_path, map_location="cpu"), strict=False)
    model.eval()
    return model