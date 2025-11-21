"""
Automatic Model Metadata Detection Hook
Automatically detects and fetches model metadata when models are detected in watch folders
"""

import os
import logging
from typing import Optional, Callable
from pathlib import Path
import threading
import time

from model_metadata import ModelMetadataManager
from civitai_integration import CivitaiIntegration

logger = logging.getLogger(__name__)


class AutoModelMetadataDetector:
    """Automatically detects and processes new models"""
    
    def __init__(
        self, 
        watch_folders: dict,  # {"SD": "/path/to/SD", "LoRA": "/path/to/LoRA"}
        civitai_token: Optional[str] = None,
        callback: Optional[Callable] = None
    ):
        """
        Initialize automatic detector
        
        Args:
            watch_folders: Dictionary of folder type to path
            civitai_token: Optional Civitai token
            callback: Optional callback function(model_path, metadata) when model is processed
        """
        self.watch_folders = watch_folders
        self.civitai_token = civitai_token
        self.callback = callback
        
        self.metadata_manager = ModelMetadataManager()
        self.civitai_integration = CivitaiIntegration(civitai_token)
        
        self.processed_files = set()
        self.processing = False
        self._stop_event = threading.Event()
    
    def start_watching(self):
        """Start watching folders for new models"""
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        thread.start()
        logger.info("Started watching folders for models")
    
    def stop_watching(self):
        """Stop watching folders"""
        self._stop_event.set()
        logger.info("Stopped watching folders")
    
    def _watch_loop(self):
        """Main watching loop"""
        while not self._stop_event.is_set():
            for folder_type, folder_path in self.watch_folders.items():
                if not os.path.isdir(folder_path):
                    continue
                
                self._process_folder(folder_path, folder_type)
            
            # Check every 30 seconds
            self._stop_event.wait(30)
    
    def _process_folder(self, folder_path: str, folder_type: str):
        """Process all models in folder"""
        valid_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
        
        try:
            for filename in os.listdir(folder_path):
                if not any(filename.endswith(ext) for ext in valid_extensions):
                    continue
                
                model_path = os.path.join(folder_path, filename)
                
                # Skip if already processed
                if model_path in self.processed_files:
                    continue
                
                # Skip if already has metadata
                existing_metadata = self.metadata_manager.load_metadata(model_path)
                if existing_metadata and existing_metadata.get("hash"):
                    self.processed_files.add(model_path)
                    continue
                
                logger.info(f"Detected new model: {filename}")
                self._process_model(model_path, folder_type)
                self.processed_files.add(model_path)
        
        except Exception as e:
            logger.error(f"Error processing folder {folder_path}: {e}")
    
    def _process_model(self, model_path: str, model_type: str):
        """Process single model"""
        try:
            # Calculate file hash first (quick operation)
            logger.debug(f"Calculating hash for {os.path.basename(model_path)}...")
            file_hash = self.civitai_integration.calculate_file_hash(model_path, "AUTOV2")
            
            if file_hash:
                metadata = {
                    "hash": f"AUTOV2: {file_hash}",
                    "hash_type": "AUTOV2",
                    "hash_autov2": file_hash,
                    "model_type": model_type,
                    "source": "auto_detected"
                }
                
                self.metadata_manager.save_metadata(model_path, metadata)
                logger.info(f"Saved auto-detected hash for {os.path.basename(model_path)}: {file_hash}")
                
                if self.callback:
                    self.callback(model_path, metadata)
        
        except Exception as e:
            logger.error(f"Error processing model {model_path}: {e}")
    
    def manual_fetch_civitai(self, model_path: str, civitai_url: str) -> bool:
        """
        Manually fetch metadata for a model from Civitai
        
        Args:
            model_path: Path to model
            civitai_url: Civitai URL or model ID
        
        Returns:
            True if successful
        """
        try:
            model_id, version_id = self.civitai_integration.extract_civitai_ids_from_url(civitai_url)
            
            if not model_id:
                logger.error(f"Invalid Civitai URL: {civitai_url}")
                return False
            
            logger.info(f"Fetching Civitai metadata for model {model_id}...")
            metadata = self.civitai_integration.fetch_model_metadata(model_id, version_id)
            
            if not metadata:
                logger.error("Failed to fetch metadata from Civitai")
                return False
            
            # Save metadata
            self.metadata_manager.set_civitai_metadata(model_path, metadata)
            
            # Download preview
            if metadata.preview_url:
                preview_dir = os.path.join(os.path.dirname(model_path), ".previews")
                preview_filename = os.path.basename(model_path).rsplit(".", 1)[0] + ".jpg"
                preview_path = os.path.join(preview_dir, preview_filename)
                
                if self.civitai_integration.download_preview(metadata.preview_url, preview_path):
                    model_metadata_dict = self.metadata_manager.load_metadata(model_path)
                    model_metadata_dict["preview_path"] = preview_path
                    self.metadata_manager.save_metadata(model_path, model_metadata_dict)
            
            logger.info(f"Successfully fetched metadata for {os.path.basename(model_path)}")
            
            if self.callback:
                metadata_dict = self.metadata_manager.load_metadata(model_path)
                self.callback(model_path, metadata_dict)
            
            return True
        
        except Exception as e:
            logger.error(f"Error fetching Civitai metadata: {e}")
            return False


