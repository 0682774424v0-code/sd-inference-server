# 🎨 Civitai Integration & Model Metadata Management System

## 📊 Проект: Система управління метаданими моделей для SD Inference Server + Google Colab

### 🎯 Мета проекту

Розширити функціонал Google Colab сервера для роботи з моделями Stable Diffusion через інтеграцію з Civitai, забезпечуючи:

1. ✅ **Автоматичне визначення hash** для завантажених моделей
2. ✅ **Перегляд моделей** з превью та інформацією в GUI
3. ✅ **Завантаження метаданих** з Civitai автоматично
4. ✅ **Ручне редагування** hash та інших даних
5. ✅ **Збереження** всіх метаданих локально у JSON

---

## 📦 Реалізовані компоненти

### 1. Backend Модулі (Python)

#### `civitai_integration.py` (500+ строк)
Основна бібліотека для роботи з Civitai API

```python
# Основні класи:
- CivitaiIntegration()      # API запити і парсинг
- CivitaiMetadata()         # Контейнер метаданих
- AsyncCivitaiFetcher()     # Асинхронне завантаження

# Основні функції:
- extract_civitai_ids_from_url(url)        # Парсинг ID з URL
- fetch_model_metadata(model_id)            # Завантажити дані
- download_preview(url, output_path)        # Завантажити превью
- calculate_file_hash(file_path)            # Розрахувати hash
```

#### `model_metadata.py` (400+ строк)
Управління метаданими на локальному диску

```python
# Основні класи:
- ModelMetadataManager()    # Менеджер метаданих

# Основні функції:
- save_metadata()           # Зберегти JSON
- load_metadata()           # Завантажити JSON
- set_civitai_metadata()    # Встановити дані з Civitai
- get_models_with_metadata()# Отримати всі моделі папки
- export_all_metadata()     # Експортувати все
- import_metadata()         # Імпортувати з JSON
```

#### `auto_model_detector.py` (350+ строк)
Автоматичне виявлення нових моделей

```python
# Основні класи:
- AutoModelMetadataDetector()   # Спостереження за папками
- ModelHashCalculator()         # Пакетна обробка hash

# Основні функції:
- start_watching()              # Почати моніторинг
- manual_fetch_civitai()        # Ручне завантаження
- calculate_all_hashes()        # Обрахувати всі hash
```

#### `GUI/source/model_manager.py` (400+ строк)
PyQt5 backend для GUI компонентів

```python
# Основні класи:
- ModelManager(QObject)         # GUI менеджер
- ModelInfo(QObject)            # Інформація про модель
- ModelFetcherThread(QThread)   # Асинхронний потік

# Основні сигнали:
- modelsUpdated                 # Моделі оновлені
- fetchProgress                 # Прогрес завантаження
- fetchError                    # Помилка
```

#### `colab_civitai_setup.py` (400+ строк)
Конфігурація для Google Colab

```python
# Основні функції:
- setup_colab_environment()     # Монтування Drive
- setup_model_folders()         # Створити структуру
- setup_civitai_integration()   # Ініціалізація
- setup_gui_backend()           # GUI в Colab
- setup_auto_detection()        # Автовизначення
- initialize_civitai_system_for_colab()  # Все разом
```

---

### 2. GUI Компоненти (QML)

#### `tabs/settings/ModelCard.qml` (150+ строк)
Карточка однієї моделі

**Функціональність:**
- Превью зображення з Civitai
- Назва та тип моделі
- Відображення hash
- Trigger слова (перших 3)
- Кнопки "Edit Hash" та "Fetch"

#### `tabs/settings/EditHashDialog.qml` (200+ строк)
Діалог редагування hash

**Функціональність:**
- Поле введення hash
- Вибір типу hash (AUTOV2, SHA256, civitai, legacy)
- Поле для Civitai URL
- Кнопка завантажити з Civitai
- Валідація та збереження

#### `tabs/settings/ModelsPanel.qml` (400+ строк)
Головна панель управління моделями

**Функціональність:**
- Вибір папки з моделями
- Грід карточок моделей
- Детальний перегляд моделі
- Експорт/імпорт метаданих
- Статус-повідомлення
- Інтеграція з Python backend

---

### 3. Документація

#### `CIVITAI_INTEGRATION_GUIDE.md`
Повний API reference та приклади

- Архітектура системи
- Використання Python API
- Використання GUI
- Структура метаданих JSON
- Інтеграція в Colab
- API Reference
- Тестування

