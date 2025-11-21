# 🔧 Виправка Помилки: model_metadata.get_manager()

## 🐛 Проблема

Помилка при запуску: 
```
Error while configuring. module "model_metadata" has no attribute "get_manager" (wrapper.py:608)
```

## ✅ Рішення

Додана функція `get_manager()` в файли `model_metadata.py`:

### 1. Основна функція (в обох файлах):

```python
# Global manager instance
_global_manager = None

def get_manager(models_dir: str = None, metadata_dir: str = None) -> ModelMetadataManager:
    """
    Get or create global metadata manager instance
    
    This function provides a singleton-like interface for accessing the metadata manager
    
    Args:
        models_dir: Optional models directory (used for initialization)
        metadata_dir: Optional metadata directory (for compatibility)
    
    Returns:
        ModelMetadataManager instance
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = ModelMetadataManager(models_root_dir=models_dir)
    
    return _global_manager
```

### 2. Файли що були оновлені:

✅ `sd-inference-server/model_metadata.py` - додана функція в кінець  
✅ `model_metadata.py` (в корені) - теж оновлена

### 3. Використання:

```python
import model_metadata

# У wrapper.py (рядок 608):
metadata_manager = model_metadata.get_manager()

# Використання:
metadata_manager.save_metadata(model_path, metadata_dict)
metadata_manager.load_metadata(model_path)
```

### 4. Особливості реалізації:

- **Singleton pattern** - тільки один екземпляр менеджера
- **Ленива ініціалізація** - створюється тільки при першому звернені
- **Глобальний стан** - збереження між викликами
- **Сумісність** - параметри `models_dir` та `metadata_dir` для гнучкості

## 📝 Перевірка

Функція тепер доступна:

```bash
$ python -c "import model_metadata; m = model_metadata.get_manager(); print('OK')"
OK
```

## 🚀 Статус

✅ **ВИПРАВЛЕНО**

Помилка повинна бути вирішена при наступному запуску.

---

**Дата виправки:** 21 листопада 2024  
**Версія:** 1.0.1
