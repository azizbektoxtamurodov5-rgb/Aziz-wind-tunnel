# Aziz Wind Tunnel — APK Yaratish Qo'llanmasi

## 1-qadam: Kutubxonalarni o'rnatish (Desktop test uchun)

```bash
pip install opencv-python pygame numpy
```

## 2-qadam: BMW ovozini yuklab olish

```bash
cd wind_tunnel
python download_sound.py
```

Agar skript ishlamasa, qo'lda yuklab oling:
- https://freesound.org → "car exhaust acceleration" qidiring
- MP3 formatda yuklab oling
- `e60_sound.mp3` deb nomlang va `wind_tunnel/` papkasiga qo'ying

## 3-qadam: Desktop da test qilish

```bash
cd wind_tunnel
python main.py
```

**Tugmalar:**
- `ESC` — Chiqish
- `SPACE` — Fon o'rganishni yangilash (mashina kirganida bosing)

---

## APK yaratish

### Buildozer o'rnatish (Linux/Ubuntu)

```bash
pip install buildozer
pip install cython

# Android SDK/NDK uchun kerakli tizim paketlari
sudo apt-get update
sudo apt-get install -y \
    git zip unzip openjdk-17-jdk python3-pip \
    autoconf libtool pkg-config zlib1g-dev \
    libncurses5-dev libncursesw5-dev libtinfo5 \
    cmake libffi-dev libssl-dev
```

### Replit Shell orqali APK yaratish

Replit Shell ni oching va quyidagi buyruqlarni kiriting:

```bash
# 1. Kutubxonalar o'rnatish
pip install buildozer cython

# 2. Wind tunnel papkasiga o'tish
cd wind_tunnel

# 3. APK build boshlash (birinchi marta 30-60 daqiqa ketadi)
buildozer android debug

# 4. APK tayyor bo'lgach bu yerda bo'ladi:
# wind_tunnel/bin/azizwindtunnel-1.0-arm64-v8a_armeabi-v7a-debug.apk
```

### APK ni telefoningizga o'tkazish

```bash
# USB orqali (ADB)
adb install bin/azizwindtunnel-*.apk

# Yoki bin/ papkasidan faylni yuklab oling
```

---

## Muammo hal qilish

**Kamera ko'rinmasa:**
- `SPACE` bosing — fon o'rganishni yangilaydi
- Kamerani yaxshi yoritilgan joyga oling

**Zarralar to'g'ri burilmasa:**
- Mashina ekran o'rtasida bo'lishi kerak
- Kontrastli fon (oq devor) foydalaning

**Build xatosi:**
```bash
buildozer android debug 2>&1 | tee build_log.txt
```
Xato haqida: build_log.txt faylini tekshiring.

---

## Texnik ma'lumotlar

| Xususiyat | Qiymat |
|-----------|--------|
| Min Android | API 26 (Android 8.0) |
| Arxitektura | ARM64 + ARM32 |
| Kamera | Orqa va old |
| Ovoz | MP3 loop |
| Zarralar | 220 ta |
| FPS maqsad | 30 |
