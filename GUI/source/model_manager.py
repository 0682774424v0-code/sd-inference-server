"""
Model Manager Backend
Provides PyQt5 interface for model metadata management and Civitai integration
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, pyqtSlot, pyqtProperty, QObject, QThread, QUrl
from PyQt5.QtGui import QImage
from PyQt5.QtQml import qmlRegisterType

import model_metadata
from civitai_integration import CivitaiIntegration, AsyncCivitaiFetcher, CivitaiMetadata

logger = logging.getLogger(__name__)


class ModelFetcherThread(QThread):
    """Thread for fetching model metadata from Civitai"""
    
    fetched = pyqtSignal(object)  # CivitaiMetadata
    error = pyqtSignal(str)
    
    def __init__(self, civitai_url: str, civitai_token: Optional[str] = None):
        super().__init__()
        self.civitai_url = civitai_url
        self.civitai_token = civitai_token
    
    def run(self):
        try:
            integration = CivitaiIntegration(self.civitai_token)
            model_id, version_id = integration.extract_civitai_ids_from_url(self.civitai_url)
            
            if not model_id:
                self.error.emit("Invalid Civitai URL")
                return
            
            metadata = integration.fetch_model_metadata(model_id, version_id)
            
            if metadata:
                self.fetched.emit(metadata)
            else:
                self.error.emit("Failed to fetch metadata from Civitai")
        
        except Exception as e:
            logger.error(f"Fetcher thread error: {e}")
            self.error.emit(str(e))


class ModelInfo(QObject):
    """Container for model information exposed to QML"""
    
    updated = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._name = ""
        self._path = ""
        self._size = 0
        self._hash = ""
        self._hash_type = ""
        self._civitai_name = ""
        self._civitai_type = ""
        self._civitai_id = 0
        self._trigger_words = []
        self._base_model = ""
        self._preview_path = ""
        self._description = ""
    
    @pyqtProperty(str, notify=updated)
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def path(self):
        return self._path
    
    @path.setter
    def path(self, value):
        if self._path != value:
            self._path = value
            self.updated.emit()
    
    @pyqtProperty(int, notify=updated)
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        if self._size != value:
            self._size = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def hash(self):
        return self._hash
    
    @hash.setter
    def hash(self, value):
        if self._hash != value:
            self._hash = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def hashType(self):
        return self._hash_type
    
    @hashType.setter
    def hashType(self, value):
        if self._hash_type != value:
            self._hash_type = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def civitaiName(self):
        return self._civitai_name
    
    @civitaiName.setter
    def civitaiName(self, value):
        if self._civitai_name != value:
            self._civitai_name = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def civitaiType(self):
        return self._civitai_type
    
    @civitaiType.setter
    def civitaiType(self, value):
        if self._civitai_type != value:
            self._civitai_type = value
            self.updated.emit()
    
    @pyqtProperty(int, notify=updated)
    def civitaiId(self):
        return self._civitai_id
    
    @civitaiId.setter
    def civitaiId(self, value):
        if self._civitai_id != value:
            self._civitai_id = value
            self.updated.emit()
    
    @pyqtProperty(list, notify=updated)
    def triggerWords(self):
        return self._trigger_words
    
    @triggerWords.setter
    def triggerWords(self, value):
        if self._trigger_words != value:
            self._trigger_words = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def baseModel(self):
        return self._base_model
    
    @baseModel.setter
    def baseModel(self, value):
        if self._base_model != value:
            self._base_model = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def previewPath(self):
        return self._preview_path
    
    @previewPath.setter
    def previewPath(self, value):
        if self._preview_path != value:
            self._preview_path = value
            self.updated.emit()
    
    @pyqtProperty(str, notify=updated)
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if self._description != value:
            self._description = value
            self.updated.emit()
    
    def load_from_dict(self, data: Dict):
        """Load model info from dictionary"""
        self.name = data.get("name", "")
        self.path = data.get("path", "")
        self.size = data.get("size", 0)
        self.hash = data.get("hash", "")
        self.hashType = data.get("hash_type", "")
        self.civitaiName = data.get("civitai_name", "")
        self.civitaiType = data.get("civitai_type", "")
        self.civitaiId = data.get("civitai_model_id", 0)
        self.triggerWords = data.get("trigger_words", [])
        self.baseModel = data.get("base_model", "")
        self.previewPath = data.get("preview_path", "")
        self.description = data.get("description", "")


class ModelManager(QObject):
    """Main model manager for GUI integration"""
    
    modelsUpdated = pyqtSignal()
    modelSelected = pyqtSignal(object)  # ModelInfo
    fetchProgress = pyqtSignal(str)  # Status message
    fetchError = pyqtSignal(str)  # Error message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._models = {}  # model_path -> ModelInfo
        self._selected_model = None
        self._metadata_manager = model_metadata.ModelMetadataManager()
        self._civitai_integration = CivitaiIntegration()
        self._fetcher_thread = None
        
        # Register QML types
        qmlRegisterType(ModelInfo, "gui.models", 1, 0, "ModelInfo")
    
    def set_civitai_token(self, token: str):
        """Set Civitai API token for authenticated requests"""
        self._civitai_integration = CivitaiIntegration(token)
    
    @pyqtSlot(str)
    def load_models_from_folder(self, folder_path: str):
        """
        Load all models from folder and their metadata
        
        Args:
            folder_path: Path to folder with models
        """
        if isinstance(folder_path, QUrl):
            folder_path = folder_path.toLocalFile()
        
        try:
            self._models.clear()
            folder_path = os.path.abspath(folder_path)
            
            if not os.path.isdir(folder_path):
                self.fetchError.emit(f"Folder not found: {folder_path}")
                return
            
            valid_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
            
            for filename in sorted(os.listdir(folder_path)):
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    continue
                
                model_path = os.path.join(folder_path, filename)
                file_size = os.path.getsize(model_path)
                
                # Load metadata
                metadata = self._metadata_manager.load_metadata(model_path)
                
                # Create ModelInfo
                model_info = ModelInfo(self)
                model_info.name = filename
                model_info.path = model_path
                model_info.size = file_size
                
                if metadata:
                    model_info.load_from_dict(metadata)
                
                self._models[model_path] = model_info
            
            self.modelsUpdated.emit()
            self.fetchProgress.emit(f"Loaded {len(self._models)} models")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            self.fetchError.emit(str(e))
    
    @pyqtSlot(int, result=object)
    def get_model_at(self, index: int) -> Optional[ModelInfo]:
        """Get model at index"""
        models_list = list(self._models.values())
        if 0 <= index < len(models_list):
            return models_list[index]
        return None
    
    @pyqtProperty(int, notify=modelsUpdated)
    def modelCount(self) -> int:
        """Get total number of models"""
        return len(self._models)
    
    @pyqtSlot(str)
    def select_model(self, model_path: str):
        """Select a model"""
        if model_path in self._models:
            self._selected_model = self._models[model_path]
            self.modelSelected.emit(self._selected_model)
    
    @pyqtSlot(str, str)
    def fetch_civitai_metadata(self, model_path: str, civitai_url: str):
        """
        Fetch metadata from Civitai for a model
        
        Args:
            model_path: Path to model file
            civitai_url: Civitai URL or model ID
        """
        self.fetchProgress.emit("Fetching from Civitai...")
        
        # Stop any existing fetcher
        if self._fetcher_thread and self._fetcher_thread.isRunning():
            self._fetcher_thread.quit()
            self._fetcher_thread.wait()
        
        self._fetcher_thread = ModelFetcherThread(civitai_url)
        self._fetcher_thread.fetched.connect(
            lambda metadata: self._on_metadata_fetched(model_path, metadata)
        )
        self._fetcher_thread.error.connect(self.fetchError.emit)
        self._fetcher_thread.start()
    
    def _on_metadata_fetched(self, model_path: str, civitai_metadata: CivitaiMetadata):
        """Handle fetched Civitai metadata"""
        try:
            if model_path not in self._models:
                self.fetchError.emit("Model not found in loaded models")
                return
            
            # Save to metadata file
            self._metadata_manager.set_civitai_metadata(model_path, civitai_metadata)
            
            # Update model info
            model_info = self._models[model_path]
            model_info.hash = civitai_metadata.hash_autov2 or civitai_metadata.hash_sha256 or ""
            model_info.hashType = "AUTOV2" if civitai_metadata.hash_autov2 else "SHA256"
            model_info.civitaiName = civitai_metadata.model_name or ""
            model_info.civitaiType = civitai_metadata.model_type or ""
            model_info.civitaiId = civitai_metadata.model_id or 0
            model_info.triggerWords = civitai_metadata.trigger_words or []
            model_info.baseModel = civitai_metadata.base_model or ""
            model_info.description = civitai_metadata.description or ""
            
            # Download preview if available
            if civitai_metadata.preview_url:
                self._download_preview(model_path, civitai_metadata.preview_url)
            
            self.modelsUpdated.emit()
            self.fetchProgress.emit("Metadata fetched successfully")
            
        except Exception as e:
            logger.error(f"Failed to process fetched metadata: {e}")
            self.fetchError.emit(str(e))
    
    def _download_preview(self, model_path: str, preview_url: str):
        """Download preview image"""
        try:
            preview_dir = os.path.join(os.path.dirname(model_path), ".previews")
            preview_filename = os.path.basename(model_path).rsplit(".", 1)[0] + ".jpg"
            preview_path = os.path.join(preview_dir, preview_filename)
            
            if self._civitai_integration.download_preview(preview_url, preview_path):
                model_info = self._models[model_path]
                model_info.previewPath = preview_path
                
                # Save to metadata
                metadata = self._metadata_manager.load_metadata(model_path) or {}
                metadata["preview_path"] = preview_path
                self._metadata_manager.save_metadata(model_path, metadata)
        
        except Exception as e:
            logger.warning(f"Failed to download preview: {e}")
    
    @pyqtSlot(str, str, str)
    def set_model_hash(self, model_path: str, hash_value: str, hash_type: str = "AUTOV2"):
        """
        Manually set hash for a model
        
        Args:
            model_path: Path to model
            hash_value: Hash value
            hash_type: Type of hash
        """
        try:
            self._metadata_manager.set_hash(model_path, hash_value, hash_type)
            
            if model_path in self._models:
                model_info = self._models[model_path]
                model_info.hash = hash_value
                model_info.hashType = hash_type
                self.modelsUpdated.emit()
            
            self.fetchProgress.emit("Hash updated")
        
        except Exception as e:
            logger.error(f"Failed to set hash: {e}")
            self.fetchError.emit(str(e))
    
    @pyqtSlot(str)
    def delete_model_metadata(self, model_path: str):
        """Delete metadata for a model"""
        try:
            self._metadata_manager.delete_metadata(model_path)
            
            if model_path in self._models:
                model_info = self._models[model_path]
                model_info.hash = ""
                model_info.hashType = ""
                model_info.civitaiName = ""
                model_info.civitaiType = ""
                model_info.civitaiId = 0
                self.modelsUpdated.emit()
            
            self.fetchProgress.emit("Metadata deleted")
        
        except Exception as e:
            logger.error(f"Failed to delete metadata: {e}")
            self.fetchError.emit(str(e))
    
    @pyqtSlot(str, result=str)
    def export_all_metadata(self, export_path: str) -> str:
        """
        Export all metadata to JSON
        
        Args:
            export_path: Path to export file
        
        Returns:
            Status message
        """
        try:
            folder_path = list(self._models.values())[0].path
            folder_path = os.path.dirname(folder_path)
            
            if self._metadata_manager.export_all_metadata(folder_path, export_path):
                return f"Metadata exported to {export_path}"
            return "Failed to export metadata"
        
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return str(e)
    
    @pyqtSlot(str, str, result=str)
    def import_metadata(self, import_path: str, target_folder: str) -> str:
        """
        Import metadata from JSON
        
        Args:
            import_path: Path to import file
            target_folder: Target folder for models
        
        Returns:
            Status message
        """
        try:
            if self._metadata_manager.import_metadata(import_path, target_folder):
                # Reload models
                self.load_models_from_folder(target_folder)
                return "Metadata imported successfully"
            return "Failed to import metadata"
        
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return str(e)


# Register with QML
def register_model_manager():
    """Register model manager types with QML"""
    from PyQt5.QtQml import qmlRegisterType
    qmlRegisterType(ModelManager, "gui.models", 1, 0, "ModelManager")
