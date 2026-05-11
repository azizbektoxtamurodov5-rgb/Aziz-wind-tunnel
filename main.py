"""
Aziz Real-time Virtual Wind Tunnel
Desktop: opencv + pygame + numpy
Android: pygame.camera + PIL (numpy yo'q)
"""

import pygame
import sys
import random
import os
import time

try:
    import android
    IS_ANDROID = True
except ImportError:
    IS_ANDROID = False

if not IS_ANDROID:
    try:
        cv2 = __import__('cv2')
        np = __import__('numpy')
        HAS_CV2 = True
    except ImportError:
        cv2 = None
        np = None
        HAS_CV2 = False
else:
    cv2 = None
    np = None
    HAS_CV2 = False

# ─── Sozlamalar ───────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1280, 720
FPS = 30
PARTICLE_COUNT = 180
P_SPEED_MIN = 4
P_SPEED_MAX = 9
WIND_COLOR      = (80, 160, 255)
WIND_COLOR_FAST = (180, 220, 255)
SOUND_FILE = "e60_sound.mp3"


# ─── Particle ────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x  = random.uniform(-40, 0)
        self.y  = random.uniform(0, HEIGHT)
        self.vx = random.uniform(P_SPEED_MIN, P_SPEED_MAX)
        self.vy = random.uniform(-0.3, 0.3)
        self.length = random.randint(12, 35)
        t = (self.vx - P_SPEED_MIN) / (P_SPEED_MAX - P_SPEED_MIN)
        self.color = (
            int(WIND_COLOR[0] + (WIND_COLOR_FAST[0]-WIND_COLOR[0])*t),
            int(WIND_COLOR[1] + (WIND_COLOR_FAST[1]-WIND_COLOR[1])*t),
            int(WIND_COLOR[2] + (WIND_COLOR_FAST[2]-WIND_COLOR[2])*t),
        )
        self.deflect = 0.0

    # car_mask: bytearray, WIDTH*HEIGHT, >0 = mashina pikseli
    def update(self, car_mask):
        ahead = int(self.vx * 5)
        cx = int(self.x) + ahead
        cy = int(self.y)
        if 0 <= cx < WIDTH and 0 <= cy < HEIGHT:
            if car_mask[cy * WIDTH + cx] > 0:
                self.deflect = min(self.deflect + 0.5, 6.0)
                if self.y < HEIGHT // 2:
                    self.vy -= self.deflect * 0.14
                else:
                    self.vy += self.deflect * 0.14
            else:
                self.deflect = max(0.0, self.deflect - 0.25)
                self.vy *= 0.93
        self.vy = max(-14, min(14, self.vy))
        self.x += self.vx
        self.y += self.vy
        if self.x > WIDTH + 20 or self.y < -10 or self.y > HEIGHT + 10:
            self.reset()

    def draw(self, surface):
        x1 = max(0, min(WIDTH-1,  int(self.x)))
        y1 = max(0, min(HEIGHT-1, int(self.y)))
        x2 = max(0, min(WIDTH-1,  int(self.x - self.vx*3)))
        y2 = max(0, min(HEIGHT-1, int(self.y - self.vy*3)))
        pygame.draw.line(surface, self.color, (x1,y1), (x2,y2), 2)


# ─── Desktop kamera (OpenCV + numpy) ─────────────────────────────────────────
class DesktopCamera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.bg = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=40, detectShadows=False)

    def get_frame_and_mask(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, None
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        if w != WIDTH or h != HEIGHT:
            frame = cv2.resize(frame, (WIDTH, HEIGHT))

        fg = self.bg.apply(frame, learningRate=0.005)
        k  = np.ones((5,5), np.uint8)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN,  k)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, k)
        fg = cv2.dilate(fg, k, iterations=3)

        blurred = cv2.GaussianBlur(frame, (25,25), 0)
        dark    = (blurred * 0.1).astype(np.uint8)
        soft    = cv2.GaussianBlur(cv2.dilate(fg, np.ones((15,15),np.uint8), iterations=2), (21,21), 0)
        m3 = np.stack([soft,soft,soft], axis=2).astype(np.float32)/255.0
        result = (frame.astype(np.float32)*m3 + dark.astype(np.float32)*(1-m3)).astype(np.uint8)

        rgb  = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        surf = pygame.surfarray.make_surface(np.transpose(rgb,(1,0,2)))

        # Düz bytearray maska
        mask_flat = bytearray(fg.flatten().tolist())
        return surf, mask_flat

    def reset_bg(self):
        self.bg = cv2.createBackgroundSubtractorMOG2(
            history=300, varThreshold=40, detectShadows=False)

    def release(self):
        self.cap.release()


