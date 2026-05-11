"""
BMW E60 V10 ovozini freesound.org yoki boshqa manbadan yuklab olish uchun
yordam dasturi.

Ishlatish:
    python download_sound.py

Agar avtomatik yuklab olmasa, quyidagi manbalardan qo'lda yuklab oling:
- https://freesound.org (qidirish: "car exhaust acceleration")
- https://soundsnap.com (qidirish: "BMW engine")
- YouTube dan mp3 converter orqali

Yuklab olingan faylni "e60_sound.mp3" deb nomlang va
wind_tunnel/ papkasiga qo'ying.
"""

import urllib.request
import os

# Ochiq litsenziyali mashina dvigatel ovozi (freesound.org)
# Bu yerda freesound.org dan ochiq litsenziyali mashina ovozi
SOUND_URLS = [
    # Freesound - ochiq litsenziyali sport mashina ovozi
    "https://freesound.org/data/previews/682/682783_5674468-lq.mp3",
    # Fallback - yana bir variant
    "https://freesound.org/data/previews/411/411089_5121236-lq.mp3",
]

OUTPUT_FILE = "e60_sound.mp3"

def download_sound():
    if os.path.exists(OUTPUT_FILE):
        print(f"[OK] {OUTPUT_FILE} allaqachon mavjud.")
        return True

    for url in SOUND_URLS:
        try:
            print(f"Yuklab olinmoqda: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                data = response.read()
                with open(OUTPUT_FILE, 'wb') as f:
                    f.write(data)
            print(f"[OK] Ovoz saqlandi: {OUTPUT_FILE} ({len(data)//1024} KB)")
            return True
        except Exception as e:
            print(f"[XATO] {url}: {e}")
            continue

    print("\n[OGOHLANTIRISH] Ovoz yuklab olinmadi.")
    print("Qo'lda yuklab olish uchun:")
    print("  1. https://freesound.org ga kiring")
    print("  2. 'car exhaust acceleration' deb qidiring")
    print("  3. MP3 formatda yuklab oling")
    print("  4. 'e60_sound.mp3' deb nomlang va wind_tunnel/ papkasiga qo'ying")
    return False

if __name__ == "__main__":
    download_sound()
