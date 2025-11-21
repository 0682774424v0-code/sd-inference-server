"""
TEST_EASY Colab Server
=======================

Цей скрипт розраховано на запуск у Google Colab.
Запустіть цей файл як notebook у Colab та отримайте публічне посилання для клієнта.

Встановлення:
1. Створіть новий Colab notebook
2. Завантажте цей файл як notebook (або скопіюйте код)
3. Запустіть клітинки по порядку
4. Отримайте URL та поділіться з клієнтом
"""

# ============================================================================
# 📦 КЛІТИНКА 1: Встановлення залежностей
# ============================================================================

# !pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# !pip install diffusers transformers accelerate safetensors pyngrok flask flask-cors pillow

# ============================================================================
# 📦 КЛІТИНКА 2: Імпорти та налаштування
# ============================================================================

import os
import sys
import torch
import json
from pathlib import Path
from PIL import Image
import base64
import io
from typing import Dict, Optional

# Для Flask сервера
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest

# Для ngrok тунелю
try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None
    print("⚠️  ngrok не встановлено")

# Друкуємо інформацію про обладнання
print("=" * 50)
print("🎨 TEST_EASY Colab Server")
print("=" * 50)
print(f"✅ GPU доступна: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ GPU модель: {torch.cuda.get_device_name(0)}")
    print(f"✅ CUDA версія: {torch.version.cuda}")

# ============================================================================
# 🔧 КЛІТИНКА 3: Завантажити easy_wrapper.py
# ============================================================================

# Завантажимо код з TEST_EASY/server/easy_wrapper.py
# Для простоти, ми вбудуємо код тут

from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionImg2ImgPipeline,
    StableDiffusionInpaintPipeline,
)

