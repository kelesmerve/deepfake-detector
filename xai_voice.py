import torch
import torch.nn as nn
import torchaudio
from transformers import Wav2Vec2Model
import soundfile as sf
import shap
import matplotlib.pyplot as plt
import numpy as np
import warnings

# Gereksiz uyarıları gizleyelim ki terminalimiz temiz kalsın
warnings.filterwarnings("ignore")

print("--- Deepfake SHAP Analiz Aracı Başlatılıyor ---")

# 1. Model Mimarisi (Kaggle'daki ile birebir aynı)
class DeepfakeAudioDetector(nn.Module):
    def __init__(self, model_name="facebook/wav2vec2-base"):
        super(DeepfakeAudioDetector, self).__init__()
        self.wav2vec2 = Wav2Vec2Model.from_pretrained(model_name)
        
        self.classifier = nn.Sequential(
            nn.Linear(self.wav2vec2.config.hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1)
        )

    def forward(self, x):
        outputs = self.wav2vec2(x)
        hidden_states = outputs.last_hidden_state
        pooled_output = hidden_states.mean(dim=1) 
        logits = self.classifier(pooled_output)
        return logits.squeeze(-1) 

# 2. Cihaz Ayarı
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Kullanılan Cihaz: {device}")

# 3. Modeli Yükleme
MODEL_PATH = "models/deepfake_audio_detector_lite.pth"
model = DeepfakeAudioDetector()

print("Model ağırlıkları yükleniyor...")
# Kaggle'da modeli hafifletmek için 16-bit'e (half) çevirmiştik. 
# Bilgisayarında uyumsuzluk olmasın diye map_location=device ile çekip standart 32-bit'e (float) alıyoruz.
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.to(device)
model.float() 
model.eval()
print("Model başarıyla yüklendi!")

# 4. Sesi Yükleme ve Ön İşleme
def preprocess_audio(file_path, target_sr=16000, max_length=64000):
    data, sr = sf.read(file_path, dtype='float32')
    # soundfile returns (frames, channels), torchaudio expects (channels, frames)
    if data.ndim == 1:
        waveform = torch.from_numpy(data).unsqueeze(0)
    else:
        waveform = torch.from_numpy(data).t()
    if waveform.shape[0] > 1:
        waveform = torch.mean(waveform, dim=0, keepdim=True)
    if sr != target_sr:
        resampler = torchaudio.transforms.Resample(orig_freq=sr, new_freq=target_sr)
        waveform = resampler(waveform)
    
    if waveform.shape[1] > max_length:
        waveform = waveform[:, :max_length]
    else:
        padding = max_length - waveform.shape[1]
        waveform = torch.nn.functional.pad(waveform, (0, padding))
        
    return waveform.to(device)

# -------------------------------------------------------------------- #
# BURAYI KENDİ SES DOSYANIN ADIYLA DEĞİŞTİR
TEST_AUDIO_PATH = "LA_E_1001964.flac" 
# -------------------------------------------------------------------- #

print(f"'{TEST_AUDIO_PATH}' işleniyor...")
waveform = preprocess_audio(TEST_AUDIO_PATH)

# 5. SHAP Analizi İçin Fonksiyon
def model_predict(data_np):
    data_torch = torch.from_numpy(data_np).to(device).float()
    with torch.no_grad():
        logits = model(data_torch)
        probs = torch.sigmoid(logits)
    return probs.cpu().numpy()

# Arka plan verisi (Sessizlik)
background = np.zeros((1, 64000), dtype=np.float32)
explainer = shap.KernelExplainer(model_predict, background)

print("SHAP değerleri hesaplanıyor... (Bilgisayarının gücüne göre 1-3 dakika sürebilir, lütfen bekle...)")
audio_np = waveform.cpu().numpy()
shap_values = explainer.shap_values(audio_np, nsamples=100)

# 6. Görselleştirme
print("Analiz tamamlandı! Grafik ekrana çiziliyor...")
plt.figure(figsize=(15, 5))

audio_signal = audio_np[0]
plt.plot(audio_signal, color='gray', alpha=0.5, label='Ses Dalgaları')

shap_val = shap_values[0]
plt.scatter(range(len(audio_signal)), audio_signal, c=shap_val, cmap='RdBu_r', s=2, label='SHAP Önemi')

tahmin_orani = model_predict(audio_np)[0]
sonuc_metni = "SAHTE" if tahmin_orani >= 0.5 else "GERÇEK"

plt.title(f"SHAP Analizi | Modelin Tahmini: {sonuc_metni} (Sahtelik Olasılığı: %{tahmin_orani*100:.1f})")
plt.colorbar(label="SHAP Değeri (Kırmızı=Sahtelik Belirtisi, Mavi=Gerçeklik Belirtisi)")
plt.legend()
plt.tight_layout()
plt.show()