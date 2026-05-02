import sys
import torch
import soundfile as sf
import numpy as np
import torchaudio.transforms as T
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

def analyze_audio(audio_path):
    """
    Verilen ses dosyasını analiz eder ve sonucunu terminale yazdırır.
    """
    model_id = "garystafford/wav2vec2-deepfake-voice-detector"
    
    # 1. Cihaz seçimi (GPU varsa CUDA, yoksa CPU)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[*] İşlemci olarak '{device}' kullanılıyor...")

    # 2. Ses Dosyasını Okuma (soundfile kullanarak)
    print(f"[*] '{audio_path}' okunuyor...")
    try:
        audio_np, sr = sf.read(audio_path)
    except FileNotFoundError:
        print(f"Hata: '{audio_path}' dosyası bulunamadı.")
        sys.exit(1)
    except Exception as e:
        print(f"Hata: Ses dosyası okunamadı. Detaylar: {e}")
        sys.exit(1)

    # 3. Ön İşleme (Stereo -> Mono dönüşümü)
    if len(audio_np.shape) > 1:
        print("[*] Ses stereo (çift kanal). Mono'ya (tek kanal) dönüştürülüyor...")
        # Kanalların ortalamasını alarak mono yapma
        audio_np = np.mean(audio_np, axis=1)

    # Float32 formatında olduğundan emin olalım (modeller float32 bekler)
    if audio_np.dtype != np.float32:
        audio_np = audio_np.astype(np.float32)

    # Numpy array'den PyTorch Tensor'e dönüştürme ve kanal boyutu ekleme: (1, num_samples)
    audio_tensor = torch.from_numpy(audio_np).unsqueeze(0)

    # 4. Resample (16000 Hz'e dönüştürme)
    target_sr = 16000
    if sr != target_sr:
        print(f"[*] Ses örnekleme hızı {sr} Hz. {target_sr} Hz'e dönüştürülüyor (resample)...")
        # Torchaudio'nun transform metodunu kullanarak resample işlemi
        resampler = T.Resample(orig_freq=sr, new_freq=target_sr)
        audio_tensor = resampler(audio_tensor)
    else:
        print(f"[*] Ses örnekleme hızı zaten {target_sr} Hz, resample işlemine gerek yok.")
    
    # 5. Model ve Processor Yükleme
    print(f"[*] '{model_id}' modeli yükleniyor... (Bu işlem indirme durumuna bağlı olarak biraz sürebilir)")
    try:
        # AutoProcessor bazen tokenizer arar ve bulamazsa hata verir, bu yüzden AutoFeatureExtractor daha güvenlidir.
        processor = AutoFeatureExtractor.from_pretrained(model_id)
        model = AutoModelForAudioClassification.from_pretrained(model_id)
        model.to(device)
        model.eval()  # Çıkarım moduna al
    except Exception as e:
        print(f"Hata: Model yüklenirken bir sorun oluştu. Detaylar: {e}")
        sys.exit(1)

    # 6. Çıkarım (Inference)
    print("[*] Ses analiz ediliyor...")
    try:
        # Modeli kullanmadan önce işlemciden (processor) geçirerek uygun özellikleri elde edelim.
        # Processor genellikle 1D numpy array veya tensor bekler
        audio_1d = audio_tensor.squeeze(0).numpy()
        inputs = processor(audio_1d, sampling_rate=target_sr, return_tensors="pt")
        
        # Input tensor'lerini seçilen cihaza (CPU/CUDA) taşı
        inputs = {key: val.to(device) for key, val in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            
            # Olasılıkları softmax ile hesapla
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            predicted_id = torch.argmax(logits, dim=-1).item()
            confidence = probabilities[0][predicted_id].item() * 100
            
            # Model config içinden label ismini al (Örn: 'spoof', 'bonafide')
            label_str = model.config.id2label[predicted_id].lower()

            # 7. Sonucu Yazdırma
            print("\n--------------------------------------------------")
            if "spoof" in label_str or "fake" in label_str:
                print(f"[!] SAHTE SES (Deepfake) - Olasılık: %{confidence:.2f}")
            elif "bonafide" in label_str or "real" in label_str:
                print(f"[*] GERÇEK SES (Bonafide) - Olasılık: %{confidence:.2f}")
            else:
                # Beklenmeyen bir label formatı gelmesi durumunda fallback (Varsayılan olarak 0: Spoof, 1: Bonafide)
                if predicted_id == 0:
                    print(f"[!] SAHTE SES (Deepfake) - Olasılık: %{confidence:.2f} (Etiket: {label_str.upper()})")
                else:
                    print(f"[*] GERÇEK SES (Bonafide) - Olasılık: %{confidence:.2f} (Etiket: {label_str.upper()})")
            print("--------------------------------------------------\n")

    except Exception as e:
        print(f"Hata: Çıkarım (inference) sırasında bir sorun oluştu. Detaylar: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python scamhunter_aasist.py <ses_dosyasi_yolu>")
        print("Örnek: python scamhunter_aasist.py ornek_ses.flac")
        sys.exit(1)
        
    audio_file_path = sys.argv[1]
    analyze_audio(audio_file_path)