class SimpleGenerator:
    """Спрощена версія генератора"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.txt2img_pipeline = None
        self.img2img_pipeline = None
        self.inpaint_pipeline = None
        self.current_checkpoint = None
    
    def _load_checkpoint(self, checkpoint_name: str):
        """Завантажити checkpoint"""
        if self.current_checkpoint == checkpoint_name:
            return
        
        print(f"📦 Завантажуємо: {checkpoint_name}")
        
        # Дефолтні checkpoint'и
        checkpoints = {
            "sd15": "runwayml/stable-diffusion-v1-5",
            "sd21": "stabilityai/stable-diffusion-2-1",
            "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
        }
        
        model_id = checkpoints.get(checkpoint_name, checkpoint_name)
        
        self.txt2img_pipeline = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=self.dtype,
            safety_checker=None,
        ).to(self.device)
        
        self.txt2img_pipeline.enable_attention_slicing()
        self.current_checkpoint = checkpoint_name
        print(f"✅ Checkpoint готовий: {checkpoint_name}")
    
    def txt2img(self, prompt, negative_prompt="", checkpoint="sd15", width=512, height=512, steps=20, scale=7.5, seed=-1):
        """txt2img генерація"""
        self._load_checkpoint(checkpoint)
        
        if seed >= 0:
            generator = torch.Generator(self.device).manual_seed(seed)
        else:
            generator = None
        
        with torch.no_grad():
            result = self.txt2img_pipeline(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=steps,
                guidance_scale=scale,
                generator=generator,
            )
        
        return result.images[0]
    
    def img2img(self, prompt, image_pil, negative_prompt="", checkpoint="sd15", strength=0.75, steps=20, scale=7.5, seed=-1):
        """img2img генерація"""
        self._load_checkpoint(checkpoint)
        
        if self.img2img_pipeline is None:
            self.img2img_pipeline = StableDiffusionImg2ImgPipeline(
                **self.txt2img_pipeline.components
            ).to(self.device)
        
        if seed >= 0:
            generator = torch.Generator(self.device).manual_seed(seed)
        else:
            generator = None
        
        with torch.no_grad():
            result = self.img2img_pipeline(
                prompt=prompt,
                image=image_pil,
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=scale,
                generator=generator,
                negative_prompt=negative_prompt,
            )
        
        return result.images[0]
    
    def inpaint(self, prompt, image_pil, mask_pil, negative_prompt="", checkpoint="sd15", steps=20, scale=7.5, seed=-1):
        """inpaint генерація"""
        self._load_checkpoint(checkpoint)
        
        if self.inpaint_pipeline is None:
            self.inpaint_pipeline = StableDiffusionInpaintPipeline(
                **self.txt2img_pipeline.components
            ).to(self.device)
        
        if seed >= 0:
            generator = torch.Generator(self.device).manual_seed(seed)
        else:
            generator = None
        
        mask_pil = mask_pil.resize(image_pil.size)
        
        with torch.no_grad():
            result = self.inpaint_pipeline(
                prompt=prompt,
                image=image_pil,
                mask_image=mask_pil,
                num_inference_steps=steps,
                guidance_scale=scale,
                generator=generator,
                negative_prompt=negative_prompt,
            )
        
        return result.images[0]

# Ініціалізація генератора
generator = SimpleGenerator()

# ============================================================================
# 🌐 КЛІТИНКА 4: Flask сервер
# ============================================================================

app = Flask(__name__)
CORS(app)

def image_to_base64(image):
    """Конвертувати PIL Image в base64"""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(img_base64):
    """Конвертувати base64 в PIL Image"""
    img_data = base64.b64decode(img_base64)
    return Image.open(io.BytesIO(img_data))

@app.route('/status', methods=['GET'])
def status():
    """Статус сервера"""
    return jsonify({
        'status': 'ready',
        'device': generator.device,
        'gpu_available': torch.cuda.is_available(),
        'current_checkpoint': generator.current_checkpoint,
    })

@app.route('/txt2img', methods=['POST'])
def txt2img_endpoint():
    """txt2img endpoint"""
    try:
        data = request.json
        
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        checkpoint = data.get('checkpoint', 'sd15')
        width = data.get('width', 512)
        height = data.get('height', 512)
        steps = data.get('steps', 20)
        scale = data.get('scale', 7.5)
        seed = data.get('seed', -1)
        
        print(f"🎨 txt2img: {prompt[:50]}...")
        
        image = generator.txt2img(
            prompt=prompt,
            negative_prompt=negative_prompt,
            checkpoint=checkpoint,
            width=width,
            height=height,
            steps=steps,
            scale=scale,
            seed=seed,
        )
        
        img_base64 = image_to_base64(image)
        
        return jsonify({
            'success': True,
            'image': img_base64,
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/img2img', methods=['POST'])
def img2img_endpoint():
    """img2img endpoint"""
    try:
        data = request.json
        
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        image_base64 = data.get('image', '')
        checkpoint = data.get('checkpoint', 'sd15')
        strength = data.get('strength', 0.75)
        steps = data.get('steps', 20)
        scale = data.get('scale', 7.5)
        seed = data.get('seed', -1)
        
        image = base64_to_image(image_base64)
        
        print(f"🖼️  img2img: {prompt[:50]}...")
        
        result_image = generator.img2img(
            prompt=prompt,
            image_pil=image,
            negative_prompt=negative_prompt,
            checkpoint=checkpoint,
            strength=strength,
            steps=steps,
            scale=scale,
            seed=seed,
        )
        
        img_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'image': img_base64,
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/inpaint', methods=['POST'])
def inpaint_endpoint():
    """inpaint endpoint"""
    try:
        data = request.json
        
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        image_base64 = data.get('image', '')
        mask_base64 = data.get('mask', '')
        checkpoint = data.get('checkpoint', 'sd15')
        steps = data.get('steps', 20)
        scale = data.get('scale', 7.5)
        seed = data.get('seed', -1)
        
        image = base64_to_image(image_base64)
        mask = base64_to_image(mask_base64)
        
        print(f"🎭 inpaint: {prompt[:50]}...")
        
        result_image = generator.inpaint(
            prompt=prompt,
            image_pil=image,
            mask_pil=mask,
            negative_prompt=negative_prompt,
            checkpoint=checkpoint,
            steps=steps,
            scale=scale,
            seed=seed,
        )
        
        img_base64 = image_to_base64(result_image)
        
        return jsonify({
            'success': True,
            'image': img_base64,
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# 🚀 КЛІТИНКА 5: Запустити сервер
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 Запускаємо Flask сервер")
    print("=" * 50)
    
    # Використовуємо ngrok для публічного доступу
    if ngrok:
        print("\n🌐 Встановлюємо ngrok туннель...")
        
        # Запустити Flask локально
        from threading import Thread
        
        def run_app():
            app.run(port=5000, debug=False, use_reloader=False)
        
        thread = Thread(target=run_app, daemon=True)
        thread.start()
        
        # Встановити ngrok туннель
        public_url = ngrok.connect(5000)
        
        print(f"\n✅ Сервер запущено!")
        print(f"✅ Публічне посилання: {public_url}")
        print(f"\n📌 Використовуйте це посилання у клієнті:")
        print(f"   {public_url}")
        
        # Тримати сервер живим
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n❌ Сервер зупинено")
    else:
        # Запустити без ngrok
        print("⚠️  ngrok не встановлено. Запускаємо локально...")
        app.run(host='0.0.0.0', port=5000, debug=False)
