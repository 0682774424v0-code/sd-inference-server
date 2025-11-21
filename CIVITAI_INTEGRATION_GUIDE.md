# Civitai Integration & Model Metadata Management

## Overview

Це розширення дозволяє інтегрувати Civitai API для автоматичного отримання метаданих моделей, включаючи:
- **Hash моделей** (AUTOV2, SHA256, civitai format)
- **Превью зображення** з Civitai
- **Інформацію про модель** (тип, параметри, trigger слова)
- **Ручне редагування** метаданих через GUI

## Архітектура

### Основні компоненти:

```
civitai_integration.py      # Бібліотека для роботи з Civitai API
├── CivitaiIntegration      # Основний клас для запитів
├── CivitaiMetadata         # Контейнер метаданих
└── AsyncCivitaiFetcher     # Асинхронні запити

model_metadata.py           # Управління метаданими локально
├── ModelMetadataManager    # Зберігання/читання JSON метаданих
└── Утиліти                 # Допоміжні функції

GUI/source/model_manager.py # PyQt5 backend для GUI
├── ModelManager            # Основний менеджер для GUI
├── ModelInfo               # QObject для передачі до QML
└── ModelFetcherThread      # Потік для асинхронного завантаження

GUI/source/tabs/settings/   # QML компоненти
├── ModelCard.qml           # Карточка окремої моделі
├── EditHashDialog.qml      # Діалог редагування hash
└── ModelsPanel.qml         # Основна панель моделей
```

## Використання

### Python API

```python
from civitai_integration import CivitaiIntegration
from model_metadata import ModelMetadataManager

# Ініціалізація
integration = CivitaiIntegration(token="your_civitai_token")
metadata_manager = ModelMetadataManager()

# Завантаження метаданих з Civitai
model_id = 12345
version_id = 67890
metadata = integration.fetch_model_metadata(model_id, version_id)

if metadata:
    # Збереження локально
    metadata_manager.set_civitai_metadata(
        "/path/to/model.safetensors", 
        metadata
    )
    
    # Завантаження превью
    integration.download_preview(
        metadata.preview_url,
        "/path/to/preview.jpg"
    )

# Читання локально збереженого hash
hash_value = metadata_manager.get_hash("/path/to/model.safetensors")
print(f"Model hash: {hash_value}")
```

### GUI Використання

1. **Завантаження моделей з папки:**
   - Перейти на вкладку Settings → Models
   - Натиснути "Browse" та вибрати папку з моделями
   - Натиснути "Refresh" для оновлення

2. **Отримання метаданих з Civitai:**
   - На карточці моделі натиснути "Fetch"
   - Вставити Civitai URL або ID моделі
   - Система автоматично:
     - Отримає hash моделі
     - Завантажить превью
     - Збереже інформацію локально

3. **Ручне редагування hash:**
   - На карточці моделі натиснути "Edit Hash"
   - Ввести hash вручну або вставити Civitai URL
   - Вибрати тип hash (AUTOV2, SHA256, civitai)
   - Натиснути "Save"

4. **Експорт/Імпорт метаданих:**
   - "Export Metadata" - збереження всіх метаданих у JSON
   - "Import Metadata" - завантаження метаданих з JSON файлу

## Структура метаданих

### JSON Формат

Кожна модель має супровідний файл `model_name.ext.metadata.json`:

```json
{
  "hash": "AUTOV2: 90BFFAFD10",
  "hash_type": "AUTOV2",
  "hash_autov2": "90BFFAFD10",
  "hash_sha256": "abcdef1234567890",
  "civitai_model_id": 2131974,
  "civitai_version_id": 2411703,
  "civitai_name": "MyAwesomeModel",
  "civitai_type": "Checkpoint",
  "model_type": "Checkpoint",
  "preview_path": ".previews/model_name.jpg",
  "trigger_words": ["trigger1", "trigger2"],
  "base_model": "SDXL 1.0",
  "preview_url": "https://civitai.com/...",
  "description": "Model description...",
  "last_updated": "2024-11-21T10:30:00"
}
```

### Підтримувані формати Hash:

