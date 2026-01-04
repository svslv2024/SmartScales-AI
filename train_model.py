from ultralytics import YOLO

# Загружаем уже обученную модель
model = YOLO('yolov8n.pt') 

# Запускаем дообучение
# data - путь к файлу data.yaml, который ты создал
# epochs - количество проходов обучения (начни с 20-30)
# img_size - размер изображений для обучения (640 - хороший старт)
results = model.train(data='smart_scales_dataset/data.yaml', epochs=30, imgsz=640, device='0') 

# Сохранится новая модель в папке runs/detect/trainX/weights/best.pt
# Её ты будешь использовать в основном скрипте вместо yolov8n.pt