class ModelHashCalculator:
    """Utility for calculating model hashes"""
    
    @staticmethod
    def calculate_all_hashes(folder_path: str, force_recalculate: bool = False) -> dict:
        """
        Calculate hashes for all models in folder
        
        Args:
            folder_path: Path to folder with models
            force_recalculate: Force recalculation even if hash exists
        
        Returns:
            Dictionary of model_path -> hash
        """
        results = {}
        manager = ModelMetadataManager()
        integration = CivitaiIntegration()
        
        valid_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
        
        if not os.path.isdir(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return results
        
        models = []
        for filename in os.listdir(folder_path):
            if any(filename.endswith(ext) for ext in valid_extensions):
                models.append(os.path.join(folder_path, filename))
        
        logger.info(f"Calculating hashes for {len(models)} models...")
        
        for idx, model_path in enumerate(models, 1):
            try:
                # Check if already has hash
                if not force_recalculate:
                    existing = manager.load_metadata(model_path)
                    if existing and existing.get("hash"):
                        results[model_path] = existing["hash"]
                        logger.debug(f"[{idx}/{len(models)}] Using existing hash for {os.path.basename(model_path)}")
                        continue
                
                # Calculate hash
                logger.info(f"[{idx}/{len(models)}] Calculating hash for {os.path.basename(model_path)}...")
                hash_value = integration.calculate_file_hash(model_path, "AUTOV2")
                
                if hash_value:
                    results[model_path] = f"AUTOV2: {hash_value}"
                    
                    # Save to metadata
                    metadata = manager.load_metadata(model_path) or {}
                    metadata["hash"] = f"AUTOV2: {hash_value}"
                    metadata["hash_type"] = "AUTOV2"
                    metadata["hash_autov2"] = hash_value
                    manager.save_metadata(model_path, metadata)
                
            except Exception as e:
                logger.error(f"Error calculating hash for {os.path.basename(model_path)}: {e}")
        
        logger.info(f"Hash calculation complete. Processed {len(results)} models")
        return results


# Example usage
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example: Watch folders and auto-detect models
    watch_folders = {
        "SD": "./models/SD",
        "LoRA": "./models/LoRA",
        "Upscaler": "./models/SR",
    }
    
    civitai_token = os.environ.get("CIVITAI_TOKEN", "")
    
    def on_model_processed(model_path, metadata):
        logger.info(f"Model processed: {model_path}")
        logger.info(f"Metadata: {metadata}")
    
    detector = AutoModelMetadataDetector(
        watch_folders,
        civitai_token=civitai_token,
        callback=on_model_processed
    )
    
    # Start watching
    detector.start_watching()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        detector.stop_watching()
        logger.info("Detector stopped")
