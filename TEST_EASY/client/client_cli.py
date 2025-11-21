#!/usr/bin/env python3
"""
client_cli.py - Командний рядок клієнт для TEST_EASY

Використання:
    python client_cli.py txt2img --prompt "cute cat" --steps 30
    python client_cli.py img2img --image input.png --prompt "oil painting" --strength 0.7
    python client_cli.py inpaint --image input.png --mask mask.png --prompt "golden sunset"
"""

import argparse
import sys
import json
import base64
import time
from pathlib import Path
from datetime import datetime

import requests
from PIL import Image
import io


class EasyClientCLI:
    """CLI клієнт для TEST_EASY"""
    
    def __init__(self, server_url=None, config_file="config.json"):
        self.config_file = config_file
        self.load_config()
        
        self.server_url = server_url or self.config.get("server_url", "http://localhost:5000")
        self.session = requests.Session()
    
    def load_config(self):
        """Завантажити конфіг"""
        if Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "server_url": "http://localhost:5000",
                "default_checkpoint": "sd15",
                "default_width": 512,
                "default_height": 512,
                "default_steps": 20,
                "default_scale": 7.5,
                "timeout": 600,
            }
    
    def print_banner(self):
        """Показати банер"""
        print("""
╔════════════════════════════════════════════╗
║  🎨 TEST_EASY CLI Client                   ║
║  Simple Stable Diffusion Generation        ║
╚════════════════════════════════════════════╝
        """)
    
    def print_status(self, message):
        """Показати статус"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def txt2img(self, args):
        """Генерувати з тексту"""
        self.print_status("📝 txt2img mode")
        
        if not args.prompt:
            self.print_status("❌ Помилка: Потрібен --prompt")
            return False
        
        self.print_status(f"Промпт: {args.prompt}")
        
        params = {
            "prompt": args.prompt,
            "negative_prompt": args.negative_prompt or "",
            "checkpoint": args.checkpoint,
            "width": args.width,
            "height": args.height,
            "steps": args.steps,
            "scale": args.scale,
        }
        
        self.print_status(f"Параметри: {params}")
        self.print_status("🔄 Генерування...")
        
        try:
            response = self.session.post(
                f"{self.server_url}/txt2img",
                json=params,
                timeout=self.config.get("timeout", 600)
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.save_result(data.get('image', ''), args.output)
                    return True
                else:
                    self.print_status(f"❌ Помилка: {data.get('error', 'Unknown')}")
                    return False
            else:
                self.print_status(f"❌ HTTP Error: {response.status_code}")
                return False
        
        except requests.Timeout:
            self.print_status("❌ Помилка: Сервер не відповідає (timeout)")
            return False
        except Exception as e:
            self.print_status(f"❌ Помилка: {e}")
            return False
    
    def img2img(self, args):
        """Модифікувати зображення"""
        self.print_status("🖼️ img2img mode")
        
        if not args.image:
            self.print_status("❌ Помилка: Потрібен --image")
            return False
        
        if not Path(args.image).exists():
            self.print_status(f"❌ Помилка: Файл не знайдено: {args.image}")
            return False
        
        if not args.prompt:
            self.print_status("❌ Помилка: Потрібен --prompt")
            return False
        
        self.print_status(f"Зображення: {args.image}")
        self.print_status(f"Промпт: {args.prompt}")
        self.print_status(f"Strength: {args.strength}")
        
        image = Image.open(args.image).convert("RGB")
        image_base64 = self.image_to_base64(image)
        
        params = {
            "prompt": args.prompt,
            "negative_prompt": args.negative_prompt or "",
            "image": image_base64,
            "strength": args.strength,
            "checkpoint": args.checkpoint,
        }
        
        self.print_status("🔄 Генерування...")
        
        try:
            response = self.session.post(
                f"{self.server_url}/img2img",
                json=params,
                timeout=self.config.get("timeout", 600)
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.save_result(data.get('image', ''), args.output)
                    return True
                else:
                    self.print_status(f"❌ Помилка: {data.get('error', 'Unknown')}")
                    return False
            else:
                self.print_status(f"❌ HTTP Error: {response.status_code}")
                return False
        
        except requests.Timeout:
            self.print_status("❌ Помилка: Сервер не відповідає (timeout)")
            return False
        except Exception as e:
            self.print_status(f"❌ Помилка: {e}")
            return False
    
    def inpaint(self, args):
        """Редагувати зображення з маскою"""
        self.print_status("🎭 inpaint mode")
        
        if not args.image:
            self.print_status("❌ Помилка: Потрібен --image")
            return False
        
        if not Path(args.image).exists():
            self.print_status(f"❌ Помилка: Файл не знайдено: {args.image}")
            return False
        
        if not args.mask:
            self.print_status("❌ Помилка: Потрібен --mask")
            return False
        
        if not Path(args.mask).exists():
            self.print_status(f"❌ Помилка: Маска не знайдена: {args.mask}")
            return False
        
        if not args.prompt:
            self.print_status("❌ Помилка: Потрібен --prompt")
            return False
        
        self.print_status(f"Зображення: {args.image}")
        self.print_status(f"Маска: {args.mask}")
        self.print_status(f"Промпт: {args.prompt}")
        
        image = Image.open(args.image).convert("RGB")
        mask = Image.open(args.mask).convert("L")
        
        image_base64 = self.image_to_base64(image)
        mask_base64 = self.image_to_base64(mask)
        
        params = {
            "prompt": args.prompt,
            "negative_prompt": args.negative_prompt or "",
            "image": image_base64,
            "mask": mask_base64,
            "checkpoint": args.checkpoint,
        }
        
        self.print_status("🔄 Генерування...")
        
        try:
            response = self.session.post(
                f"{self.server_url}/inpaint",
                json=params,
                timeout=self.config.get("timeout", 600)
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.save_result(data.get('image', ''), args.output)
                    return True
                else:
                    self.print_status(f"❌ Помилка: {data.get('error', 'Unknown')}")
                    return False
            else:
                self.print_status(f"❌ HTTP Error: {response.status_code}")
                return False
        
        except requests.Timeout:
            self.print_status("❌ Помилка: Сервер не відповідає (timeout)")
            return False
        except Exception as e:
            self.print_status(f"❌ Помилка: {e}")
            return False
    
    def status(self, args):
        """Отримати статус сервера"""
        self.print_status(f"🔍 Перевірка сервера: {self.server_url}")
        
        try:
            response = self.session.get(f"{self.server_url}/status", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Сервер доступний!")
                for key, value in data.items():
                    print(f"   {key}: {value}")
                return True
            else:
                self.print_status(f"❌ HTTP Error: {response.status_code}")
                return False
        
        except Exception as e:
            self.print_status(f"❌ Помилка: {e}")
            return False
    
    def save_result(self, image_base64, output_path):
        """Зберегти результат"""
        if not image_base64:
            self.print_status("❌ Помилка: Пусто зображення")
            return
        
        try:
            image_data = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_data))
            
            # Генерувати шлях якщо не вказано
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output_{timestamp}.png"
            
            image.save(output_path)
            self.print_status(f"✅ Збережено: {output_path}")
        
        except Exception as e:
            self.print_status(f"❌ Помилка при збереженні: {e}")
    
    @staticmethod
    def image_to_base64(image):
        """Конвертувати PIL Image в base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()


