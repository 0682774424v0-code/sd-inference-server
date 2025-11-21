"""
Google Colab Configuration Example
Shows how to integrate Civitai metadata system into Colab server
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# COLAB SPECIFIC SETUP
# ============================================================================

def setup_colab_environment():
    """Setup paths and environment for Colab"""
    
    # Mount Google Drive
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        colab_root = '/content/drive/MyDrive/sd-inference'
        logger.info(f"Mounted Google Drive at {colab_root}")
    except:
        colab_root = '/content'
        logger.warning("Running without Google Drive mount")
    
    return colab_root


def setup_model_folders(base_path):
    """Setup model folder structure"""
    
    folders = {
        'SD': f'{base_path}/models/SD',
        'LoRA': f'{base_path}/models/LoRA',
        'ControlNet': f'{base_path}/models/CN',
        'Upscaler': f'{base_path}/models/SR',
        'Embedding': f'{base_path}/models/TI',
        'Detailers': f'{base_path}/models/HN',
    }
    
    for folder_type, folder_path in folders.items():
        Path(folder_path).mkdir(parents=True, exist_ok=True)
        Path(f'{folder_path}/.previews').mkdir(parents=True, exist_ok=True)
        logger.info(f"Setup {folder_type} folder: {folder_path}")
    
    return folders


def setup_civitai_integration(root_path, civitai_token=None):
    """Initialize Civitai integration"""
    
    # Add to path if needed
    if root_path not in sys.path:
        sys.path.insert(0, root_path)
    
    # Import modules
    try:
        from civitai_integration import CivitaiIntegration
        from model_metadata import ModelMetadataManager
        from auto_model_detector import AutoModelMetadataDetector
        
        logger.info("✓ Civitai integration modules loaded")
    except ImportError as e:
        logger.error(f"Failed to import Civitai modules: {e}")
        return None
    
    # Get token from environment if not provided
    if not civitai_token:
        civitai_token = os.environ.get('CIVITAI_TOKEN', '')
    
    if civitai_token:
        logger.info("✓ Civitai token found")
    else:
        logger.warning("⚠ No Civitai token provided (optional)")
    
    # Initialize integration
    integration = CivitaiIntegration(token=civitai_token)
    manager = ModelMetadataManager()
    
    return {
        'integration': integration,
        'manager': manager,
        'token': civitai_token
    }


def setup_gui_backend(civitai_system, watch_folders):
    """Setup PyQt5 GUI backend"""
    
    try:
        from gui.source.model_manager import ModelManager, register_model_manager
        
        # Register QML types
        register_model_manager()
        
        # Create manager
        model_manager = ModelManager()
        
        # Set Civitai token
        if civitai_system and civitai_system.get('token'):
            model_manager.set_civitai_token(civitai_system['token'])
        
        logger.info("✓ GUI backend initialized")
        return model_manager
    
    except Exception as e:
        logger.error(f"Failed to setup GUI backend: {e}")
        return None


def setup_auto_detection(civitai_system, watch_folders):
    """Setup automatic model detection"""
    
    try:
        from auto_model_detector import AutoModelMetadataDetector
        
        def on_model_detected(model_path, metadata):
            logger.info(f"Auto-detected model: {os.path.basename(model_path)}")
            logger.info(f"  Hash: {metadata.get('hash', 'N/A')}")
            logger.info(f"  Type: {metadata.get('model_type', 'N/A')}")
        
        detector = AutoModelMetadataDetector(
            watch_folders=watch_folders,
            civitai_token=civitai_system['token'] if civitai_system else None,
            callback=on_model_detected
        )
        
        # Start watching in background
        detector.start_watching()
        logger.info("✓ Auto-detection enabled")
        
        return detector
    
    except Exception as e:
        logger.error(f"Failed to setup auto-detection: {e}")
        return None


# ============================================================================
# COLAB NOTEBOOK EXAMPLE
# ============================================================================

COLAB_SETUP_EXAMPLE = """
# Google Colab Cell 1: Install dependencies
!pip install requests>=2.28.0
!pip install PyQt5==5.15.7

# Google Colab Cell 2: Clone or upload project
!git clone https://github.com/your-repo/sd-inference-server.git /content/sd-server
cd /content/sd-server

# Google Colab Cell 3: Setup environment
import os
os.environ['CIVITAI_TOKEN'] = 'your_token_here'  # Get from civitai.com/user/account

