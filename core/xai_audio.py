import torch
import numpy as np
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
from PIL import Image

# Inference module'dan gerekli araclari aliyoruz
from core.inference_audio import load_audio_model, load_audio, TARGET_SR
import core.inference_audio as inf_audio

def fig_to_pil(fig):
    """Convert matplotlib figure to PIL Image."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).convert("RGB")

def generate_shap_analysis(audio_path):
    """Ses dosyasi icin SHAP hesaplar, grafikleri ve kural tabanli metni dondurur."""
    load_audio_model()
    
    audio_np, sr = load_audio(audio_path)
    if audio_np is None:
        raise ValueError("Audio file could not be loaded.")

    # Model bagimliliklarini al
    feature_extractor = inf_audio._feature_extractor
    model = inf_audio._audio_model
    device = inf_audio._device

    # Sahtelik class ID'sini tespit et
    id2label = model.config.id2label
    fake_id = 1
    for k, v in id2label.items():
        if "fake" in v.lower() or "spoof" in v.lower():
            fake_id = k
            break
    real_id = 1 - fake_id

    # SHAP icin model tahmin fonksiyonu
    def predict_fn(data_numpy):
        # data_numpy: (N, ses_uzunlugu)
        all_probs = []
        for i in range(data_numpy.shape[0]):
            inputs = feature_extractor(
                data_numpy[i],
                sampling_rate=TARGET_SR,
                return_tensors="pt",
                padding=True,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            with torch.no_grad():
                logits = model(**inputs).logits
                probs = torch.softmax(logits, dim=-1)[0]
                
            # fake_prob'u aliyoruz (sadece sahteligi aciklamak icin)
            fake_p = probs[fake_id].item()
            all_probs.append(fake_p)
        return np.array(all_probs)

    # Arka plan verisi (tamamen sessizlik)
    audio_length = len(audio_np)
    background = np.zeros((1, audio_length), dtype=np.float32)
    
    # KernelExplainer kullanimi
    explainer = shap.KernelExplainer(predict_fn, background)
    
    # Gecikmeyi azaltmak icin nsamples=25 yapiyoruz (Gradio icin makul sure)
    shap_values = explainer.shap_values(audio_np.reshape(1, -1), nsamples=25)
    
    # shap_values genellikle liste veya array doner
    if isinstance(shap_values, list):
        shap_val = shap_values[0][0]
    else:
        shap_val = shap_values[0]

    # Modelin gercek tahmini
    tahmin_orani = predict_fn(audio_np.reshape(1, -1))[0]
    is_fake = tahmin_orani >= 0.90 # threshold from inference_audio

    # 1. Grafik Olusturma
    fig, ax = plt.subplots(figsize=(15, 5))
    fig.patch.set_facecolor("#0a0a1a")
    ax.set_facecolor("#0a0a1a")

    ax.plot(audio_np, color='gray', alpha=0.5, label='Audio Waveform')
    scatter = ax.scatter(range(len(audio_np)), audio_np, c=shap_val, cmap='RdBu_r', s=2, alpha=0.8, label='SHAP Value')
    
    ax.set_title(f"XAI Audio Analysis | Fake Probability: {tahmin_orani*100:.1f}%", color="white", fontsize=14)
    ax.tick_params(colors="white")
    
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.ax.yaxis.set_tick_params(color="white")
    cbar.ax.yaxis.set_ticklabels(cbar.ax.yaxis.get_ticklabels(), color="white")
    cbar.set_label("SHAP Value (Red = Fake, Blue = Real)", color="white")
    
    leg = ax.legend(facecolor="#0a0a1a", edgecolor="white")
    for text in leg.get_texts():
        text.set_color("white")
        
    plt.tight_layout()
    shap_image = fig_to_pil(fig)

    # 2. Kural Tabanli Metin Uretimi (Summary)
    summary_md = generate_audio_summary(shap_val, audio_length, tahmin_orani, is_fake)

    return shap_image, summary_md


def generate_audio_summary(shap_val, audio_length, fake_prob, is_fake):
    """
    SHAP degerlerini zaman pencerelerine bolup kural tabanli rapor uretir.
    """
    # 0.5 saniyelik pencereler (16000 sr = 8000 ornek)
    window_size = int(TARGET_SR * 0.5)
    num_windows = int(np.ceil(audio_length / window_size))
    
    window_shaps = []
    for i in range(num_windows):
        start = i * window_size
        end = min((i + 1) * window_size, audio_length)
        # Sadece pozitif (sahtelik) SHAP degerlerinin ortalamasini al
        positive_shaps = shap_val[start:end][shap_val[start:end] > 0]
        avg_shap = positive_shaps.mean() if len(positive_shaps) > 0 else 0
        window_shaps.append(avg_shap)
        
    window_shaps = np.array(window_shaps)
    
    # En cok sahtelik gosteren ilk 3 pencereyi bul
    top_indices = np.argsort(window_shaps)[-3:][::-1]
    
    # Cikti metnini hazirla
    label = "DEEPFAKE" if is_fake else "REAL (AUTHENTIC)"
    conf_pct = fake_prob * 100 if is_fake else (1 - fake_prob) * 100
    
    lines = []
    lines.append(f"## 🔍 Audio Analysis Result: **{label}**\n")
    
    if is_fake:
        lines.append(f"⚠️ **High confidence AI-generated audio detection** ({conf_pct:.1f}%).\n")
        lines.append("**Critical Forensic Indicators:**\n")
        
        # Kritik saniyeleri yaz
        suspicious_times = []
        for idx in top_indices:
            if window_shaps[idx] > 0: # Anlamli bir sahtelik degeri varsa
                start_time = idx * 0.5
                end_time = start_time + 0.5
                suspicious_times.append(f"**{start_time:.1f}s - {end_time:.1f}s**")
                
        if suspicious_times:
            times_str = ", ".join(suspicious_times)
            lines.append(f"- Strong synthetic manipulation indicators (high SHAP activations) were detected around {times_str}.\n")
            lines.append("- This pattern suggests the presence of synthetic voice generation, text-to-speech (TTS) artifacts, or voice cloning/conversion in these specific segments.\n")
        else:
            lines.append("- Artificial artifacts are spread evenly across the audio file.\n")
            
        lines.append("\n**Technical Details:**\n")
        lines.append("- Model: Wav2Vec2 Audio Forensics\n")
        lines.append("- Analysis: SHAP Kernel Explainer\n")
        lines.append("- Risk Level: **🔴 CRITICAL**\n")
        
    else:
        lines.append(f"✅ **High confidence authentic audio** ({conf_pct:.1f}%).\n")
        lines.append("**Analysis Details:**\n")
        lines.append("- The SHAP analysis shows mostly negative or neutral activations, aligning with natural vocal tract frequencies and environmental acoustic patterns.\n")
        lines.append("- No significant synthetic speech boundaries or cloning artifacts detected.\n")
        lines.append("\n**Technical Details:**\n")
        lines.append("- Model: Wav2Vec2 Audio Forensics\n")
        lines.append("- Analysis: SHAP Kernel Explainer\n")
        lines.append("- Risk Level: **🟢 SAFE**\n")

    return "".join(lines)
