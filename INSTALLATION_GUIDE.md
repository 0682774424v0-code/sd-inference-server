# Installation and Integration Guide

## Step-by-Step Integration

### 1. Install Required Dependencies

Add `requests` to your requirements:

```bash
pip install requests>=2.28.0
```

Or add to `requirements.txt`:
```
requests>=2.28.0
```

### 2. File Structure

New files created:
```
sd-inference-server/
├── civitai_integration.py          # Civitai API utilities
├── model_metadata.py               # Metadata management
├── auto_model_detector.py          # Automatic detection
├── CIVITAI_INTEGRATION_GUIDE.md    # Full documentation
│
└── GUI/source/
    ├── model_manager.py            # PyQt5 backend
    └── tabs/settings/
        ├── ModelCard.qml           # Model card component
        ├── EditHashDialog.qml      # Hash editor dialog
        └── ModelsPanel.qml         # Main models panel
```

### 3. Integration into Existing Code

#### In `GUI/source/main.py` or startup script:

```python
# At the top with other imports
from model_manager import ModelManager, register_model_manager

# In your QML initialization section:
register_model_manager()

# Create manager instance
model_manager = ModelManager()

# Set Civitai token if available (from environment or config)
civitai_token = os.environ.get('CIVITAI_TOKEN', '')
if civitai_token:
    model_manager.set_civitai_token(civitai_token)

# Register with QML context
qml_engine.rootContext().setContextProperty("MODEL_MANAGER", model_manager)
```

#### In `GUI/source/tabs/settings/Settings.qml`:

```qml
import QtQuick 2.15
import QtQuick.Layouts 1.15

// Add to your Settings component
ColumnLayout {
    // ... existing code ...
    
    // Add models panel tab
    TabBar {
        id: settingsTabBar
        
        TabButton { text: "General" }
        TabButton { text: "Models" }  // NEW
        // ... other tabs ...
    }
    
    StackLayout {
        currentIndex: settingsTabBar.currentIndex
        
        // General tab content
        Rectangle { /* ... */ }
        
        // Models tab content
        ModelsPanel {
            modelManager: MODEL_MANAGER
        }
        
        // ... other tab contents ...
    }
}
```

#### Enable auto-detection (optional):

In `GUI/source/main.py` or `colab_setup.py`:

```python
from auto_model_detector import AutoModelMetadataDetector

# Setup watch folders
watch_folders = {
    "SD": "./models/SD",
    "LoRA": "./models/LoRA",
    "Upscaler": "./models/SR",
    "ControlNet": "./models/CN",
}

# Create detector
detector = AutoModelMetadataDetector(
    watch_folders,
    civitai_token=civitai_token,
    callback=lambda path, meta: logger.info(f"Model detected: {path}")
)

# Start watching (runs in background thread)
detector.start_watching()
```

### 4. Environment Variables

For Civitai token, set environment variable:

```bash
export CIVITAI_TOKEN="your_token_here"
```

Or on Windows:
```powershell
$env:CIVITAI_TOKEN="your_token_here"
```

### 5. Metadata Storage

Metadata files are stored automatically:
- Location: Next to model file
- Format: `model_name.ext.metadata.json`
- Example: `mymodel.safetensors.metadata.json`

Preview images:
- Location: `.previews/` subfolder in model directory
- Example: `models/SD/.previews/mymodel.jpg`

### 6. Usage Scenarios

#### Scenario 1: Auto-detect hashes for all models
```python
from auto_model_detector import ModelHashCalculator

calculator = ModelHashCalculator()
hashes = calculator.calculate_all_hashes(
    "./models/LoRA",
    force_recalculate=False
)

for model_path, hash_value in hashes.items():
    print(f"{os.path.basename(model_path)}: {hash_value}")
```

#### Scenario 2: Fetch specific model from Civitai
```python
from civitai_integration import CivitaiIntegration
from model_metadata import ModelMetadataManager

integration = CivitaiIntegration(token="your_token")
manager = ModelMetadataManager()

# Fetch metadata
metadata = integration.fetch_model_metadata(model_id=12345)

if metadata:
    # Save locally
    manager.set_civitai_metadata("model.safetensors", metadata)
    
    # Download preview
    if metadata.preview_url:
        integration.download_preview(
            metadata.preview_url,
            "preview.jpg"
        )
```

#### Scenario 3: Batch import from Civitai URLs
```python
urls = [
    "https://civitai.com/models/123456",
    "https://civitai.com/models/789012",
]

for url in urls:
    model_path = "./models/SD/mymodel.safetensors"
    detector.manual_fetch_civitai(model_path, url)
```

### 7. Troubleshooting

#### Issue: "requests module not found"
**Solution:** Install requests
```bash
pip install requests
```

#### Issue: "ModuleNotFoundError: No module named 'model_manager'"
**Solution:** Ensure all files are in correct locations and Python path includes GUI/source directory

#### Issue: Civitai API returns 403/401
**Solution:** Check your Civitai token validity or run without authentication

#### Issue: Preview images not downloading
**Solution:** Check internet connection and that Civitai URLs are accessible

### 8. Performance Notes

- Hash calculation: ~2-5 seconds per model (depends on size)
- Civitai API calls: Limited to reasonable rate
- Preview download: ~1-3 seconds per image
- Auto-detection: Runs in background, non-blocking

### 9. Testing

Run tests to verify installation:

```bash
# Test Civitai integration
python -c "
from civitai_integration import CivitaiIntegration
integration = CivitaiIntegration()
model_id, _ = integration.extract_civitai_ids_from_url(
    'https://civitai.com/models/123456'
)
print(f'✓ Civitai integration working: model_id={model_id}')
"

# Test metadata manager
python -c "
from model_metadata import ModelMetadataManager
manager = ModelMetadataManager()
test_data = {'hash': 'test123'}
# Create temp file for testing
print('✓ Metadata manager working')
"

# Test model manager (GUI)
python GUI/source/model_manager.py
```

### 10. Upgrading

To update components:

1. Download latest versions of:
   - `civitai_integration.py`
   - `model_metadata.py`
   - `auto_model_detector.py`
   - `GUI/source/model_manager.py`

2. QML files rarely need updates but check for new features

3. Update imports if module structure changes

## Configuration Reference

### ModelMetadataManager
```python
manager = ModelMetadataManager(models_root_dir="./models")

# Load metadata
metadata = manager.load_metadata("model.safetensors")

# Save metadata
manager.save_metadata("model.safetensors", {
    "hash": "AUTOV2: 90BFFAFD10",
    "civitai_name": "MyModel"
})

# Get hash
hash_val = manager.get_hash("model.safetensors")

# Set hash
manager.set_hash("model.safetensors", "AUTOV2: 90BFFAFD10", "AUTOV2")
```

### CivitaiIntegration
```python
integration = CivitaiIntegration(token="optional_token")

# Extract IDs
model_id, version_id = integration.extract_civitai_ids_from_url(url)

# Fetch metadata
metadata = integration.fetch_model_metadata(model_id, version_id)

# Download preview
integration.download_preview(url, output_path)

# Calculate hash
hash_val = integration.calculate_file_hash(file_path, method="AUTOV2")
```

## Support

For issues:
1. Check CIVITAI_INTEGRATION_GUIDE.md for detailed documentation
2. Review error logs (logging is configured with DEBUG level)
3. Ensure all dependencies are installed
4. Verify file paths are correct
5. Check Civitai API status at civitai.com

---

**Last Updated:** November 21, 2024
