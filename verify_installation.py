#!/usr/bin/env python3
"""
Quick Verification Script for Civitai Integration
Перевіряє що все правильно інстальовано та налаштовано
"""

import os
import sys
from pathlib import Path

def check_file_exists(path, name):
    """Перевірити чи файл існує"""
    if os.path.exists(path):
        size = os.path.getsize(path)
        print(f"✅ {name}: {path} ({size} bytes)")
        return True
    else:
        print(f"❌ {name}: {path} (НЕ ЗНАЙДЕНО)")
        return False

def main():
    print("=" * 70)
    print("Civitai Integration - Verification Checklist")
    print("=" * 70)
    
    root = os.path.dirname(os.path.abspath(__file__))
    all_good = True
    
    # Check Python modules
    print("\n📦 Python Модулі:")
    all_good &= check_file_exists(
        os.path.join(root, "civitai_integration.py"),
        "Civitai API"
    )
    all_good &= check_file_exists(
        os.path.join(root, "model_metadata.py"),
        "Metadata Manager"
    )
    all_good &= check_file_exists(
        os.path.join(root, "auto_model_detector.py"),
        "Auto Detector"
    )
    all_good &= check_file_exists(
        os.path.join(root, "colab_civitai_setup.py"),
        "Colab Setup"
    )
    
    # Check GUI modules
    print("\n🎨 GUI Модулі:")
    all_good &= check_file_exists(
        os.path.join(root, "GUI/source/model_manager.py"),
        "Model Manager Backend"
    )
    
    # Check QML components
    print("\n✨ QML Компоненти:")
    all_good &= check_file_exists(
        os.path.join(root, "GUI/source/tabs/settings/ModelCard.qml"),
        "Model Card"
    )
    all_good &= check_file_exists(
        os.path.join(root, "GUI/source/tabs/settings/EditHashDialog.qml"),
        "Edit Hash Dialog"
    )
    all_good &= check_file_exists(
        os.path.join(root, "GUI/source/tabs/settings/ModelsPanel.qml"),
        "Models Panel"
    )
    
    # Check documentation
    print("\n📚 Документація:")
    all_good &= check_file_exists(
        os.path.join(root, "CIVITAI_INTEGRATION_GUIDE.md"),
        "API Guide"
    )
    all_good &= check_file_exists(
        os.path.join(root, "INSTALLATION_GUIDE.md"),
        "Installation Guide"
    )
    all_good &= check_file_exists(
        os.path.join(root, "CIVITAI_AND_MODELS_SUMMARY.md"),
        "Summary"
    )
    all_good &= check_file_exists(
        os.path.join(root, "README_CIVITAI_INTEGRATION.md"),
        "README"
    )
    
    # Check dependencies
    print("\n🔧 Залежності:")
    try:
        import requests
        print(f"✅ requests: {requests.__version__}")
    except ImportError:
        print("❌ requests: НЕ ВСТАНОВЛЕНО (pip install requests)")
        all_good = False
    
    try:
        import PyQt5
        print(f"✅ PyQt5: {PyQt5.__version__ if hasattr(PyQt5, '__version__') else 'installed'}")
    except ImportError:
        print("⚠️ PyQt5: НЕ ВСТАНОВЛЕНО (використовується тільки для GUI)")
    
    # Summary
    print("\n" + "=" * 70)
    if all_good:
        print("✅ ВСЕ ПЕРЕВІРКИ ПРОЙДЕНО!")
        print("\nДалі:")
        print("1. pip install requests>=2.28.0")
        print("2. Прочитайте INSTALLATION_GUIDE.md")
        print("3. Інтегруйте компоненти в ваш код")
        print("4. Встановіть Civitai токен (опціонально)")
        print("5. Почніть користуватися системою!")
    else:
        print("❌ ДЕЯКІ ФАЙЛИ НЕ ЗНАЙДЕНІ")
        print("Перевірте що всі файли розташовані правильно")
    print("=" * 70)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