# Run setup
exec(open('colab_civitai_setup.py').read())

# Google Colab Cell 4: Use GUI backend
model_manager.load_models_from_folder('./models/LoRA')

# Google Colab Cell 5: Fetch metadata for a model
model_manager.fetch_civitai_metadata(
    './models/LoRA/mymodel.safetensors',
    'https://civitai.com/models/123456'
)

# Google Colab Cell 6: Export all metadata
import json
metadata = model_manager.export_all_metadata('./models', 'metadata_export.json')
print(f"Exported: {metadata}")

# Google Colab Cell 7: Monitor auto-detection
import time
print("Auto-detection running in background...")
print("Check logs for detected models")
time.sleep(60)
"""


# ============================================================================
# MAIN SETUP FUNCTION
# ============================================================================

def initialize_civitai_system_for_colab():
    """Complete initialization for Colab"""
    
    print("=" * 60)
    print("Civitai Integration Setup for Google Colab")
    print("=" * 60)
    
    # 1. Setup Colab environment
    logger.info("\n[1/4] Setting up Colab environment...")
    colab_root = setup_colab_environment()
    
    # 2. Setup model folders
    logger.info("\n[2/4] Setting up model folders...")
    watch_folders = setup_model_folders(colab_root)
    
    # 3. Setup Civitai integration
    logger.info("\n[3/4] Initializing Civitai integration...")
    civitai_system = setup_civitai_integration(colab_root)
    
    # 4. Setup GUI backend
    logger.info("\n[4/4] Initializing GUI backend...")
    model_manager = setup_gui_backend(civitai_system, watch_folders)
    
    # 5. Setup auto-detection (optional)
    logger.info("\n[5/5] Enabling auto-detection...")
    auto_detector = setup_auto_detection(civitai_system, watch_folders)
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print(f"Root: {colab_root}")
    print(f"Models: {watch_folders}")
    print(f"Token: {'✓ Set' if civitai_system and civitai_system.get('token') else '✗ Not set'}")
    print(f"GUI Backend: {'✓ Ready' if model_manager else '✗ Failed'}")
    print(f"Auto-detection: {'✓ Running' if auto_detector else '✗ Disabled'}")
    print("=" * 60)
    
    return {
        'root': colab_root,
        'folders': watch_folders,
        'civitai': civitai_system,
        'model_manager': model_manager,
        'auto_detector': auto_detector
    }


# ============================================================================
# QUICK START FUNCTIONS FOR COLAB
# ============================================================================

def quick_fetch_model_metadata(model_manager, model_path, civitai_url):
    """Quick function to fetch metadata for a model"""
    logger.info(f"Fetching metadata for {os.path.basename(model_path)}...")
    model_manager.fetch_civitai_metadata(model_path, civitai_url)
    logger.info("Done!")


def quick_set_hash(model_manager, model_path, hash_value, hash_type="AUTOV2"):
    """Quick function to set hash"""
    logger.info(f"Setting hash for {os.path.basename(model_path)}: {hash_value}")
    model_manager.set_model_hash(model_path, hash_value, hash_type)
    logger.info("Done!")


def quick_export_metadata(model_manager, export_path):
    """Quick function to export metadata"""
    logger.info(f"Exporting metadata to {export_path}...")
    result = model_manager.export_all_metadata(export_path)
    logger.info(f"Result: {result}")


def quick_import_metadata(model_manager, import_path, target_folder):
    """Quick function to import metadata"""
    logger.info(f"Importing metadata from {import_path}...")
    result = model_manager.import_metadata(import_path, target_folder)
    logger.info(f"Result: {result}")


# ============================================================================
# ENTRYPOINT
# ============================================================================

if __name__ == "__main__":
    # Initialize system
    system = initialize_civitai_system_for_colab()
    
    # Make components globally available
    root = system['root']
    folders = system['folders']
    civitai = system['civitai']
    model_manager = system['model_manager']
    auto_detector = system['auto_detector']
    
    print("\nReady to use! Available variables:")
    print("  - root: Colab root directory")
    print("  - folders: Model folder paths")
    print("  - civitai: Civitai integration system")
    print("  - model_manager: GUI backend manager")
    print("  - auto_detector: Auto-detection system")
    print("\nQuick functions available:")
    print("  - quick_fetch_model_metadata()")
    print("  - quick_set_hash()")
    print("  - quick_export_metadata()")
    print("  - quick_import_metadata()")
