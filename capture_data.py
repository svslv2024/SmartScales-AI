import cv2
import time
import os
import threading # Используем для RTSP

# --- НАСТРОЙКИ ---
RTSP_URL = "rtsp://admin:password@192.168.1.100:554/stream" # Или 0 для USB-камеры
OUTPUT_DIR = "data_collection" # Папка для сохранения фото

# Класс для захвата видео (из основного проекта)
class VideoStreamReader:
    def __init__(self, url):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.frame = None
        self.started = False
        self.read_lock = threading.Lock()

    def start(self):
        self.started = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            if grabbed:
                with self.read_lock: self.frame = frame
            else:
                time.sleep(0.01)

    def get_frame(self):
        with self.read_lock:
            return self.frame.copy() if self.frame is not None else None

def collect_data():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    reader = VideoStreamReader(RTSP_URL).start()
    print(">>> Захват видео запущен. Нажмите 'q' для выхода.")
    print(">>> Нажмите 's' для сохранения фотографии.")

    photo_count = 0
    while True:
        frame = reader.get_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        cv2.imshow("Data Collection - Press 's' to save", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = os.path.join(OUTPUT_DIR, f"image_{time.time():.0f}.jpg")
            cv2.imwrite(filename, frame)
            photo_count += 1
            print(f"Сохранено фото: {filename} (Всего: {photo_count})")
            time.sleep(0.2) # Защита от случайного двойного нажатия

    reader.stop()
    cv2.destroyAllWindows()
    print(f"\n>>> Сбор данных завершен. Всего сохранено: {photo_count} фото.")

if __name__ == "__main__":
    collect_data()
