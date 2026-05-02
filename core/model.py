import torch
from torchvision.models import efficientnet_b0

def load_model(weights_path="models/best_model-v3.pth"):
    # 1. Base (temel) EfficientNet-B0 mimarisini yukle
    model = efficientnet_b0(weights=None)
    
    # 2. Classifier (siniflandirici) kismini 2 sinif (Real/Fake) uretecek sekilde degistir
    model.classifier[1] = torch.nn.Linear(model.classifier[1].in_features, 2)
    
    # 3. Agirliklari SIKI (strict=True) bir sekilde yukle
    # Eger mimari ve agirliklar uyusmazsa hata verecektir, boylece rastgele agirlik calismasini onleriz.
    model.load_state_dict(torch.load(weights_path, map_location="cpu"), strict=True)
    model.eval()
    return model