# ─── Android kamera (pygame.camera + PIL — numpy yo'q!) ──────────────────────
class AndroidCamera:
    def __init__(self):
        pygame.camera.init()
        cams = pygame.camera.list_cameras()
        cam_id = cams[0] if cams else "/dev/video0"
        self.cam = pygame.camera.Camera(cam_id, (WIDTH, HEIGHT))
        self.cam.start()
        self.prev_gray = None       # list of ints, WIDTH*HEIGHT

    def _surface_to_gray(self, surf):
        """Pygame surface → grayscale list, hech qanday numpy ishlatmasdan"""
        # pygame.transform.grayscale PIL o'rniga
        gray_surf = pygame.transform.grayscale(surf)
        # pygame.PixelArray orqali piksel qiymatlari
        pa = pygame.PixelArray(gray_surf)
        gray = []
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Kulrang kanal (RGB da R=G=B)
                c = gray_surf.unmap_rgb(pa[x, y])
                gray.append(c[0])
        del pa
        return gray

    def get_frame_and_mask(self):
        if not self.cam.query_image():
            return None, None

        surf = self.cam.get_image()

        # Grayscale
        gray = self._surface_to_gray(surf)

        # Harakat maskasi
        if self.prev_gray is None:
            self.prev_gray = gray
            mask_flat = bytearray(WIDTH * HEIGHT)
        else:
            mask_flat = bytearray(WIDTH * HEIGHT)
            for i in range(len(gray)):
                diff = abs(int(gray[i]) - int(self.prev_gray[i]))
                mask_flat[i] = 255 if diff > 20 else 0
            self.prev_gray = gray

        # Fon qoraytirish: maskalanmagan piksellarni qoraytirish
        result = surf.copy()
        for y in range(0, HEIGHT, 2):       # tezlik uchun 2 qadam
            for x in range(0, WIDTH, 2):
                if mask_flat[y * WIDTH + x] == 0:
                    c = surf.get_at((x, y))
                    dark = (int(c[0]*0.1), int(c[1]*0.1), int(c[2]*0.1))
                    result.set_at((x, y), dark)

        return result, mask_flat

    def reset_bg(self):
        self.prev_gray = None

    def release(self):
        self.cam.stop()


# ─── UI ──────────────────────────────────────────────────────────────────────
def draw_ui(screen, font, font_sm, sound_ok, fps_val):
    screen.blit(font.render("AZIZ VIRTUAL WIND TUNNEL", True, (80,180,255)), (20,14))
    screen.blit(font_sm.render(f"FPS: {fps_val:.0f}   Zarralar: {PARTICLE_COUNT}", True, (150,200,255)), (20,52))
    color = (100,255,100) if sound_ok else (255,100,100)
    screen.blit(font_sm.render("BMW E60 V10: ON" if sound_ok else "e60_sound.mp3 topilmadi", True, color), (20,74))
    screen.blit(font_sm.render("SPACE — yangilash  |  ESC — chiqish", True, (90,90,140)), (20,HEIGHT-32))
    screen.blit(font_sm.render("SHAMOL ►", True, (80,140,255)), (8, HEIGHT//2-8))


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

    flags = pygame.FULLSCREEN if IS_ANDROID else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("Aziz Wind Tunnel")
    clock  = pygame.time.Clock()

    try:
        font    = pygame.font.SysFont("Arial", 26, bold=True)
        font_sm = pygame.font.SysFont("Arial", 18)
    except:
        font    = pygame.font.Font(None, 30)
        font_sm = pygame.font.Font(None, 22)

    # Ovoz
    sound_ok = False
    volume   = 0.0
    if os.path.exists(SOUND_FILE):
        try:
            pygame.mixer.music.load(SOUND_FILE)
            pygame.mixer.music.set_volume(0.0)
            pygame.mixer.music.play(-1)
            sound_ok = True
        except Exception as e:
            print("[Ovoz xato]", e)

    # Kamera
    try:
        cam = AndroidCamera() if (IS_ANDROID or not HAS_CV2) else DesktopCamera()
        print("[OK] Kamera ulandi")
    except Exception as e:
        print("[XATO] Kamera:", e)
        pygame.quit()
        sys.exit(1)

    particles = [Particle() for _ in range(PARTICLE_COUNT)]
    car_mask  = bytearray(WIDTH * HEIGHT)
    fps_display = FPS
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    cam.reset_bg()
            if IS_ANDROID and event.type == pygame.FINGERDOWN:
                cam.reset_bg()

        frame_surf, new_mask = cam.get_frame_and_mask()
        if frame_surf is not None:
            screen.blit(frame_surf, (0, 0))
            if new_mask is not None:
                car_mask = new_mask
        else:
            screen.fill((10, 10, 10))

        for p in particles:
            p.update(car_mask)
            p.draw(screen)

        draw_ui(screen, font, font_sm, sound_ok, fps_display)

        if sound_ok and volume < 1.0:
            volume = min(1.0, volume + 0.004)
            pygame.mixer.music.set_volume(volume)

        pygame.display.flip()
        clock.tick(FPS)
        fps_display = clock.get_fps()

    cam.release()
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
