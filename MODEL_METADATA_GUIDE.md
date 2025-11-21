# Model Metadata & Preview System

## Огляд
Ця система дозволяє:
- ✅ **Додавати хеші моделей** (AUTOV2, SHA256, CRC32, BLAKE3, AUTOV3) - як у Civitai
- ✅ **Відображати превьюші (обкладинки) моделей** у GUI в розділі "Models"
- ✅ **Показувати детальну інформацію** про моделі (LoRA, Checkpoint, Upscaler)
- ✅ **Зберігати метадані** у PNG файлах картинок при генерації
- ✅ **Витягувати слова-тригери для LoRA**

---

## Файли, що були додані/змінені

### 1. **model_metadata.py** (НОВИЙ)
Основний модуль для роботи з метаданими:
- `calculate_model_hash(file_path, algorithm)` - обчислює хеш за вибраним алгоритмом
- `get_all_model_hashes(file_path)` - отримує всі 5 типів хешів
- `ModelMetadataManager` - клас для управління метаданими моделей
- `extract_lora_trigger_words(model_path)` - витягує слова-тригери
- `get_model_preview_path(model_path)` - знаходить превьюш моделі
- `format_hashes_for_metadata(hashes)` - форматує хеші у стиль Civitai

### 2. **wrapper.py** (ЗМІНЕНО)
Додано підтримку хешів до метаданих:
```python
# Імпорт нового модуля
import model_metadata

# Нові методи класу GenerationParameters:
def get_model_hash(self, model_path)  # Отримує хеш моделі (AUTOV2)

# У функції get_metadata() додано:
- model_hash (для однієї моделі)
- UNET_hash, CLIP_hash, VAE_hash (для розділених моделей)
- lora_hashes (для всіх підключених LoRA)
```

### 3. **GUI/source/model_preview.py** (НОВИЙ)
GUI компонент для управління превьюшами:
- `ModelPreviewProvider` - провайдер превьюшів моделей
- `ModelInfoFormatter` - форматування інформації про моделі
- Сканування директорій моделей
- Управління метаданими через GUI

### 4. **GUI/source/tabs/settings/ModelCard.qml** (НОВИЙ)
QML компонент - карточка однієї моделі:
-显ує превьюш/обкладинку
- Показує назву моделі
- Виводить тип моделі (LoRA, Model, SR, CN)
- Показує хеш (AUTOV2)
- Виводить розмір файлу

### 5. **GUI/source/tabs/settings/ModelsPanel.qml** (НОВИЙ)
QML компонент - панель зі всіма моделями:
- Вибір типу моделей (LORA, CHECKPOINT, UPSCALER, CONTROLNET)
- Сітка з карточками моделей
- Кнопка оновлення/сканування
- Лічильник моделей

### 6. **GUI/source/tabs/settings/ModelDetailsDialog.qml** (НОВИЙ)
QML вікно - детальна інформація про модель:
- Превьюш
- Назва, тип, розмір
- **Усі 5 типів хешів** (AUTOV2, SHA256, CRC32, BLAKE3, AUTOV3)
- Слова-тригери (для LoRA)
- Опис
- Автор

---

## Як це працює

### 1. Генерація картинки з хешами

При генерації картинки метадані тепер включають:
```
model_hash: 90BFFAFD10
UNET_hash: cab478b74a
CLIP_hash: d4f7b91e8c
VAE_hash: 735e4c3a9f
lora_hashes: "AvariceV1.1: 77fa6414d4fe, Kerfus-Illustrious: 23fbc4a6fcd6"
```

Ці хеші **зберігаються в PNG файлі** як метадані, як це робить Civitai.

### 2. Функція calculate_model_hash()

```python
# Отримати хеш у форматі AUTOV2 (8 символів)
hash_autov2 = calculate_model_hash("path/to/model.safetensors", "autov2")
# Результат: 90BFFAFD10

# Отримати SHA256 (64 символи)
hash_sha256 = calculate_model_hash("path/to/model.safetensors", "sha256")
# Результат: 90BFFAFD10DC1A17528C1DAAB0FC5C8D21BE959FB5081AC9A285180EE6F9C30B

# Отримати всі хеші
all_hashes = get_all_model_hashes("path/to/model.safetensors")
# Результат: {
#   "autov2": "90BFFAFD10",
#   "sha256": "90BFFAFD10DC1A17528C1DAAB0FC5C8D21BE959FB...",
#   "crc32": "B7A9E45A",
#   "blake3": "BAA4F21ECD392A53B8F7984722C005452D1A1F9F...",
#   "autov3": "6BA97B773590"
# }
```

### 3. GUI Панель Моделей

