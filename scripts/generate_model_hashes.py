#!/usr/bin/env python3
"""
Script to scan model directories and generate hashes for all models
Usage: python generate_model_hashes.py [--models-dir models] [--metadata-dir model_metadata]
"""

import os
import sys
import argparse
import json
from pathlib import Path
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import model_metadata


def get_model_type_from_path(model_path: str) -> str:
    """Determine model type from directory structure"""
    parts = Path(model_path).parts
    
    if 'LoRA' in parts or 'lora' in parts:
        return 'LORA'
    elif 'SD' in parts or 'Checkpoint' in parts:
        return 'UNET'
    elif 'SR' in parts or 'Upscaler' in parts:
        return 'UPSCALER'
    elif 'CN' in parts or 'ControlNet' in parts:
        return 'CONTROLNET'
    elif 'TI' in parts or 'Embedding' in parts:
        return 'TI'
    elif 'VAE' in parts:
        return 'VAE'
    elif 'HN' in parts:
        return 'DETAILER'
    else:
        # Try to infer from file extension or directory name
        dir_name = os.path.basename(os.path.dirname(model_path)).lower()
        if 'lora' in dir_name:
            return 'LORA'
        elif 'checkpoint' in dir_name or 'model' in dir_name:
            return 'UNET'
        elif 'upscal' in dir_name:
            return 'UPSCALER'
        elif 'control' in dir_name:
            return 'CONTROLNET'
        elif 'embedding' in dir_name or 'textual' in dir_name:
            return 'TI'
        elif 'vae' in dir_name:
            return 'VAE'
        return 'UNKNOWN'


def scan_models_directory(models_dir: str) -> dict:
    """Scan models directory and return list of model files"""
    models = {}
    
    supported_extensions = {'.safetensors', '.ckpt', '.pt', '.pth', '.bin'}
    
    for root, dirs, files in os.walk(models_dir):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if os.path.splitext(file)[1].lower() in supported_extensions:
                model_path = os.path.join(root, file)
                model_type = get_model_type_from_path(model_path)
                model_name = os.path.splitext(file)[0]
                
                if model_type not in models:
                    models[model_type] = []
                
                models[model_type].append({
                    'name': model_name,
                    'path': model_path,
                    'type': model_type
                })
    
    return models


def generate_hashes(models_dir: str = 'models', metadata_dir: str = 'model_metadata', 
                   skip_existing: bool = True, preview_dir: str = 'model_previews'):
    """Generate hashes for all models in the models directory"""
    
    print(f"Scanning models directory: {models_dir}")
    
    manager = model_metadata.get_manager(models_dir, metadata_dir)
    models = scan_models_directory(models_dir)
    
    total_models = sum(len(v) for v in models.values())
    processed = 0
    skipped = 0
    
    with tqdm(total=total_models, desc="Generating hashes") as pbar:
        for model_type, model_list in models.items():
            for model_info in model_list:
                model_name = model_info['name']
                model_path = model_info['path']
                model_type = model_info['type']
                
                # Check if metadata already exists
                existing_metadata = manager.get_metadata(model_name, model_type)
                
                if skip_existing and existing_metadata:
                    pbar.update(1)
                    skipped += 1
                    continue
                
                try:
                    # Check for preview image
                    preview_path = None
                    if os.path.exists(preview_dir):
                        for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                            potential_preview = os.path.join(
                                preview_dir, 
                                f"{model_name}{ext}"
                            )
                            if os.path.exists(potential_preview):
                                preview_path = potential_preview
                                break
                    
                    # Create/update metadata
                    metadata = manager.create_or_update_metadata(
                        model_path=model_path,
                        model_type=model_type,
                        preview_path=preview_path,
                        description=f"{model_type} model",
                        base_model="Unknown"
                    )
                    
                    processed += 1
                    
                except Exception as e:
                    print(f"Error processing {model_name}: {e}")
                
                pbar.update(1)
    
    print(f"\n✅ Hash generation complete!")
    print(f"   Processed: {processed} models")
    print(f"   Skipped: {skipped} models")
    print(f"   Metadata directory: {metadata_dir}")
    
    # Print statistics
    print("\n📊 Model Statistics:")
    for model_type, model_list in sorted(models.items()):
        print(f"   {model_type}: {len(model_list)} models")


def export_metadata_as_json(metadata_dir: str = 'model_metadata', 
                           output_file: str = 'models_export.json'):
    """Export all model metadata to a single JSON file"""
    
    manager = model_metadata.get_manager(metadata_dir=metadata_dir)
    
    export_data = {}
    for key, meta in manager.metadata_cache.items():
        model_type, name = key.split(':', 1)
        if model_type not in export_data:
            export_data[model_type] = {}
        export_data[model_type][name] = meta.to_dict()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Metadata exported to {output_file}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate hashes for all models in the models directory'
    )
    parser.add_argument(
        '--models-dir',
        default='models',
        help='Path to models directory (default: models)'
    )
    parser.add_argument(
        '--metadata-dir',
        default='model_metadata',
        help='Path to metadata directory (default: model_metadata)'
    )
    parser.add_argument(
        '--preview-dir',
        default='model_previews',
        help='Path to preview images directory (default: model_previews)'
    )
    parser.add_argument(
        '--no-skip',
        action='store_true',
        help='Regenerate hashes for all models, including existing ones'
    )
    parser.add_argument(
        '--export',
        metavar='FILE',
        help='Export all metadata to a JSON file'
    )
    
    args = parser.parse_args()
    
    # Generate hashes
    generate_hashes(
        models_dir=args.models_dir,
        metadata_dir=args.metadata_dir,
        preview_dir=args.preview_dir,
        skip_existing=not args.no_skip
    )
    
    # Export if requested
    if args.export:
        export_metadata_as_json(args.metadata_dir, args.export)