1. **AUTOV2:** `AUTOV2: 90BFFAFD10`
2. **SHA256:** Повний SHA256 хеш
3. **Civitai:** `civitai: 2131974 @ 2411703`
4. **Legacy:** 10-символьні хеші

## Інтеграція в Colab

Для Google Colab сервера додайте в `launch.py` або `colab_setup.py`:

```python
from model_manager import ModelManager, register_model_manager

# Реєстрація типів для QML
register_model_manager()

# Ініціалізація менеджера
model_manager = ModelManager()

# Встановлення Civitai токена (якщо є)
civitai_token = os.environ.get('CIVITAI_TOKEN', '')
if civitai_token:
    model_manager.set_civitai_token(civitai_token)

# Передача в GUI контекст
context.setContextProperty("MODEL_MANAGER", model_manager)
```

Додайте в Settings.qml:

```qml
import "tabs/settings"

ModelsPanel {
    modelManager: MODEL_MANAGER
}
```

## API Reference

### CivitaiIntegration

#### Methods:

- `extract_civitai_ids_from_url(url: str) -> (model_id, version_id)`
  - Видобуває ID моделі з URL

- `fetch_model_metadata(model_id: int, version_id: int = None) -> CivitaiMetadata`
  - Завантажує метадані моделі з API

- `download_preview(preview_url: str, output_path: str) -> bool`
  - Завантажує превью зображення

- `calculate_file_hash(file_path: str, method: str = "SHA256") -> str`
  - Розраховує hash файлу

### ModelMetadataManager

#### Methods:

- `load_metadata(model_file_path: str) -> dict`
  - Завантажує метадані з JSON

- `save_metadata(model_file_path: str, metadata: dict) -> bool`
  - Зберігає метадані у JSON

- `set_hash(model_file_path: str, hash_value: str, hash_type: str) -> bool`
  - Встановлює hash для моделі

- `set_civitai_metadata(model_file_path: str, civitai_metadata) -> bool`
  - Встановлює метадані з Civitai

- `get_models_with_metadata(folder_path: str) -> dict`
  - Отримує всі моделі папки з метаданими

- `export_all_metadata(folder_path: str, export_file: str) -> bool`
  - Експортує всі метадані у JSON

### ModelManager (PyQt5)

#### Signals:

- `modelsUpdated` - моделі оновлені
- `modelSelected(ModelInfo)` - модель вибрана
- `fetchProgress(str)` - повідомлення про прогрес
- `fetchError(str)` - повідомлення про помилку

#### Slots:

- `load_models_from_folder(folder_path: str)`
  - Завантажує моделі з папки

- `fetch_civitai_metadata(model_path: str, civitai_url: str)`
  - Завантажує метадані з Civitai

- `set_model_hash(model_path: str, hash_value: str, hash_type: str)`
  - Встановлює hash вручну

## Обробка помилок

Всі модулі включають детальне логування. Для включення debug режиму:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Примітки для Google Colab

1. **Токен Civitai:** Встановіть змінну оточення `CIVITAI_TOKEN`
2. **Папки моделей:** Переконайтеся що папки доступні на диску
3. **Интернет:** Потрібна стабільна інтернет з'єднання для завантаження метаданих
4. **Throttling:** Civitai API має обмеження на запити. Система автоматично обробляє це

## Розширення функціоналу

Для додавання нових функцій:

1. **Нові формати hash:** Додайте регулярні вирази в `HASH_FORMATS` в `civitai_integration.py`
2. **Додаткові метадані:** Розширте клас `CivitaiMetadata` та JSON структуру
3. **GUI компоненти:** Створіть нові QML файли в `tabs/settings/`

## Тестування

```python
# Тест парсингу URL
integration = CivitaiIntegration()
model_id, version_id = integration.extract_civitai_ids_from_url(
    "https://civitai.com/models/123456?modelVersionId=789012"
)
assert model_id == 123456
assert version_id == 789012

# Тест зберігання метаданих
manager = ModelMetadataManager()
metadata = {"hash": "AUTOV2: 90BFFAFD10"}
manager.save_metadata("model.safetensors", metadata)
loaded = manager.load_metadata("model.safetensors")
assert loaded["hash"] == "AUTOV2: 90BFFAFD10"
```

## License

Цей код є частиною SD Inference Server проекту.
