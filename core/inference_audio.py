import torch
import numpy as np
import soundfile as sf
import torchaudio.transforms as T
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
from ui.components import format_verdict

# --- Sabitler ---
MODEL_ID  = "garystafford/wav2vec2-deepfake-voice-detector"
TARGET_SR = 16000

# Global degiskenler (lazy load)
_feature_extractor = None
_audio_model = None
_device = None

def load_audio_model():
    global _feature_extractor, _audio_model, _device
    if _audio_model is None:
        print("[*] Loading Audio Model...")
        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        _feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_ID)
        _audio_model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
        _audio_model.to(_device)
        _audio_model.eval()
        print("[*] Audio Model Loaded!")

def load_audio(path: str):
    try:
        audio_np, sr = sf.read(path)
    except Exception as e:
        print(f"  [HATA] Dosya okunamadi: {e}")
        return None, None

    # Stereo → Mono
    if audio_np.ndim > 1:
        audio_np = np.mean(audio_np, axis=1)

    # float32'ye donustur
    audio_np = audio_np.astype(np.float32)

    # Resample gerekiyorsa
    if sr != TARGET_SR:
        t = torch.from_numpy(audio_np).unsqueeze(0)
        t = T.Resample(orig_freq=sr, new_freq=TARGET_SR)(t)
        audio_np = t.squeeze(0).numpy()
        sr = TARGET_SR

    return audio_np, sr

def analyze_audio(path: str):
    if path is None:
        return format_verdict("error", 0), "No file provided."
        
    load_audio_model()
    
    audio_np, sr = load_audio(path)
    if audio_np is None:
        return format_verdict("error", 0), "Error: Could not read audio file."
        
    inputs = _feature_extractor(
        audio_np,
        sampling_rate=sr,
        return_tensors="pt",
        padding=True,
    )
    inputs = {k: v.to(_device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = _audio_model(**inputs).logits
        probs  = torch.softmax(logits, dim=-1)

    id2label = _audio_model.config.id2label
    fake_id = 1
    for k, v in id2label.items():
        if "fake" in v.lower() or "spoof" in v.lower():
            fake_id = k
            break
            
    real_id = 1 - fake_id
    
    fake_prob = probs[0][fake_id].item()
    real_prob = probs[0][real_id].item()

    THRESHOLD = 0.90 

    if fake_prob >= THRESHOLD:
        pred = fake_id
        conf = fake_prob
    else:
        pred = real_id
        conf = real_prob

    label = "fake" if pred == fake_id else "real"
    
    verdict_html = format_verdict(label, conf)
    summary = f"### Audio Analysis Results\n\n- **Deepfake Probability:** {fake_prob*100:.2f}%\n- **Authentic Probability:** {real_prob*100:.2f}%\n\n*Note: A threshold of 90% is used for deepfake classification.*"
    
    return verdict_html, summary
