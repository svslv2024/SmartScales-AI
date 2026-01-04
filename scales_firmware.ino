/*
 * Прошивка для весов на базе Arduino Mini и HX711
 * Передает данные о весе в последовательный порт (Serial)
 */

#include <HX711_ADC.h> // Библиотека для работы с весами
#include <EEPROM.h>

const int DT_PIN = 4;  // Пин данных HX711
const int SCK_PIN = 5; // Пин синхронизации HX711

HX711_ADC LoadCell(DT_PIN, SCK_PIN);

void setup() {
  Serial.begin(57600); // Инициализация связи с ПК
  LoadCell.begin();
  
  float calibrationValue = 220.5; // ТВОЁ калибровочное число
  
  // Инициализация датчика с прогревом 2 секунды и обнулением (Тара)
  LoadCell.start(2000, true);
  LoadCell.setCalFactor(calibrationValue);
}

void loop() {
  static boolean newDataReady = 0;
  
  // Проверяем, есть ли новые данные от АЦП HX711
  if (LoadCell.update()) newDataReady = true;

  if (newDataReady) {
    static unsigned long lastTime = 0;
    // Отправляем вес в компьютер раз в 200 мс (5 Гц)
    if (millis() - lastTime > 200) {
      float w = LoadCell.getData();
      Serial.println(w); // Отправляем значение веса новой строкой
      lastTime = millis();
      newDataReady = false;
    }
  }

  // Слушаем команды от ПК (например, 't' для обнуления)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 't') LoadCell.tareNoDelay();
  }
}
