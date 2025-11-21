#!/usr/bin/env python3
"""
batch_txt2img.py - Batch обробка для txt2img

Генерує множину зображень з різними промптами
"""

import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime
import time


class BatchProcessor:
    """Batch обробка txt2img"""
    
    def __init__(self, server_url="http://localhost:5000", output_dir="batch_output"):
        self.server_url = server_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def print_header(self, text):
        """Показати заголовок"""
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}\n")
    
    def print_status(self, message, level="info"):
        """Показати статус"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"info": "ℹ️", "success": "✅", "error": "❌", "progress": "🔄"}
        icon = icons.get(level, "ℹ️")
        print(f"[{timestamp}] {icon} {message}")
    
    def generate_image(self, prompt, negative_prompt="", checkpoint="sd15", 
                      width=512, height=512, steps=20, filename=None):
        """Генерувати одне зображення"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:16]
            filename = f"batch_{timestamp}.png"
        
        output_path = self.output_dir / filename
        
        cmd = [
            "python", "client_cli.py",
            "--server", self.server_url,
            "txt2img",
            "--prompt", prompt,
            "--checkpoint", checkpoint,
            "--width", str(width),
            "--height", str(height),
            "--steps", str(steps),
            "--output", str(output_path)
        ]
        
        if negative_prompt:
            cmd.extend(["--negative-prompt", negative_prompt])
        
        self.print_status(f"Генеруємо: {prompt[:50]}...")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.print_status(f"✅ {output_path.name}", "success")
                return str(output_path)
            else:
                self.print_status(f"❌ Помилка: {result.stderr}", "error")
                return None
        except subprocess.TimeoutExpired:
            self.print_status("❌ Timeout (генерування зайняло занадто довго)", "error")
            return None
        except Exception as e:
            self.print_status(f"❌ Помилка: {e}", "error")
            return None
    
    def batch_prompts(self, prompts_list, negative_prompt="", checkpoint="sd15",
                     width=512, height=512, steps=20, delay=1):
        """Обробити список промптів"""
        self.print_header(f"Batch обробка ({len(prompts_list)} промптів)")
        self.print_status(f"Сервер: {self.server_url}")
        self.print_status(f"Вихідна папка: {self.output_dir}")
        self.print_status(f"Параметри: {width}x{height}, {steps} steps, {checkpoint}\n")
        
        results = []
        successful = 0
        failed = 0
        
        for i, prompt in enumerate(prompts_list, 1):
            self.print_status(f"[{i}/{len(prompts_list)}] Обробка...")
            
            result = self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                checkpoint=checkpoint,
                width=width,
                height=height,
                steps=steps,
                filename=f"batch_{i:03d}.png"
            )
            
            if result:
                results.append(result)
                successful += 1
            else:
                failed += 1
            
            if i < len(prompts_list):
                time.sleep(delay)
        
        # Результати
        self.print_header("Результати")
        self.print_status(f"Успішно: {successful}")
        self.print_status(f"Помилок: {failed}")
        self.print_status(f"Всього: {len(prompts_list)}")
        
        return results
    
    def batch_styles(self, base_prompt, styles_list, checkpoint="sd15",
                    width=512, height=512, steps=25, delay=1):
        """Генерувати один промпт в різних стилях"""
        self.print_header(f"Стильові варіації ({len(styles_list)} стилів)")
        self.print_status(f"Базовий промпт: {base_prompt}")
        self.print_status(f"Вихідна папка: {self.output_dir}\n")
        
        results = []
        
        for i, style in enumerate(styles_list, 1):
            prompt = f"{base_prompt}, {style}"
            
            self.print_status(f"[{i}/{len(styles_list)}] Стиль: {style}")
            
            result = self.generate_image(
                prompt=prompt,
                checkpoint=checkpoint,
                width=width,
                height=height,
                steps=steps,
                filename=f"style_{i:02d}_{style.replace(' ', '_')[:20]}.png"
            )
            
            if result:
                results.append(result)
            
            if i < len(styles_list):
                time.sleep(delay)
        
        self.print_header("Готово!")
        self.print_status(f"Генеровано {len(results)} варіацій")
        
        return results
    
    def batch_parameters(self, prompt, params_variants, delay=1):
        """Генерувати один промпт з різними параметрами"""
        self.print_header(f"Варіації параметрів ({len(params_variants)} варіантів)")
        self.print_status(f"Промпт: {prompt}")
        self.print_status(f"Вихідна папка: {self.output_dir}\n")
        
        results = []
        
        for i, params in enumerate(params_variants, 1):
            desc = f"{params['width']}x{params['height']}, {params['steps']} steps, scale={params.get('scale', 7.5)}"
            
            self.print_status(f"[{i}/{len(params_variants)}] {desc}")
            
            result = self.generate_image(
                prompt=prompt,
                checkpoint=params.get('checkpoint', 'sd15'),
                width=params.get('width', 512),
                height=params.get('height', 512),
                steps=params.get('steps', 20),
                filename=f"params_{i:02d}_{desc.replace(' ', '_')[:20]}.png"
            )
            
            if result:
                results.append(result)
            
            if i < len(params_variants):
                time.sleep(delay)
        
        self.print_header("Готово!")
        self.print_status(f"Генеровано {len(results)} варіацій")
        
        return results


# ===== Приготовлені наборні =====

EXAMPLE_PROMPTS = [
    "cute fluffy cat, professional photo, 4k",
    "beautiful mountain landscape, sunset, detailed",
    "steampunk robot, industrial, detailed",
    "fantasy castle, magical atmosphere, cinematic",
    "underwater world, coral reef, colorful fish",
]

EXAMPLE_STYLES = [
    "watercolor painting",
    "oil painting, renaissance",
    "anime, manga",
    "3d render, cinematic",
    "pencil sketch, detailed",
]

EXAMPLE_PARAMS = [
    {"width": 512, "height": 512, "steps": 20, "checkpoint": "sd15"},
    {"width": 768, "height": 512, "steps": 30, "checkpoint": "sd21"},
    {"width": 512, "height": 768, "steps": 40, "checkpoint": "sdxl"},
]


def main():
    """Головна функція"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch txt2img генерування")
    parser.add_argument("--server", default="http://localhost:5000", help="Server URL")
    parser.add_argument("--mode", choices=["prompts", "styles", "params"], 
                       default="prompts", help="Режим batch обробки")
    parser.add_argument("--output", default="batch_output", help="Вихідна папка")
    parser.add_argument("--delay", type=float, default=1, help="Затримка між генеруваннями (сек)")
    
    args = parser.parse_args()
    
    processor = BatchProcessor(server_url=args.server, output_dir=args.output)
    
    if args.mode == "prompts":
        print("\n🎨 BATCH MODE: Множинні промпти")
        processor.batch_prompts(
            EXAMPLE_PROMPTS,
            checkpoint="sd15",
            steps=20,
            delay=args.delay
        )
    
    elif args.mode == "styles":
        print("\n🎨 BATCH MODE: Стильові варіації")
        processor.batch_styles(
            base_prompt="cute castle on a hill",
            styles_list=EXAMPLE_STYLES,
            steps=25,
            delay=args.delay
        )
    
    elif args.mode == "params":
        print("\n🎨 BATCH MODE: Варіації параметрів")
        processor.batch_parameters(
            prompt="beautiful woman, portrait, elegant",
            params_variants=EXAMPLE_PARAMS,
            delay=args.delay
        )
    
    print("\n✅ Batch обробка завершена!")
    print(f"📁 Результати в папці: {args.output}")


if __name__ == "__main__":
    main()
