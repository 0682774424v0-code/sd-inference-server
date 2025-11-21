"""
Модуль для управління превьюшами моделей у GUI
Відображає обкладинки LoRA, Checkpoint, Upscaler та інших моделей
"""

import os
import json
from pathlib import Path
from PyQt5.QtCore import QObject, QUrl, pyqtProperty, pyqtSignal, pyqtSlot, QThread, QMutex, QThreadPool
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtQml import qmlRegisterSingletonType
import model_metadata


class ModelPreviewProvider(QObject):
    """Провайдер превьюшів для моделей"""
    
    modelDataUpdated = pyqtSignal(str, object)  # model_type, model_data
    allModelsUpdated = pyqtSignal(object)  # all_models_data
    
    def __init__(self, models_dir: str, parent=None):
        super().__init__(parent)
        self.models_dir = models_dir
        self.metadata_manager = model_metadata.ModelMetadataManager(models_dir)
        self._models_cache = {}
        self._scanning = False
        
    def scan_models(self):
        """Скануємо всі моделі та їх превьюші"""
        if self._scanning:
            return
        
        self._scanning = True
        models_data = {
            "LORA": [],
            "CHECKPOINT": [],
            "UPSCALER": [],
            "CONTROLNET": [],
            "DETAILER": [],
            "TEXTUAL_INVERSION": []
        }
        
        try:
            # Сканування LoRA
            lora_paths = [
                os.path.join(self.models_dir, "LoRA"),
                os.path.join(self.models_dir, "LyCORIS")
            ]
            for lora_path in lora_paths:
                if os.path.exists(lora_path):
                    models_data["LORA"].extend(
                        self._scan_directory(lora_path, "LORA")
                    )
            
            # Сканування Checkpoint
            checkpoint_paths = [
                os.path.join(self.models_dir, "SD"),
                os.path.join(self.models_dir, "Stable-diffusion")
            ]
            for cp_path in checkpoint_paths:
                if os.path.exists(cp_path):
                    models_data["CHECKPOINT"].extend(
                        self._scan_directory(cp_path, "CHECKPOINT")
                    )
            
            # Сканування Upscaler
            upscaler_paths = [
                os.path.join(self.models_dir, "SR"),
                os.path.join(self.models_dir, "ESRGAN"),
                os.path.join(self.models_dir, "RealESRGAN")
            ]
            for up_path in upscaler_paths:
                if os.path.exists(up_path):
                    models_data["UPSCALER"].extend(
                        self._scan_directory(up_path, "UPSCALER")
                    )
            
            # Сканування ControlNet
            cn_path = os.path.join(self.models_dir, "CN")
            if os.path.exists(cn_path):
                models_data["CONTROLNET"].extend(
                    self._scan_directory(cn_path, "CONTROLNET")
                )
            
            self._models_cache = models_data
            self.allModelsUpdated.emit(models_data)
            
        except Exception as e:
            print(f"Error scanning models: {e}")
        finally:
            self._scanning = False
    
    def _scan_directory(self, directory: str, model_type: str) -> list:
        """Скануємо директорію на моделі та їх превьюші"""
        models = []
        
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                
                # Пропускаємо директорії та приховані файли
                if os.path.isdir(file_path) or filename.startswith('.'):
                    continue
                
                # Перевіряємо розширення
                if not self._is_model_file(filename, model_type):
                    continue
                
                model_info = self._get_model_info(file_path, model_type)
                if model_info:
                    models.append(model_info)
        
        except Exception as e:
            print(f"Error scanning directory {directory}: {e}")
        
        return models
    
    def _is_model_file(self, filename: str, model_type: str) -> bool:
        """Перевіряємо, чи це файл моделі"""
        filename_lower = filename.lower()
        
        extensions = {
            "LORA": [".safetensors", ".pt", ".pth", ".bin"],
            "CHECKPOINT": [".safetensors", ".pt", ".pth", ".bin", ".ckpt"],
            "UPSCALER": [".safetensors", ".pt", ".pth", ".bin", ".pth"],
            "CONTROLNET": [".safetensors", ".pt", ".pth", ".bin"],
            "DETAILER": [".safetensors", ".pt", ".pth", ".bin"],
            "TEXTUAL_INVERSION": [".safetensors", ".pt", ".pth", ".bin"]
        }
        
        for ext in extensions.get(model_type, []):
            if filename_lower.endswith(ext):
                return True
        
        return False
    
    def _get_model_info(self, file_path: str, model_type: str) -> dict:
        """Отримуємо інформацію про модель"""
        try:
            filename = os.path.basename(file_path)
            base_name = os.path.splitext(filename)[0]
            
            # Отримуємо превьюш
            preview_path = model_metadata.get_model_preview_path(file_path, model_type)
            
            # Отримуємо метадані з файлу метаданих (якщо існує)
            relative_path = os.path.relpath(file_path, self.models_dir)
            stored_metadata = self.metadata_manager.get_model_metadata(relative_path)
            
            # Отримуємо хеші
            hashes = model_metadata.get_all_model_hashes(file_path) if stored_metadata is None else stored_metadata.get("hashes", {})
            
            model_info = {
                "name": base_name,
                "filename": filename,
                "path": file_path,
                "relative_path": relative_path,
                "type": model_type,
                "preview": preview_path,
                "size": os.path.getsize(file_path),
                "hashes": hashes,
            }
            
            # Додаємо збережені метадані
            if stored_metadata:
                model_info.update(stored_metadata)
            
            # Для LoRA отримуємо слова-тригери
            if model_type == "LORA":
                trigger_words = model_metadata.extract_lora_trigger_words(file_path)
                if trigger_words:
                    model_info["trigger_words"] = trigger_words
            
            return model_info
        
        except Exception as e:
            print(f"Error getting model info for {file_path}: {e}")
            return None
    
    @pyqtSlot(str, str, object)
    def updateModelMetadata(self, model_type: str, model_name: str, metadata: dict):
        """Оновлюємо метадані моделі"""
        try:
            # Знайдемо модель
            models = self._models_cache.get(model_type, [])
            for model in models:
                if model["name"] == model_name:
                    # Оновлюємо метадані
                    self.metadata_manager.add_model_metadata(
                        model["relative_path"], 
                        metadata
                    )
                    # Оновлюємо хеші якщо потрібно
                    if "update_hashes" in metadata and metadata["update_hashes"]:
                        self.metadata_manager.update_model_hashes(
                            model["relative_path"],
                            model["path"]
                        )
                    
                    self.modelDataUpdated.emit(model_type, model)
                    break
        
        except Exception as e:
            print(f"Error updating model metadata: {e}")
    
    @pyqtProperty(object, notify=allModelsUpdated)
    def allModels(self):
        """Отримуємо всі моделі"""
        return self._models_cache
    
    @pyqtSlot()
    def refresh(self):
        """Оновлюємо список моделей"""
        self.scan_models()


class ModelInfoFormatter(QObject):
    """Форматує інформацію про модель для відображення"""
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Форматує розмір файлу"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    @staticmethod
    def format_hashes(hashes: dict) -> str:
        """Форматує хеші для відображення (як у Civitai)"""
        return model_metadata.format_hashes_for_metadata(hashes)
    
    @staticmethod
    def get_trigger_words_display(trigger_words: list) -> str:
        """Форматує слова-тригери для відображення"""
        if not trigger_words:
            return ""
        return ", ".join(trigger_words[:3])  # Показуємо перші 3
    
    @staticmethod
    def format_model_description(model_info: dict) -> str:
        """Створює описання моделі для відображення"""
        parts = []
        
        if "description" in model_info:
            parts.append(model_info["description"])
        
        if "base_model" in model_info:
            parts.append(f"Base: {model_info['base_model']}")
        
        if "trigger_words" in model_info:
            words = ModelInfoFormatter.get_trigger_words_display(model_info["trigger_words"])
            if words:
                parts.append(f"Triggers: {words}")
        
        if "author" in model_info:
            parts.append(f"By: {model_info['author']}")
        
        return " | ".join(parts)
