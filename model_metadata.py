"""
Model Metadata Management Module
Handles storing and retrieving model metadata including hashes from Civitai
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# Metadata file suffix
METADATA_SUFFIX = ".metadata.json"


class ModelMetadataManager:
    """Manages metadata for models (hash, preview info, etc.)"""
    
    def __init__(self, models_root_dir: str = None):
        """
        Initialize metadata manager
        
        Args:
            models_root_dir: Root directory containing model folders (SD, LoRA, etc.)
        """
        self.models_root_dir = models_root_dir or os.path.join(os.path.dirname(__file__), "models")
        self.metadata_cache = {}
    
    def get_metadata_path(self, model_file_path: str) -> str:
        """
        Get metadata file path for a model
        
        Args:
            model_file_path: Path to model file
        
        Returns:
            Path to metadata JSON file
        """
        return model_file_path + METADATA_SUFFIX
    
    def save_metadata(self, model_file_path: str, metadata: Dict[str, Any]) -> bool:
        """
        Save metadata for a model to JSON file
        
        Args:
            model_file_path: Path to model file
            metadata: Dictionary with metadata
        
        Returns:
            True if successful, False otherwise
        """
        try:
            metadata_path = self.get_metadata_path(model_file_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            
            # Add timestamp
            metadata["last_updated"] = datetime.now().isoformat()
            
            # Validate hash format if present
            if "hash" in metadata:
                metadata["hash"] = self._validate_hash_format(metadata["hash"])
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Update cache
            self.metadata_cache[model_file_path] = metadata
            
            logger.info(f"Saved metadata for {os.path.basename(model_file_path)}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
            return False
    
    def load_metadata(self, model_file_path: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Load metadata for a model from JSON file
        
        Args:
            model_file_path: Path to model file
            use_cache: Use cached metadata if available
        
        Returns:
            Dictionary with metadata or None if not found
        """
        try:
            # Check cache first
            if use_cache and model_file_path in self.metadata_cache:
                return self.metadata_cache[model_file_path]
            
            metadata_path = self.get_metadata_path(model_file_path)
            
            if not os.path.exists(metadata_path):
                logger.debug(f"No metadata file found for {model_file_path}")
                return None
            
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Update cache
            self.metadata_cache[model_file_path] = metadata
            
            logger.debug(f"Loaded metadata for {os.path.basename(model_file_path)}")
            return metadata
        
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return None
    
    def delete_metadata(self, model_file_path: str) -> bool:
        """
        Delete metadata file for a model
        
        Args:
            model_file_path: Path to model file
        
        Returns:
            True if successful or file didn't exist, False on error
        """
        try:
            metadata_path = self.get_metadata_path(model_file_path)
            
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                logger.info(f"Deleted metadata for {os.path.basename(model_file_path)}")
            
            # Remove from cache
            if model_file_path in self.metadata_cache:
                del self.metadata_cache[model_file_path]
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete metadata: {e}")
            return False
    
    def get_hash(self, model_file_path: str) -> Optional[str]:
        """
        Get hash from model metadata
        
        Args:
            model_file_path: Path to model file
        
        Returns:
            Hash string or None if not found
        """
        metadata = self.load_metadata(model_file_path)
        return metadata.get("hash") if metadata else None
    
    def set_hash(self, model_file_path: str, hash_value: str, hash_type: str = "AUTOV2") -> bool:
        """
        Set hash for a model
        
        Args:
            model_file_path: Path to model file
            hash_value: Hash string
            hash_type: Type of hash (AUTOV2, SHA256, civitai, etc.)
        
        Returns:
            True if successful
        """
        metadata = self.load_metadata(model_file_path) or {}
        metadata["hash"] = hash_value
        metadata["hash_type"] = hash_type
        return self.save_metadata(model_file_path, metadata)
    
    def set_civitai_metadata(self, model_file_path: str, civitai_metadata: 'CivitaiMetadata') -> bool:
        """
        Set Civitai metadata for a model
        
        Args:
            model_file_path: Path to model file
            civitai_metadata: CivitaiMetadata object
        
        Returns:
            True if successful
        """
        metadata = self.load_metadata(model_file_path) or {}
        
        # Update with Civitai data
        metadata.update({
            "civitai_model_id": civitai_metadata.model_id,
            "civitai_version_id": civitai_metadata.version_id,
            "civitai_name": civitai_metadata.model_name,
            "civitai_type": civitai_metadata.model_type,
            "hash": civitai_metadata.hash_autov2 or civitai_metadata.hash_sha256,
            "hash_type": "AUTOV2" if civitai_metadata.hash_autov2 else "SHA256",
            "hash_autov2": civitai_metadata.hash_autov2,
            "hash_sha256": civitai_metadata.hash_sha256,
            "trigger_words": civitai_metadata.trigger_words,
            "base_model": civitai_metadata.base_model,
            "preview_url": civitai_metadata.preview_url,
        })
        
        return self.save_metadata(model_file_path, metadata)
    
    def get_models_with_metadata(self, folder_path: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all models in folder with their metadata
        
        Args:
            folder_path: Path to folder with models
        
        Returns:
            Dictionary mapping model paths to metadata
        """
        models = {}
        
        if not os.path.isdir(folder_path):
            return models
        
        valid_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
        
        for filename in os.listdir(folder_path):
            if not any(filename.endswith(ext) for ext in valid_extensions):
                continue
            
            model_path = os.path.join(folder_path, filename)
            metadata = self.load_metadata(model_path)
            
            models[model_path] = {
                "name": filename,
                "path": model_path,
                "size": os.path.getsize(model_path),
                "metadata": metadata or {}
            }
        
        return models
    
    def _validate_hash_format(self, hash_value: str) -> str:
        """
        Validate and normalize hash format
        
        Args:
            hash_value: Hash value to validate
        
        Returns:
            Normalized hash value
        """
        hash_value = hash_value.strip()
        
        # Normalize AUTOV2 format
        if hash_value.startswith("AUTOV2:"):
            parts = hash_value.split(":")
            if len(parts) == 2:
                hash_value = f"AUTOV2: {parts[1].strip().upper()}"
        
        # Normalize civitai format
        if hash_value.startswith("civitai:"):
            parts = hash_value.split(":")
            if len(parts) == 2:
                hash_value = f"civitai: {parts[1].strip()}"
        
        return hash_value
    
    def clear_cache(self):
        """Clear metadata cache"""
        self.metadata_cache.clear()
        logger.debug("Metadata cache cleared")
    
    def export_all_metadata(self, folder_path: str, export_file: str) -> bool:
        """
        Export all metadata from folder to JSON file
        
        Args:
            folder_path: Path to folder with models
            export_file: Path to export file
        
        Returns:
            True if successful
        """
        try:
            models = self.get_models_with_metadata(folder_path)
            
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "folder": folder_path,
                "models": models
            }
            
            os.makedirs(os.path.dirname(export_file), exist_ok=True)
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported metadata to {export_file}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export metadata: {e}")
            return False
    
    def import_metadata(self, import_file: str, folder_path: str = None) -> bool:
        """
        Import metadata from JSON file
        
        Args:
            import_file: Path to import file
            folder_path: Optional folder to restrict imports to
        
        Returns:
            True if successful
        """
        try:
            with open(import_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            models = import_data.get("models", {})
            imported_count = 0
            
            for model_path, model_info in models.items():
                # Adjust path if necessary
                if folder_path and not model_path.startswith(folder_path):
                    model_name = os.path.basename(model_path)
                    model_path = os.path.join(folder_path, model_name)
                
                if os.path.exists(model_path):
                    self.save_metadata(model_path, model_info.get("metadata", {}))
                    imported_count += 1
            
            logger.info(f"Imported metadata for {imported_count} models")
            return True
        
        except Exception as e:
            logger.error(f"Failed to import metadata: {e}")
            return False


# Utility functions

def get_metadata_for_model(model_path: str, manager: ModelMetadataManager = None) -> Optional[Dict]:
    """
    Convenience function to get metadata for a single model
    
    Args:
        model_path: Path to model file
        manager: Optional metadata manager instance
    
    Returns:
        Metadata dictionary or None
    """
    if manager is None:
        manager = ModelMetadataManager()
    return manager.load_metadata(model_path)


def set_metadata_for_model(model_path: str, metadata: Dict, manager: ModelMetadataManager = None) -> bool:
    """
    Convenience function to set metadata for a single model
    
    Args:
        model_path: Path to model file
        metadata: Metadata dictionary
        manager: Optional metadata manager instance
    
    Returns:
        True if successful
    """
    if manager is None:
        manager = ModelMetadataManager()
    return manager.save_metadata(model_path, metadata)
