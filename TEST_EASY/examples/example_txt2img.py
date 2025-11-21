#!/usr/bin/env python3
"""
example_txt2img.py - Приклади txt2img генерування

Показує різні використання text-to-image генерування
"""

import requests
import json
from pathlib import Path
from PIL import Image
import io
import base64
import time


class EasyExamples:
    """Колекція прикладів використання"""
    
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.session = requests.Session()
    
    def base64_to_image(self, img_base64):
        """Конвертувати base64 в PIL Image"""
        img_data = base64.b64decode(img_base64)
        return Image.open(io.BytesIO(img_data))
    
    def print_section(self, title):
        """Показати заголовок"""
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}\n")
    
    # ===== Приклади txt2img =====
    
    def example_simple(self):
        """Простий приклад: кіт"""
        self.print_section("Приклад 1: Простий кіт")
        
        print("Генеруємо: 'cute fluffy cat'")
        print("Параметри: стандартні\n")
        
        params = {
            "prompt": "cute fluffy cat, sitting, professional photo, 4k, detailed fur",
            "checkpoint": "sd15",
            "width": 512,
            "height": 512,
            "steps": 20,
            "scale": 7.5,
        }
        
        try:
            response = self.session.post(f"{self.server_url}/txt2img", json=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image = self.base64_to_image(data['image'])
                    image.save("example_01_cute_cat.png")
                    print("✅ Збережено: example_01_cute_cat.png")
                else:
                    print(f"❌ Помилка: {data.get('error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    def example_landscape(self):
        """Приклад 2: Пейзаж"""
        self.print_section("Приклад 2: Красивий пейзаж")
        
        print("Генеруємо: гірський пейзаж на заході сонця")
        print("Параметри: більше кроків для якості\n")
        
        params = {
            "prompt": "majestic mountain landscape, sunset, golden hour light, "
                     "reflection in lake, snow peaks, professional photography, 4k, cinematic",
            "negative_prompt": "blurry, low quality, distorted",
            "checkpoint": "sd21",  # Вища якість
            "width": 768,
            "height": 512,
            "steps": 30,  # Більше кроків
            "scale": 8.0,
        }
        
        print(f"Промпт: {params['prompt'][:60]}...")
        print(f"Negative: {params['negative_prompt']}")
        print(f"Параметри: {params['width']}x{params['height']}, {params['steps']} steps\n")
        
        try:
            response = self.session.post(f"{self.server_url}/txt2img", json=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image = self.base64_to_image(data['image'])
                    image.save("example_02_landscape.png")
                    print("✅ Збережено: example_02_landscape.png")
                else:
                    print(f"❌ Помилка: {data.get('error')}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    def example_portrait(self):
        """Приклад 3: Портрет"""
        self.print_section("Приклад 3: Портрет")
        
        print("Генеруємо: портрет красивої дівчини")
        print("Параметри: студійне освітлення\n")
        
        params = {
            "prompt": "portrait of beautiful woman, elegant, soft lighting, studio photography, "
                     "detailed face, professional makeup, warm color grading, 8k quality",
            "negative_prompt": "ugly, deformed, blurry, bad proportions, extra limbs",
            "checkpoint": "sdxl",  # Найкраща якість
            "width": 512,
            "height": 768,
            "steps": 40,
            "scale": 7.5,
        }
        
        print(f"Промпт: {params['prompt'][:60]}...")
        print(f"Checkpoint: {params['checkpoint']} (найкраща якість)\n")
        
        try:
            response = self.session.post(f"{self.server_url}/txt2img", json=params)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image = self.base64_to_image(data['image'])
                    image.save("example_03_portrait.png")
                    print("✅ Збережено: example_03_portrait.png")
                else:
                    print(f"❌ Помилка: {data.get('error')}")
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    def example_style_variations(self):
        """Приклад 4: Варіації стилю"""
        self.print_section("Приклад 4: Один предмет в різних стилях")
        
        styles = [
            ("watercolor painting style", "example_04a_watercolor.png"),
            ("oil painting, renaissance, detailed", "example_04b_renaissance.png"),
            ("anime, manga, colorful", "example_04c_anime.png"),
            ("3d render, octane render, detailed", "example_04d_3d.png"),
        ]
        
        base_prompt = "cute castle on a hill"
        
        for i, (style, filename) in enumerate(styles, 1):
            print(f"\n[{i}/{len(styles)}] {style}")
            
            params = {
                "prompt": f"{base_prompt}, {style}",
                "checkpoint": "sd15",
                "width": 512,
                "height": 512,
                "steps": 25,
                "scale": 7.5,
            }
            
            try:
                response = self.session.post(f"{self.server_url}/txt2img", json=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        image = self.base64_to_image(data['image'])
                        image.save(filename)
                        print(f"   ✅ {filename}")
                    else:
                        print(f"   ❌ Помилка: {data.get('error')}")
                time.sleep(1)  # Пауза між запитами
            except Exception as e:
                print(f"   ❌ Помилка: {e}")
    
    def example_negative_prompt(self):
        """Приклад 5: Вплив negative prompt"""
        self.print_section("Приклад 5: Negative Prompt")
        
        # Без negative prompt
        print("Генеруємо БЕЗ negative prompt...")
        params1 = {
            "prompt": "dog, portrait, detailed",
            "checkpoint": "sd15",
            "width": 512,
            "height": 512,
            "steps": 20,
            "scale": 7.5,
        }
        
        try:
            response = self.session.post(f"{self.server_url}/txt2img", json=params1)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image = self.base64_to_image(data['image'])
                    image.save("example_05a_without_negative.png")
                    print("✅ example_05a_without_negative.png")
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        time.sleep(1)
        
        # З negative prompt
        print("\nГенеруємо З negative prompt...")
        params2 = {
            "prompt": "dog, portrait, detailed",
            "negative_prompt": "blurry, low quality, distorted, extra ears, extra eyes",
            "checkpoint": "sd15",
            "width": 512,
            "height": 512,
            "steps": 20,
            "scale": 7.5,
        }
        
        try:
            response = self.session.post(f"{self.server_url}/txt2img", json=params2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image = self.base64_to_image(data['image'])
                    image.save("example_05b_with_negative.png")
                    print("✅ example_05b_with_negative.png")
                    print("\n💡 Порівняйте обидва результати!")
        except Exception as e:
            print(f"❌ Помилка: {e}")
    
    def example_scale_variations(self):
        """Приклад 6: Вплив guidance scale"""
        self.print_section("Приклад 6: Guidance Scale варіації")
        
        scales = [3.0, 7.5, 15.0]
        
        for scale in scales:
            print(f"\nГенеруємо з scale={scale}...")
            
            params = {
                "prompt": "a wizard casting spell, magical effects, detailed",
                "checkpoint": "sd15",
                "width": 512,
                "height": 512,
                "steps": 25,
                "scale": scale,
            }
            
            try:
                response = self.session.post(f"{self.server_url}/txt2img", json=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        image = self.base64_to_image(data['image'])
                        filename = f"example_06_scale_{scale}.png"
                        image.save(filename)
                        print(f"✅ {filename}")
                time.sleep(1)
            except Exception as e:
                print(f"❌ Помилка: {e}")
    
    def run_all(self):
        """Запустити всі приклади"""
        print("""
╔════════════════════════════════════════════╗
║  🎨 TEST_EASY - Приклади txt2img            ║
╚════════════════════════════════════════════╝
        """)
        
        try:
            # Перевірити сервер
            print("🔍 Перевірка сервера...")
            response = self.session.get(f"{self.server_url}/status", timeout=5)
            if response.status_code != 200:
                print("❌ Сервер недоступний!")
                return
            print("✅ Сервер доступний\n")
        except Exception as e:
            print(f"❌ Помилка підключення: {e}")
            return
        
        # Запустити приклади
        print("Запуск прикладів... (може зайняти кілька хвилин)")
        
        self.example_simple()
        time.sleep(2)
        
        self.example_landscape()
        time.sleep(2)
        
        self.example_portrait()
        time.sleep(2)
        
        self.example_style_variations()
        time.sleep(2)
        
        self.example_negative_prompt()
        time.sleep(2)
        
        self.example_scale_variations()
        
        print("\n" + "="*50)
        print("✅ Всі приклади завершені!")
        print("="*50)
        print("\n📁 Генеровані файли:")
        for f in sorted(Path(".").glob("example_*.png")):
            print(f"   - {f.name}")


def main():
    """Головна функція"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Приклади txt2img генерування")
    parser.add_argument("--server", default="http://localhost:5000", help="Server URL")
    parser.add_argument("--example", type=int, help="Запустити конкретний приклад (1-6)")
    
    args = parser.parse_args()
    
    examples = EasyExamples(server_url=args.server)
    
    if args.example:
        if args.example == 1:
            examples.example_simple()
        elif args.example == 2:
            examples.example_landscape()
        elif args.example == 3:
            examples.example_portrait()
        elif args.example == 4:
            examples.example_style_variations()
        elif args.example == 5:
            examples.example_negative_prompt()
        elif args.example == 6:
            examples.example_scale_variations()
        else:
            print(f"❌ Невідомий приклад: {args.example}")
    else:
        examples.run_all()


if __name__ == "__main__":
    main()
