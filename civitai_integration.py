"""
Civitai Integration Module
Provides utilities for fetching model metadata, hashes, and previews from Civitai
"""

import os
import json
import hashlib
import requests
import threading
from typing import Dict, Optional, Tuple, List
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

# Civitai API endpoints
CIVITAI_API_BASE = "https://civitai.com/api/v1"
CIVITAI_MODEL_INFO = f"{CIVITAI_API_BASE}/models"
CIVITAI_VERSION_INFO = f"{CIVITAI_API_BASE}/model-versions"

# Hash format patterns
HASH_FORMATS = {
    "AUTOV2": r"AUTOV2:\s+[A-F0-9]+",  # AUTOV2: 90BFFAFD10
    "civitai": r"civitai:\s+\d+\s*@\s*\d+",  # civitai: 2131974 @ 2411703
    "civitai_model": r"civitai:\s+\d+",  # civitai: 2131974
    "legacy": r"[a-f0-9]{10}",  # Legacy 10-char hash
}


class CivitaiMetadata:
    """Container for Civitai model metadata"""
    
    def __init__(self):
        self.model_id: Optional[int] = None
        self.version_id: Optional[int] = None
        self.model_name: Optional[str] = None
        self.model_type: Optional[str] = None
        self.hash_autov2: Optional[str] = None
        self.hash_sha256: Optional[str] = None
        self.preview_url: Optional[str] = None
        self.trigger_words: List[str] = []
        self.base_model: Optional[str] = None
        self.file_size: Optional[int] = None
        self.download_count: int = 0
        self.rating: float = 0.0
        self.description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert metadata to dictionary for JSON serialization"""
        return {
            "model_id": self.model_id,
            "version_id": self.version_id,
            "model_name": self.model_name,
            "model_type": self.model_type,
            "hash_autov2": self.hash_autov2,
            "hash_sha256": self.hash_sha256,
            "preview_url": self.preview_url,
            "trigger_words": self.trigger_words,
            "base_model": self.base_model,
            "file_size": self.file_size,
            "download_count": self.download_count,
            "rating": self.rating,
            "description": self.description,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'CivitaiMetadata':
        """Create metadata object from dictionary"""
        metadata = CivitaiMetadata()
        for key, value in data.items():
            if hasattr(metadata, key):
                setattr(metadata, key, value)
        return metadata


class CivitaiIntegration:
    """Main class for Civitai API integration"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Civitai integration
        
        Args:
            token: Optional Civitai API token for authenticated requests
        """
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })
        self.session.timeout = 10
    
    def extract_civitai_ids_from_url(self, url: str) -> Tuple[Optional[int], Optional[int]]:
        """
        Extract model and version IDs from Civitai URL
        
        Supported URL formats:
        - https://civitai.com/models/123456
        - https://civitai.com/models/123456?modelVersionId=456789
        - https://civitai.com/api/download/models/123456@456789
        
        Args:
            url: Civitai model URL
        
        Returns:
            Tuple of (model_id, version_id) or (None, None) if not valid
        """
        try:
            parsed = urlparse(url)
            
            # Format: /api/download/models/123456@456789
            if "api/download/models/" in url:
                parts = url.split("/models/")[-1].split("@")
                model_id = int(parts[0])
                version_id = int(parts[1]) if len(parts) > 1 else None
                return model_id, version_id
            
            # Format: /models/123456
            if "/models/" in parsed.path:
                model_id = int(parsed.path.split("/models/")[-1].rstrip("/"))
                
                # Check for versionId in query params
                version_id = None
                if "modelVersionId" in parsed.query:
                    query_params = parse_qs(parsed.query)
                    version_id = int(query_params["modelVersionId"][0])
                
                return model_id, version_id
            
            return None, None
        except (ValueError, IndexError, AttributeError):
            logger.warning(f"Could not extract IDs from Civitai URL: {url}")
            return None, None
    
    def fetch_model_metadata(self, model_id: int, version_id: Optional[int] = None) -> Optional[CivitaiMetadata]:
        """
        Fetch model metadata from Civitai API
        
        Args:
            model_id: Civitai model ID
            version_id: Optional specific version ID
        
        Returns:
            CivitaiMetadata object or None if fetch failed
        """
        try:
            # Fetch model info
            model_url = f"{CIVITAI_MODEL_INFO}/{model_id}"
            model_response = self.session.get(model_url, timeout=10)
            model_response.raise_for_status()
            model_data = model_response.json()
            
            metadata = CivitaiMetadata()
            metadata.model_id = model_data.get("id")
            metadata.model_name = model_data.get("name")
            metadata.model_type = model_data.get("type")
            metadata.download_count = model_data.get("downloadCount", 0)
            metadata.rating = model_data.get("stats", {}).get("rating", 0.0)
            metadata.description = model_data.get("description", "")[:500]  # Truncate description
            
            # Get latest version if not specified
            versions = model_data.get("modelVersions", [])
            if not versions:
                logger.warning(f"No versions found for model {model_id}")
                return None
            
            target_version = None
            if version_id:
                target_version = next((v for v in versions if v.get("id") == version_id), None)
            if not target_version:
                target_version = versions[0]  # Use latest version
            
            metadata.version_id = target_version.get("id")
            metadata.base_model = target_version.get("baseModel")
            
            # Extract hash and trigger words
            metadata.trigger_words = target_version.get("trainedWords", [])
            
            # Get file hash
            files = target_version.get("files", [])
            if files:
                primary_file = files[0]
                metadata.hash_autov2 = primary_file.get("hashes", {}).get("AUTOV2")
                metadata.hash_sha256 = primary_file.get("hashes", {}).get("SHA256")
                metadata.file_size = primary_file.get("size")
            
            # Get preview image
            images = target_version.get("images", [])
            if images:
                metadata.preview_url = images[0].get("url")
            
            logger.info(f"Fetched metadata for model {model_id}: {metadata.model_name}")
            return metadata
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch model metadata from Civitai: {e}")
            return None
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            logger.error(f"Failed to parse Civitai response: {e}")
            return None
    
    def download_preview(self, preview_url: str, output_path: str) -> bool:
        """
        Download preview image from Civitai
        
        Args:
            preview_url: URL of preview image
            output_path: Where to save the preview
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.session.get(preview_url, timeout=30)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded preview to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to download preview: {e}")
            return False
    
    def extract_metadata_from_generation_params(self, params_text: str) -> Dict[str, any]:
        """
        Extract generation parameters from image metadata string
        
        Example:
        (masterpiece, best quality), <lora:AvariceV1.1:0.8>, ...
        Negative prompt: worst quality, low quality
        Steps: 24, Sampler: DPM2 a, CFG scale: 3.5, Seed: 1486243165,
        Size: 832x1216, Model hash: cab478b74a, Model: novaFurryXL,
        Lora hashes: "AvariceV1.1: 77fa6414d4fe, Kerfus: 23fbc4a6fcd6"
        
        Returns:
            Dictionary with extracted parameters
        """
        params = {}
        
        # Split by "Negative prompt:" to separate positive and negative
        parts = params_text.split("Negative prompt:")
        if parts:
            params["prompt"] = parts[0].strip()
        
        if len(parts) > 1:
            # Split by first comma after negative prompt
            remaining = parts[1]
            neg_prompt_match = remaining.split(",", 1)
            params["negative_prompt"] = neg_prompt_match[0].strip()
            
            if len(neg_prompt_match) > 1:
                # Parse remaining parameters
                param_str = neg_prompt_match[1]
                for param_part in param_str.split(","):
                    if ":" in param_part:
                        key, value = param_part.split(":", 1)
                        params[key.strip().lower()] = value.strip()
        
        return params
    
    def calculate_file_hash(self, file_path: str, method: str = "SHA256") -> Optional[str]:
        """
        Calculate hash of model file
        
        Args:
            file_path: Path to model file
            method: Hash method - "SHA256" or "AUTOV2"
        
        Returns:
            Hex digest of file hash
        """
        try:
            if method == "SHA256":
                hash_obj = hashlib.sha256()
            elif method == "AUTOV2":
                # AUTOV2 is SHA256 of first 8MB
                hash_obj = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    hash_obj.update(f.read(8 * 1024 * 1024))
                return hash_obj.hexdigest()[:10].upper()
            else:
                raise ValueError(f"Unknown hash method: {method}")
            
            # Calculate full SHA256
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate file hash: {e}")
            return None


class AsyncCivitaiFetcher:
    """Thread-safe async fetcher for Civitai metadata"""
    
    def __init__(self, token: Optional[str] = None):
        self.integration = CivitaiIntegration(token)
        self.callbacks = {}
    
    def fetch_async(self, civitai_url: str, callback: callable, error_callback: callable = None):
        """
        Fetch metadata asynchronously
        
        Args:
            civitai_url: Civitai model URL
            callback: Function to call with (CivitaiMetadata) on success
            error_callback: Function to call with (error_message) on error
        """
        def fetch_thread():
            try:
                model_id, version_id = self.integration.extract_civitai_ids_from_url(civitai_url)
                
                if not model_id:
                    raise ValueError("Could not extract model ID from URL")
                
                metadata = self.integration.fetch_model_metadata(model_id, version_id)
                
                if metadata:
                    callback(metadata)
                else:
                    if error_callback:
                        error_callback("Failed to fetch metadata")
            except Exception as e:
                logger.error(f"Async fetch error: {e}")
                if error_callback:
                    error_callback(str(e))
        
        thread = threading.Thread(target=fetch_thread, daemon=True)
        thread.start()