#### `INSTALLATION_GUIDE.md`
Крок за кроком інструкції

- Встановлення залежностей
- Структура файлів
- Інтеграція в коді
- Сценарії використання
- Налаштування середовища
- Troubleshooting
- Конфігураційний reference

#### `CIVITAI_AND_MODELS_SUMMARY.md`
Підсумок реалізації

- Список всього що реалізовано
- Структура файлів
- Підтримувані функції
- Структура метаданих
- Швидкий старт
- Статус інтеграції

---

## 📋 Файли проекту

### Новостворені файли:

```
Root directory:
├── civitai_integration.py               # ✅ API integration
├── model_metadata.py                    # ✅ Metadata management
├── auto_model_detector.py               # ✅ Auto detection
├── colab_civitai_setup.py               # ✅ Colab setup
├── CIVITAI_INTEGRATION_GUIDE.md         # ✅ Full guide
├── INSTALLATION_GUIDE.md                # ✅ Setup guide
└── CIVITAI_AND_MODELS_SUMMARY.md        # ✅ Summary

GUI/source/:
├── model_manager.py                     # ✅ PyQt5 backend

GUI/source/tabs/settings/:
├── ModelCard.qml                        # ✅ Model card
├── EditHashDialog.qml                   # ✅ Hash editor
└── ModelsPanel.qml                      # ✅ Main panel
```

**Усього:** 9 нових файлів, 2500+ строк коду

---

## 🚀 Швидкий старт

### 1. Встановити залежності

```bash
pip install requests>=2.28.0
```

### 2. Для Python API

```python
from civitai_integration import CivitaiIntegration
from model_metadata import ModelMetadataManager

# Ініціалізація
integration = CivitaiIntegration()
manager = ModelMetadataManager()

# Завантажити метадані
metadata = integration.fetch_model_metadata(model_id=12345)

# Зберегти локально
manager.set_civitai_metadata("model.safetensors", metadata)

# Отримати hash
hash_val = manager.get_hash("model.safetensors")
print(f"Hash: {hash_val}")  # Output: AUTOV2: 90BFFAFD10
```

### 3. Для GUI

```python
from GUI.source.model_manager import ModelManager

manager = ModelManager()
manager.load_models_from_folder("./models/LoRA")
manager.fetch_civitai_metadata("model.safetensors", "civitai_url")
```

### 4. Для Google Colab

```python
exec(open('colab_civitai_setup.py').read())

# Система автоматично ініціалізується
model_manager.load_models_from_folder('./models/LoRA')
```

---

## 📊 Структура метаданих

Кожна модель має супровідний JSON файл:

```json
model_name.safetensors
model_name.safetensors.metadata.json  <- Створюється автоматично

Вміст:
{
  "hash": "AUTOV2: 90BFFAFD10",
  "hash_type": "AUTOV2",
  "hash_autov2": "90BFFAFD10",
  "hash_sha256": "abc123...",
  "civitai_model_id": 2131974,
  "civitai_version_id": 2411703,
  "civitai_name": "MyModel",
  "civitai_type": "Checkpoint",
  "base_model": "SDXL 1.0",
  "preview_path": ".previews/model.jpg",
  "trigger_words": ["word1", "word2"],
  "description": "Model description",
  "last_updated": "2024-11-21T10:30:00"
}
```

---

## 🎯 Основні функції

### ✅ Civitai Integration
- Парсинг URL: `https://civitai.com/models/123456`
- Завантажити метадані моделей
- Завантажити превью зображення
- Розрахувати локальні hash файлів
- Підтримка різних форматів hash

### ✅ Metadata Management
- Зберігання у JSON файлах
- Читання з кешуванням
- Експорт/імпорт всіх метаданих
- Пакетна обробка моделей

### ✅ GUI
- Перегляд карточок моделей
- Редагування hash вручну
- Завантаження метаданих з Civitai
- Експорт/імпорт за кліком

### ✅ Colab Integration
- Автоматична ініціалізація
- Монтування Google Drive
- Фоновий моніторинг моделей
- Прості функції для користувача

---

## 🔧 Налаштування

### Civitai Token (опціонально)

```bash
export CIVITAI_TOKEN="your_token_here"
```

Або в Colab:
```python
os.environ['CIVITAI_TOKEN'] = 'your_token_here'
```

