# 🛡️ Deepfake Detection System

Bu proje, görüntü ve videolardaki "Deepfake" (sahte yüz) manipülasyonlarını tespit etmek için geliştirilmiş yapay zeka destekli bir web uygulamasıdır. Proje, yapay zekanın sadece "Gerçek" veya "Sahte" demekle kalmayıp *neden* bu kararı verdiğini kullanıcıya şeffaf bir şekilde sunabilmesi için **Açıklanabilir Yapay Zeka (Explainable AI - XAI)** teknikleriyle donatılmıştır.

## 🌟 Özellikler

- **Çoklu Format Desteği:** Hem resimler (`.jpg`, `.jpeg`, `.png`) hem de videolar (`.mp4`, `.mov`, `.avi`) üzerinden otomatik analiz.
- **Canlı Kamera Testi:** Doğrudan bilgisayarınızın kamerasını kullanarak anlık "Deepfake" testi yapabilme.
- **Gelişmiş Yüz Tespiti (MTCNN):** Yüklenen medyalardaki yüzleri otomatik olarak kırpar ve sadece doğru hedefe odaklanır.
- **Açıklanabilir Yapay Zeka (XAI) Modülleri:**
  - **🔥 Grad-CAM:** Yapay zekanın, manipülasyon kararı verirken yüzün tam olarak hangi bölgelerine odaklandığını gösteren ısı haritaları üretir.
  - **🧩 LIME:** Görseli küçük parçalara (süper pikseller) bölerek hangi parçaların sonucu "Gerçek" veya "Sahte" yapmaya daha çok katkı sağladığını gösterir.
- **Modern Arayüz:** Gradio tabanlı, etkileşimli, koyu temalı (Galactic Theme) ve son derece kullanımı kolay web paneli.

## 🛠️ Kullanılan Teknolojiler

- **Derin Öğrenme:** PyTorch, PyTorch Lightning
- **Yüz Algılama:** Facenet-PyTorch (MTCNN)
- **Web Arayüzü:** Gradio
- **XAI Yöntemleri:** Lime, Grad-CAM (Özel implementasyon)
- **Veri İşleme:** OpenCV, Pillow, NumPy (`<2.0`)

---

## 🚀 Kurulum ve Çalıştırma

Aşağıdaki adımları takip ederek projeyi kendi bilgisayarınızda kolayca ayağa kaldırabilirsiniz.

### 1. Gereksinimlerin Kurulması
Projenin ana klasöründe bir terminal/komut satırı açın ve aşağıdaki komutla tüm gerekli kütüphaneleri indirin:

```bash
pip install -r requirements.txt
```
*(PyTorch modüllerinin çökmemesi için Numpy sürümü bilinçli olarak `1.x` seviyesinde tutulmuştur.)*

### 2. Model Dosyasının Kontrolü
Sistemin çalışabilmesi için eğitilmiş yapay zeka ağırlıklarına ihtiyacı vardır. `models/` klasörünün altında `best_model-v3.pth` (veya `best_model.pth` vb.) adlı model dosyanızın bulunduğundan emin olun.

### 3. Uygulamanın Başlatılması
Gerekli kurulumları yaptıktan sonra web arayüzünü çalıştırmak için şu komutu girin:

```bash
python web-app.py
```

Terminalde uygulamanın başlatıldığını gösteren `http://127.0.0.1:7860` benzeri bir adres belirecektir. Bu linke tıklayarak veya tarayıcınıza yapıştırarak sisteme giriş yapabilirsiniz.

---

## 📂 Proje Dizin Yapısı

- **`web-app.py`** : Gradio arayüzünü ayağa kaldıran, dosya/kamera işlemlerini ve ana analiz boru hattını (pipeline) yöneten ana dosya.
- **`xai.py`** : Sistemin "Açıklanabilir Yapay Zeka" yeteneklerini sağlayan (Grad-CAM vb.) fonksiyonları içerir.
- **`requirements.txt`** : Gerekli paketlerin listesi.
- **`models/`** : Yapay zekanın daha önceden öğrenmiş olduğu derin öğrenme ağırlıklarının (`.pth`) barındırıldığı dizin.
- **`scratch.py`** : Geliştirme sürecinde kullanılan test ve deneme betiği.

---

### Nasıl Kullanılır?
1. Tarayıcıda açılan sayfaya girin.
2. Sol taraftaki alana test etmek istediğiniz videoyu veya resmi yükleyin, ya da **kameradan anlık çekim** yapın.
3. **🔍 Analyze** butonuna basın.
4. Sistem, analiz sonuçlarını saniyeler içinde sekmeler halinde size sunacaktır (Sonuç, Grad-CAM Haritası, LIME Haritası vb.).

🛡️ *Bu araç, siber güvenlik araştırmaları, medya doğrulaması ve eğitim amaçları için tasarlanmıştır.*
