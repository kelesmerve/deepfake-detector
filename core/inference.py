import time
import cv2
import mimetypes
import numpy as np
import torch
import torch.nn.functional as tF
from PIL import Image

# Yerel Moduller
from core.model import load_model
from core.vision import preprocess, crop_face
from ui.components import format_verdict

# XAI Modulleri
from xai import (
    GradCAM,
    generate_gradcam_figure,
    generate_gradcam_metrics,
    generate_lime_explanation,
    generate_artifact_analysis,
    generate_analysis_summary,
)

# =====================================================================
# GLOBAL BASLATMALAR
# =====================================================================
model = load_model()
gradcam = GradCAM(model)

# =====================================================================
# TEMEL CIKARIM (INFERENCE) FONKSIYONLARI
# =====================================================================

def _progress(progress, value, desc):
    if progress is not None:
        progress(value, desc=desc)

def analyze_image(img):
    """Tek bir goruntu icin tahmin ve Grad-CAM ciktisi uretir."""
    tensor = preprocess(img).unsqueeze(0)
    
    start = time.time()
    with torch.no_grad():
        out = model(tensor)
        probs = tF.softmax(out, dim=1)[0]
        conf, pred = torch.max(probs, dim=0)
    inference_time = time.time() - start

    prediction = pred.item()
    confidence = conf.item()
    fake_prob = probs[0].item()
    real_prob = probs[1].item()

    tensor_grad = preprocess(img).unsqueeze(0)
    cam = gradcam.generate(tensor_grad, target_class=prediction)

    return prediction, confidence, real_prob, fake_prob, cam, inference_time


def _analyze_pil_image(img, progress=None):
    """Yuklenmis bir PIL formatindaki goruntuyu tam pipeline'dan gecirir."""
    _progress(progress, 0.25, "Detecting face")
    img = crop_face(img)

    _progress(progress, 0.45, "Running deepfake model")
    prediction, confidence, real_prob, fake_prob, cam, inference_time = analyze_image(img)

    verdict_html = format_verdict(
        "fake" if prediction == 0 else "real",
        confidence,
        real_prob=real_prob,
        fake_prob=fake_prob,
    )
    _progress(progress, 0.65, "Generating Grad-CAM explanation")
    gradcam_img = generate_gradcam_figure(img, cam)
    gradcam_metrics = generate_gradcam_metrics(cam, prediction, confidence)
    _progress(progress, 0.78, "Generating LIME explanation")
    lime_img, lime_metrics = generate_lime_explanation(model, img, preprocess)
    _progress(progress, 0.88, "Checking forensic artifacts")
    artifact_img = generate_artifact_analysis(img)

    _progress(progress, 0.96, "Preparing report")
    summary = generate_analysis_summary(
        prediction, confidence, cam, inference_time,
        is_video=False, num_frames=1
    )

    return verdict_html, gradcam_img, gradcam_metrics, lime_img, lime_metrics, artifact_img, summary, img


def _analyze_image_file(path, progress=None):
    """Disk uzerindeki bir goruntu dosyasini okuyup analiz eder."""
    _progress(progress, 0.12, "Reading image file")
    img = Image.open(path).convert("RGB")
    return _analyze_pil_image(img, progress=progress)


def _analyze_video_file(path, progress=None):
    """Video dosyasini okuyup belirli karelerden orneklem alarak analiz eder."""
    _progress(progress, 0.12, "Opening video file")
    cap = cv2.VideoCapture(path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    num_samples = min(10, total_frames)
    
    indices = np.linspace(0, total_frames - 1, num=num_samples, dtype=int)

    all_probs = []
    all_cams = []
    first_img = None
    total_time = 0

    for sample_no, idx in enumerate(indices, start=1):
        _progress(progress, 0.15 + (0.45 * sample_no / max(1, num_samples)), f"Analyzing video frame {sample_no}/{num_samples}")
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            continue
            
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = crop_face(img)
        
        if first_img is None:
            first_img = img

        prediction, confidence, real_prob, fake_prob, cam, inf_time = analyze_image(img)
        all_probs.append([real_prob, fake_prob])
        all_cams.append(cam)
        total_time += inf_time

    cap.release()

    if not all_probs or first_img is None:
        return (
            format_verdict("error", 0),
            None, None, None, None, None,
            "Error: Could not read video frames.",
            None,
        )

    # Sonuclari ortala (Aggregation)
    _progress(progress, 0.65, "Combining frame predictions")
    avg_probs = np.mean(all_probs, axis=0)
    avg_real_prob, avg_fake_prob = avg_probs
    final_pred = 0 if avg_fake_prob >= avg_real_prob else 1
    final_conf = avg_fake_prob if final_pred == 0 else avg_real_prob
    avg_cam = np.mean(all_cams, axis=0)

    verdict_html = format_verdict(
        "fake" if final_pred == 0 else "real",
        final_conf,
        real_prob=avg_probs[0],
        fake_prob=avg_probs[1],
    )
    _progress(progress, 0.74, "Generating Grad-CAM explanation")
    gradcam_img = generate_gradcam_figure(first_img, avg_cam)
    gradcam_metrics = generate_gradcam_metrics(avg_cam, final_pred, final_conf)
    _progress(progress, 0.84, "Generating LIME explanation")
    lime_img, lime_metrics = generate_lime_explanation(model, first_img, preprocess)
    _progress(progress, 0.91, "Checking forensic artifacts")
    artifact_img = generate_artifact_analysis(first_img)

    _progress(progress, 0.96, "Preparing report")
    summary = generate_analysis_summary(
        final_pred, final_conf, avg_cam, total_time,
        is_video=True, num_frames=len(all_probs)
    )

    return verdict_html, gradcam_img, gradcam_metrics, lime_img, lime_metrics, artifact_img, summary, first_img


# =====================================================================
# ANA ROUTER FONKSIYONU
# =====================================================================

def predict_file(file_obj, progress=None):
    """Gelen dosyanin tipini (resim/video) tespit edip ilgili fonksiyonu cagirir."""
    if file_obj is None:
        return (
            format_verdict("waiting", 0),
            None, None, None, None, None,
            "Upload an image or video to begin analysis.",
            None,
        )

    path = file_obj.name if hasattr(file_obj, 'name') else file_obj
    _progress(progress, 0.08, "Detecting file type")
    mime, _ = mimetypes.guess_type(path)

    if mime and mime.startswith("image"):
        return _analyze_image_file(path, progress=progress)
    elif mime and mime.startswith("video"):
        return _analyze_video_file(path, progress=progress)
    else:
        return (
            format_verdict("error", 0),
            None, None, None, None, None,
            "Error: Unsupported file type. Please upload JPG, PNG, MP4, or MOV.",
            None,
        )
