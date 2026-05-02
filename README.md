# 🛡️ Deepfake Detection & Analysis System

Bu proje, hem görsel (resim ve video) hem de işitsel (ses) medyalardaki "Deepfake" manipülasyonlarını yüksek doğrulukla tespit etmek için geliştirilmiş yapay zeka destekli kapsamlı bir analiz sistemidir. Sistem, sadece "Gerçek" veya "Sahte" sonucunu vermekle kalmayıp kararın *nedenini* **Açıklanabilir Yapay Zeka (XAI - Explainable AI)** teknikleriyle kullanıcıya görsel ve işitsel olarak sunar.

## ✨ Temel Özellikler

- **Görsel Deepfake Tespiti:** Yüz tespit algoritmaları (MTCNN) kullanarak resim (`.jpg`, `.png`) ve videolardaki (`.mp4`, `.avi`) yüz manipülasyonlarını tespit eder.
- **Ses Deepfake Tespiti (AASIST):** Orijinal insan seslerini ve yapay zeka ile üretilmiş (AI-generated) veya klonlanmış sahte sesleri ayırt eden özel ses analizi.
- **Canlı Kamera Analizi:** Web kameranızı kullanarak anlık derin sahte kontrolü yapabilme imkanı.
- **Açıklanabilir Yapay Zeka (XAI) Entegrasyonu:**
  - **🔥 Grad-CAM:** Görsel manipülasyon tespitinde, modelin yüzün hangi bölgelerine (gözler, dudak çevresi vb.) odaklandığını gösteren ısı haritaları.
  - **🧩 LIME (Görsel):** Görüntüyü süper piksellere ayırarak hangi bölgelerin "Sahte" veya "Gerçek" kararına katkı sağladığını gösteren parçalı analiz.
  - **🎙️ SHAP (Ses):** Ses analizinde spektrogram üzerinden hangi frekans/zaman aralıklarının sahtelik kararına yol açtığını görselleştiren açıklanabilirlik.
- **Kullanıcı Dostu Arayüz:** Gradio tabanlı, modern ve etkileşimli bir kontrol paneli.

## 📂 Proje Yapısı

Daha düzenli ve modüler bir mimariyle geliştirilen projenin güncel klasör yapısı:

```text
Deepfake-Detector/
├── app.py                   # Ana Gradio web arayüzünü başlatan dosya
├── requirements.txt         # Proje bağımlılıkları
├── .gitignore               # Git tarafından takip edilmeyecek dosyalar
├── README.md                # Proje dokümantasyonu
├── audio_samples/           # Test amaçlı örnek ses dosyaları (.flac)
├── core/                    # Çekirdek modeller ve çıkarım (inference) mantığı
│   ├── inference.py         # Görsel Deepfake analiz pipeline'ı
│   ├── inference_audio.py   # İşitsel (Ses) Deepfake analiz pipeline'ı
│   └── model.py             # Model mimarileri
├── ui/                      # Arayüz bileşenleri
│   ├── components.py        # Gradio arayüz parçaları (sekmeler, butonlar)
│   └── theme.py             # Arayüz tema ve CSS ayarları
├── xai.py                   # Görsel Açıklanabilir AI (Grad-CAM, LIME) metodları
├── xai_voice.py             # İşitsel Açıklanabilir AI (SHAP vb.) metodları
├── scamhunter_aasist.py     # Ses deepfake tespiti için AASIST entegrasyonu
├── models/                  # [Eğitilmiş model ağırlıkları (.pth) buraya konur]
└── weights/                 # [Ek model ağırlıkları buraya konur]
```

## 🚀 Kurulum

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları takip edin:

### 1. Depoyu Klonlayın
```bash
git clone https://github.com/kullaniciadi/Deepfake-Detector.git
cd Deepfake-Detector
```

### 2. Sanal Ortam Oluşturun (Önerilen)
```bash
python -m venv .venv
# Windows için:
.venv\Scripts\activate
# macOS/Linux için:
source .venv/bin/activate
```

### 3. Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### 4. Model Ağırlıklarını Ekleyin
Görsel ve ses analizi modellerinin çalışabilmesi için eğitilmiş ağırlık dosyalarına (`.pth`, `.pt` vb.) ihtiyacınız vardır.
Bu dosyaları `models/` klasörü altına yerleştirin. (Büyük boyutlu model ağırlıkları `.gitignore` aracılığıyla Github'a yüklenmez).

## 💻 Kullanım

Tüm kurulumlar tamamlandıktan sonra aşağıdaki komut ile web arayüzünü başlatabilirsiniz:

```bash
python app.py
```

- Terminalde `http://127.0.0.1:7860` şeklinde yerel bir adres belirecektir. Bu linki tarayıcınızda açın.
- Arayüz üzerinden **Resim/Video** veya **Ses** yükleyerek (veya **audio_samples/** klasöründeki test seslerini kullanarak) analizi başlatın.
- "Analyze" (Analiz Et) butonuna basarak hem tespiti hem de XAI (Açıklanabilirlik) sonuçlarını saniyeler içinde görüntüleyin.

## 🛡️ Yasal Uyarı

Bu araç ve kaynak kodları yalnızca siber güvenlik araştırmaları, medya doğrulaması ve eğitim amaçları gözetilerek geliştirilmiştir. Herhangi bir kötüye kullanım durumunda sorumluluk kullanıcıya aittir.
