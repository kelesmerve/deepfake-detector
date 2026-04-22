import torch
from torchvision import transforms
from facenet_pytorch import MTCNN
from PIL import Image

preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

mtcnn_detector = MTCNN(keep_all=False, select_largest=True, device='cuda' if torch.cuda.is_available() else 'cpu')

def crop_face(img: Image.Image, margin=0.35) -> Image.Image:
    boxes, probs = mtcnn_detector.detect(img)
    if boxes is not None and len(boxes) > 0:
        box = boxes[0]  
        x1, y1, x2, y2 = box
        w = x2 - x1
        h = y2 - y1
        
        center_x = x1 + w / 2
        center_y = y1 + h / 2
        
        side_len = max(w, h)
        new_side_len = side_len * (1 + margin * 2)
        
        nx1 = max(0, int(center_x - new_side_len / 2))
        ny1 = max(0, int(center_y - new_side_len / 2))
        nx2 = min(img.width, int(center_x + new_side_len / 2))
        ny2 = min(img.height, int(center_y + new_side_len / 2))
        
        return img.crop((nx1, ny1, nx2, ny2))
    return img