"""
Smart Scales AI - Главный модуль управления
"""
import cv2
import serial
import threading
import pyttsx3
import numpy as np
from ultralytics import YOLO

# Настройки системы
CAMERA_ID = 0           # Индекс веб-камеры Logitech C920
PORT = 'COM3'           # Порт Arduino
BAUD = 57600            # Скорость порта
MODEL_PATH = 'yolov8n.pt' # Путь к файлу нейросети

# База данных: Ключ ИИ -> (Название, Цена за 1 кг)
PRODUCTS = {
    'potato': ("Картофель", 40),
    'carrot': ("Морковь", 50),
    'apple': ("Яблоко", 100)
}

# Инициализация голоса (озвучка работает в фоне)
voice = pyttsx3.init()
def say(text):
    def run():
        voice.say(text)
        voice.runAndWait()
    threading.Thread(target=run, daemon=True).start()

def create_label(name, weight, total):
    """Создает графический файл чека"""
    img = np.ones((300, 400, 3), dtype=np.uint8) * 255
    cv2.putText(img, f"Product: {name}", (20, 50), 1, 1.5, (0,0,0), 2)
    cv2.putText(img, f"Weight: {weight}g", (20, 100), 1, 1.5, (0,0,0), 2)
    cv2.putText(img, f"Total: {total:.2f} RUB", (20, 200), 1, 2, (0,0,255), 3)
    cv2.imwrite("last_receipt.png", img)

def main():
    # Инициализация ИИ и камеры
    model = YOLO(MODEL_PATH)
    cap = cv2.VideoCapture(CAMERA_ID)
    
    # Инициализация Serial порта (с обработкой ошибки подключения)
    try:
        ser = serial.Serial(PORT, BAUD, timeout=0.1)
    except:
        ser = None
        print("Внимание: Весы не подключены (режим симуляции)")

    current_weight = 0.0

    while True:
        ret, frame = cap.read()
        if not ret: break

        # Читаем данные с Arduino
        if ser and ser.in_waiting:
            try:
                line = ser.readline().decode().strip()
                current_weight = float(line) if float(line) > 5 else 0
            except: pass

        # Запуск распознавания
        results = model(frame, verbose=False)[0]
        detected_names = []

        for box in results.boxes:
            label = model.names[int(box.cls[0])]
            if label in PRODUCTS:
                detected_names.append(label)
                # Рисуем рамку
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Отрисовка меню выбора на экране
        options = list(set(detected_names))[:3]
        cv2.putText(frame, f"Weight: {current_weight} g", (10, 50), 1, 2, (0, 255, 0), 2)
        for i, opt in enumerate(options):
            cv2.putText(frame, f"[{i+1}] {PRODUCTS[opt][0]}", (10, 100 + i*40), 1, 1.5, (255, 255, 255), 2)

        cv2.imshow("Smart Scales System", frame)

        # Управление кнопками
        key = cv2.waitKey(1)
        if key == ord('q'): break # Выход
        if key == ord('t') and ser: ser.write(b't') # Сброс веса
        
        # Нажатие 1, 2 или 3 для выбора товара
        if key in [ord('1'), ord('2'), ord('3')]:
            idx = int(chr(key)) - 1
            if idx < len(options):
                key_name = options[idx]
                p_name, p_price = PRODUCTS[key_name]
                total = (current_weight / 1000) * p_price
                
                say(f"Выбрано {p_name}. Итого {int(total)} рублей.")
                create_label(p_name, current_weight, total)
                print(f"Чек создан: {p_name} - {total} RUB")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
