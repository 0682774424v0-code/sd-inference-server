"""
easy_wrapper.py - Спрощена версія wrapper для TEST_EASY

Цей файл містить основний функціонал для:
- txt2img
- img2img  
- inpaint

Спеціально оптимізовано для Google Colab та простоти використання
"""

import torch
import io
import base64
import json
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from PIL import Image
import numpy as np

try:
    from diffusers import (
        StableDiffusionPipeline,
        StableDiffusionImg2ImgPipeline,
        StableDiffusionInpaintPipeline,
        DPMSolverMultistepScheduler
    )
    HAVE_DIFFUSERS = True
except ImportError:
    HAVE_DIFFUSERS = False
    print("⚠️  diffusers не встановлено. Встановіть: pip install diffusers")

from PIL import ImageDraw


class EasyConfig:
    """Конфіг для простої версії"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.checkpoint_path = "models/checkpoints"
        self.lora_path = "models/lora"
        self.upscaler_path = "models/upscalers"
        
        # Параметри за замовчуванням
        self.default_width = 512
        self.default_height = 512
        self.default_steps = 20
        self.default_scale = 7.5
        self.default_seed = -1
        
    def to_dict(self):
        return {
            "device": self.device,
            "dtype": str(self.dtype),
            "checkpoint_path": self.checkpoint_path,
            "lora_path": self.lora_path,
            "default_width": self.default_width,
            "default_height": self.default_height,
            "default_steps": self.default_steps,
            "default_scale": self.default_scale,
        }


class EasyGenerator:
    """Основний генератор зображень"""
    
    def __init__(self, config: Optional[EasyConfig] = None):
        self.config = config or EasyConfig()
        self.device = self.config.device
        self.dtype = self.config.dtype
        
        # Pipelines (будуть завантажені за потреби)
        self.txt2img_pipeline = None
        self.img2img_pipeline = None
        self.inpaint_pipeline = None
        self.current_checkpoint = None
        
    def _load_checkpoint(self, checkpoint_name: str):
        """Завантажити checkpoint"""
        if not HAVE_DIFFUSERS:
            raise RuntimeError("diffusers не встановлено")
            
        if self.current_checkpoint == checkpoint_name:
            return  # Уже завантажено
            
        print(f"📦 Завантажуємо checkpoint: {checkpoint_name}")
        
        try:
            # Основні checkpoint'и з HuggingFace
            checkpoint_ids = {
                "sd15": "runwayml/stable-diffusion-v1-5",
                "sd21": "stabilityai/stable-diffusion-2-1",
                "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
                "epic": "gsdf/Counterfeit-V2.5",
            }
            
            model_id = checkpoint_ids.get(checkpoint_name, checkpoint_name)
            
            # Завантажити txt2img pipeline
            self.txt2img_pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=self.dtype,
                safety_checker=None,
                requires_safety_checker=False
            ).to(self.device)
            
            # Оптимізація для Colab
            self.txt2img_pipeline.enable_attention_slicing()
            
            self.current_checkpoint = checkpoint_name
            print(f"✅ Checkpoint завантажено: {checkpoint_name}")
            
        except Exception as e:
            print(f"❌ Помилка завантаження checkpoint: {e}")
            raise
    
    def txt2img(
        self,
        prompt: str,
        negative_prompt: str = "",
        checkpoint: str = "sd15",
        width: int = 512,
        height: int = 512,
        steps: int = 20,
        scale: float = 7.5,
        seed: int = -1,
        lora: Optional[str] = None,
        callback=None
    ) -> Image.Image:
        """
        Генерація зображення з тексту
        
        Args:
            prompt: Опис зображення
            negative_prompt: Що не робити
            checkpoint: Назва checkpoint'а
            width: Ширина
            height: Висота
            steps: Кількість кроків
            scale: Сила впливу промпта (guidance scale)
            seed: Насіння (-1 = випадкове)
            lora: LoRA для використання
            callback: Функція зворотного виклику
            
        Returns:
            PIL Image
        """
        
        # Завантажити checkpoint
        self._load_checkpoint(checkpoint)
        
        # Встановити seed
        if seed >= 0:
            torch.manual_seed(seed)
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        print(f"🎨 Генерую: {prompt[:50]}...")
        
        # Генерація
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
        
        image = result.images[0]
        print(f"✅ Зображення готово!")
        
        return image
    
    def img2img(
        self,
        prompt: str,
        image: Image.Image,
        negative_prompt: str = "",
        checkpoint: str = "sd15",
        strength: float = 0.75,
        steps: int = 20,
        scale: float = 7.5,
        seed: int = -1,
        lora: Optional[str] = None,
        callback=None
    ) -> Image.Image:
        """
        Модифікація зображення з тексту
        
        Args:
            prompt: Описання змін
            image: Вхідне зображення (PIL Image)
            strength: Сила впливу (0.0-1.0)
            callback: Функція зворотного виклику
            
        Returns:
            PIL Image
        """
        
        self._load_checkpoint(checkpoint)
        
        # Завантажити img2img pipeline
        if self.img2img_pipeline is None:
            self.img2img_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                self.txt2img_pipeline.model_id,
                torch_dtype=self.dtype,
                safety_checker=None,
            ).to(self.device)
        
        if seed >= 0:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        print(f"🖼️  Модифікую зображення: {prompt[:50]}...")
        
        with torch.no_grad():
            result = self.img2img_pipeline(
                prompt=prompt,
                image=image.convert("RGB"),
                strength=strength,
                num_inference_steps=steps,
                guidance_scale=scale,
                generator=generator,
                negative_prompt=negative_prompt,
            )
        
        image = result.images[0]
        print(f"✅ Зображення готово!")
        
        return image
    
    def inpaint(
        self,
        prompt: str,
        image: Image.Image,
        mask: Image.Image,
        negative_prompt: str = "",
        checkpoint: str = "sd15",
        steps: int = 20,
        scale: float = 7.5,
        seed: int = -1,
        lora: Optional[str] = None,
        callback=None
    ) -> Image.Image:
        """
        Редагування зображення через маску
        
        Args:
            prompt: Опис для редагування
            image: Вхідне зображення
            mask: Маска (білий = редагувати, чорний = залишити)
            callback: Функція зворотного виклику
            
        Returns:
            PIL Image
        """
        
        self._load_checkpoint(checkpoint)
        
        if self.inpaint_pipeline is None:
            self.inpaint_pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                self.txt2img_pipeline.model_id,
                torch_dtype=self.dtype,
                safety_checker=None,
            ).to(self.device)
        
        if seed >= 0:
            generator = torch.Generator(device=self.device).manual_seed(seed)
        else:
            generator = None
        
        print(f"🎭 Редагую через маску: {prompt[:50]}...")
        
        # Переконатися, що маска має правильний розмір
        mask = mask.resize(image.size)
        image = image.convert("RGB")
        
        with torch.no_grad():
            result = self.inpaint_pipeline(
                prompt=prompt,
                image=image,
                mask_image=mask,
                num_inference_steps=steps,
                guidance_scale=scale,
                generator=generator,
                negative_prompt=negative_prompt,
            )
        
        image = result.images[0]
        print(f"✅ Редагування готово!")
        
        return image
    
    def get_status(self) -> Dict:
        """Отримати статус генератора"""
        return {
            "device": self.device,
            "dtype": str(self.dtype),
            "current_checkpoint": self.current_checkpoint,
            "available_memory": torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None,
            "config": self.config.to_dict()
        }


class ImageUtils:
    """Утиліти для роботи з зображеннями"""
    
    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """Конвертувати PIL Image в base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return img_str
    
    @staticmethod
    def base64_to_image(img_str: str) -> Image.Image:
        """Конвертувати base64 в PIL Image"""
        img_data = base64.b64decode(img_str)
        image = Image.open(io.BytesIO(img_data))
        return image
    
    @staticmethod
    def create_mask(image_size: Tuple[int, int], brush_strokes: List) -> Image.Image:
        """
        Створити маску з чорно-білого зображення
        brush_strokes: список кортежів (x, y, radius, type='draw' або 'erase')
        """
        mask = Image.new("L", image_size, 0)  # Чорна маска
        draw = ImageDraw.Draw(mask)
        
        for stroke in brush_strokes:
            x, y, radius, stroke_type = stroke
            color = 255 if stroke_type == "draw" else 0
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        
        return mask
    
    @staticmethod
    def resize_image(image: Image.Image, max_size: int = 768) -> Image.Image:
        """Змінити розмір зображення збережено aspect ratio"""
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        return image


# Приклад використання
if __name__ == "__main__":
    print("🎨 TEST_EASY Generator v1.0")
    
    # Ініціалізація
    config = EasyConfig()
    gen = EasyGenerator(config)
    
    print("\n📊 Статус:")
    print(json.dumps(gen.get_status(), indent=2))
    
    print("\n✅ Генератор готовий до використання!")
    print("Використовуйте: gen.txt2img(), gen.img2img(), gen.inpaint()")