Користувач може:
1. Перейти на вкладку "Settings" → "Models"
2. Вибрати тип моделей (LoRA, Checkpoint, Upscaler, ControlNet)
3. Бачити сітку з карточками моделей
4. Кожна карточка показує:
   - **Превьюш** (якщо є png/jpg з тим же іменем)
   - Назву моделі
   - Тип (LoRA, Model, SR, CN)
   - Хеш (AUTOV2)
   - Розмір файлу
5. Клікнути на карточку → Побачити всі деталі:
   - Всі 5 хешів
   - Слова-тригери (для LoRA)
   - Опис, автор, базова модель

### 4. Структура для зберігання метаданих

Метадані зберігаються у файлі `.models_metadata.json` у папці models:
```json
{
  "LoRA/AvariceV1.1.safetensors": {
    "name": "Avariance V1.1",
    "description": "High quality LoRA for...",
    "author": "Author Name",
    "base_model": "Illustrious",
    "trigger_words": ["avariance", "wealth", "gold"],
    "hashes": {
      "autov2": "90BFFAFD10",
      "sha256": "90BFFAFD10DC1A17...",
      "crc32": "B7A9E45A",
      "blake3": "BAA4F21ECD392A53...",
      "autov3": "6BA97B773590"
    },
    "preview": "LoRA/AvariceV1.1.preview.png",
    "updated": "2025-11-21T10:30:00"
  }
}
```

---

## Структура файлів моделей

Для правильної роботи перевьюшів файли повинні бути розташовані так:

```
models/
├── LoRA/
│   ├── ModelName.safetensors
│   ├── ModelName.preview.png         ← Превьюш
│   ├── ModelName.txt                 ← Слова-тригери (опціонально)
│   └── ...
├── Stable-diffusion/
│   ├── checkpoint_model.safetensors
│   ├── checkpoint_model.png          ← Превьюш
│   └── ...
├── SR/
│   ├── upscaler_model.safetensors
│   ├── upscaler_model.preview.png    ← Превьюш
│   └── ...
└── CN/
    ├── controlnet_model.safetensors
    ├── controlnet_model.png          ← Превьюш
    └── ...
```

**Імена файлів превьюшів:**
- `ModelName.preview.png`
- `ModelName.png`
- `ModelName.jpg`
- `ModelName.jpeg`
- `ModelName_preview.png`

**Формат файлу слів-тригерів (.txt):**
```
trigger_word1, trigger_word2, trigger_word3
```

---

## Інтеграція з Civitai

Формат метаданих тепер сумісний з Civitai:

**Приклад PNG метаданих після генерації:**
```
mode: txt2img
width: 832
height: 1216
prompt: masterpiece, best quality, absurdres
negative_prompt: worst quality, low quality
seed: 1486243165
steps: 24
scale: 3.5
sampler: DPM2 a
model: novaFurryXL_illustrious
model_hash: cab478b74a
lora_hashes: "AvariceV1.1: 77fa6414d4fe, Kerfus-Illustrious: 23fbc4a6fcd6"
```

---

## Використання у коді

### Python

```python
from model_metadata import calculate_model_hash, get_all_model_hashes

# Отримати хеш однієї моделі
hash_val = calculate_model_hash("/path/to/model.safetensors", "autov2")

# Отримати всі хеші
all_hashes = get_all_model_hashes("/path/to/model.safetensors")

# Форматувати хеші як у Civitai
from model_metadata import format_hashes_for_metadata
formatted = format_hashes_for_metadata(all_hashes)
# Результат: "AUTOV2: 90BFFAFD10, SHA256: 90BFFAFD10DC1A17..., ..."
```

### QML/GUI

```qml
import "model_preview.py" as ModelPreview

// Використання в QML
ModelsPanel {
    modelProvider: MODEL_PREVIEW_PROVIDER  // Глобальна змінна
    selectedModelType: "LORA"
}
```

---

## Можливості розширення

1. **Завантаження превьюшів з Civitai** - автоматичне завантаження обкладинок
2. **Сортування та фільтрація** - по розміру, даті, популярності
3. **Тегування моделей** - пошук за тегами
4. **Порівняння хешів** - перевірка цілісності моделей
5. **Синхронізація метаданих** - з Civitai/HuggingFace
6. **Експорт каталогу моделей** - як HTML/JSON звіту

---

## Налагодження

Якщо превьюші не показуються:
1. Переконайтеся, що файл превьюшу має правильне ім'я
2. Клікніть кнопку "Refresh" у панелі моделей
3. Перевірте, що файл PNG/JPG існує в тій же папці що модель

---

## Вимоги

- Python 3.7+
- PIL/Pillow (для роботи з PNG/JPG)
- PyQt5 (для GUI)
- Опціонально: `blake3` пакет для хешування BLAKE3

Встановлення blake3 (опціонально):
```bash
pip install blake3
```

---

## Версія
**1.0.0** - Перша версія з підтримкою хешів та превьюшів моделей