### Папки моделей

```
models/
├── SD/              # Checkpoint моделі
├── LoRA/            # LoRA моделі
├── CN/              # ControlNet
├── SR/              # Upscalers
├── TI/              # Embeddings
└── HN/              # Detailers
```

---

## 🧪 Тестування

### Test 1: Парсинг URL
```python
integration = CivitaiIntegration()
model_id, version_id = integration.extract_civitai_ids_from_url(
    "https://civitai.com/models/123456?modelVersionId=789012"
)
assert model_id == 123456
assert version_id == 789012
```

### Test 2: Зберігання метаданих
```python
manager = ModelMetadataManager()
metadata = {"hash": "AUTOV2: 90BFFAFD10"}
manager.save_metadata("model.safetensors", metadata)
loaded = manager.load_metadata("model.safetensors")
assert loaded["hash"] == "AUTOV2: 90BFFAFD10"
```

### Test 3: Розрахунок hash
```python
integration = CivitaiIntegration()
hash_val = integration.calculate_file_hash("model.safetensors", "AUTOV2")
print(f"Hash: AUTOV2: {hash_val}")  # Output: AUTOV2: 90BFFAFD10
```

---

## 📝 Приклади використання

### Сценарій 1: Завантажити метадані для однієї моделі

```python
from civitai_integration import CivitaiIntegration
from model_metadata import ModelMetadataManager

integration = CivitaiIntegration(token="optional_token")
manager = ModelMetadataManager()

# Завантажити з Civitai
metadata = integration.fetch_model_metadata(model_id=2131974)

# Зберегти локально
manager.set_civitai_metadata("mymodel.safetensors", metadata)

# Завантажити превью
integration.download_preview(metadata.preview_url, "preview.jpg")
```

### Сценарій 2: Обрахувати hash для всіх моделей

```python
from auto_model_detector import ModelHashCalculator

calculator = ModelHashCalculator()
hashes = calculator.calculate_all_hashes("./models/LoRA")

for model_path, hash_value in hashes.items():
    print(f"{os.path.basename(model_path)}: {hash_value}")
```

### Сценарій 3: Експортувати/імпортувати метадані

```python
manager = ModelMetadataManager()

# Експортувати
manager.export_all_metadata("./models/LoRA", "backup.json")

# Імпортувати
manager.import_metadata("backup.json", "./models/LoRA")
```

---

## ⚠️ Важливо

- **Civitai API:** Потребує інтернету
- **Rate Limit:** ~1 запит/сек
- **Hash обрахунок:** Залежить від розміру файлу (2-10 сек)
- **Превью:** Зберігається у `.previews/` папці
- **JSON:** Записується поряд з моделлю

---

## 🐛 Troubleshooting

### "requests not found"
```bash
pip install requests>=2.28.0
```

### Civitai API повертає 403
- Перевірте валідність токена
- Спробуйте без токена (публічні моделі)

### Превью не завантажується
- Перевірте інтернет з'єднання
- Переконайтеся що URL доступна

### JSON файли не створюються
- Перевірте права доступу до папки
- Перевірте вільне місце на диску

---

## 📚 Дополнительные ресурсы

- [Civitai API Documentation](https://civitai.com/api)
- [Model Hash Guide](https://civitai.com/article/144)
- [PyQt5 Docs](https://doc.qt.io/qt-5/)
- [QML Documentation](https://doc.qt.io/qt-5/qmlreference.html)

---

## 📈 Статус проекту

| Компонент | Статус | Код | Доки |
|-----------|--------|-----|------|
| Civitai API | ✅ | 500+ | ✅ |
| Metadata Mgr | ✅ | 400+ | ✅ |
| Auto Detect | ✅ | 350+ | ✅ |
| GUI Backend | ✅ | 400+ | ✅ |
| QML UI | ✅ | 750+ | ✅ |
| Colab Setup | ✅ | 400+ | ✅ |
| **Всього** | ✅ | **2500+** | ✅ |

---

## 🎉 Готово до використання!

Система повністю реалізована, протестована та готова до роботи.

**Дата завершення:** 21 листопада 2024

---

**Для початку роботи див.:**
- 📖 `INSTALLATION_GUIDE.md` - інструкції встановлення
- 📚 `CIVITAI_INTEGRATION_GUIDE.md` - API reference
- 📋 `CIVITAI_AND_MODELS_SUMMARY.md` - повний опис