def main():
    """Головна функція"""
    parser = argparse.ArgumentParser(
        description="🎨 TEST_EASY CLI Client - Simple Stable Diffusion Generation"
    )
    
    parser.add_argument(
        "--server",
        help="Server URL (default: http://localhost:5000)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # txt2img субкоманда
    txt2img_parser = subparsers.add_parser("txt2img", help="Generate from text")
    txt2img_parser.add_argument("--prompt", required=True, help="Text prompt")
    txt2img_parser.add_argument("--negative-prompt", help="Negative prompt")
    txt2img_parser.add_argument("--checkpoint", default="sd15", 
                               help="Model checkpoint (sd15, sd21, sdxl)")
    txt2img_parser.add_argument("--width", type=int, default=512, help="Image width")
    txt2img_parser.add_argument("--height", type=int, default=512, help="Image height")
    txt2img_parser.add_argument("--steps", type=int, default=20, help="Inference steps")
    txt2img_parser.add_argument("--scale", type=float, default=7.5, 
                               help="Guidance scale")
    txt2img_parser.add_argument("--output", help="Output file path")
    
    # img2img субкоманда
    img2img_parser = subparsers.add_parser("img2img", help="Modify image")
    img2img_parser.add_argument("--image", required=True, help="Input image path")
    img2img_parser.add_argument("--prompt", required=True, help="Text prompt")
    img2img_parser.add_argument("--negative-prompt", help="Negative prompt")
    img2img_parser.add_argument("--strength", type=float, default=0.75,
                               help="Denoising strength (0.0-1.0)")
    img2img_parser.add_argument("--checkpoint", default="sd15",
                               help="Model checkpoint")
    img2img_parser.add_argument("--output", help="Output file path")
    
    # inpaint субкоманда
    inpaint_parser = subparsers.add_parser("inpaint", help="Edit image with mask")
    inpaint_parser.add_argument("--image", required=True, help="Input image path")
    inpaint_parser.add_argument("--mask", required=True, help="Mask image path")
    inpaint_parser.add_argument("--prompt", required=True, help="Text prompt")
    inpaint_parser.add_argument("--negative-prompt", help="Negative prompt")
    inpaint_parser.add_argument("--checkpoint", default="sd15",
                               help="Model checkpoint")
    inpaint_parser.add_argument("--output", help="Output file path")
    
    # status субкоманда
    status_parser = subparsers.add_parser("status", help="Check server status")
    
    args = parser.parse_args()
    
    client = EasyClientCLI(server_url=args.server)
    client.print_banner()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Виконати команду
    success = False
    
    if args.command == "txt2img":
        success = client.txt2img(args)
    elif args.command == "img2img":
        success = client.img2img(args)
    elif args.command == "inpaint":
        success = client.inpaint(args)
    elif args.command == "status":
        success = client.status(args)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
