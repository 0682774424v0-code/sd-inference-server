# 📚 TEST_EASY - Документація використання

## Швидкий старт

### 1. Запуск Colab сервера

```python
# Скопіюйте код з colab_server.py в новий Colab notebook
# або завантажте файл remote_colab.ipynb

# В Colab виконайте ячейки:
1. Встановлення залежностей (!pip install ...)
2. Кореневий код простого сервера
3. Запуск Flask сервера з ngrok

# Видите публічну URL:
# Running on https://abcd-1234.ngrok.io
```

### 2. Оновіть config.json на своєму комп'ютері

```json
{
  "server_url": "https://YOUR_NGROK_URL.ngrok.io",
  "default_checkpoint": "sd15",
  "default_width": 512,
  "default_height": 512,
  "default_steps": 20,
  "default_scale": 7.5
}
```

## GUI Клієнт

### Встановлення

```bash
pip install PyQt5 requests pillow
python client_gui.py
```

### Інтерфейс

#### 🎨 txt2img (Текст → Зображення)

1. Введіть промпт
   - Напр.: "cute fluffy cat, professional photo, 4k, detailed"

2. Вибиріть параметри:
   - **Checkpoint**: sd15 (швидкий), sd21 (якісніший), sdxl (найякісніший)
   - **Width/Height**: 512 (стандарт), 768, 1024
   - **Steps**: 20-50 (більше = краще, але повільніше)
   - **Scale**: 7.5 (рекомендовано), 5-15 (більше = слідувати промпту)

3. Натисніть "🎨 Генерувати"

4. Результат збереживається в `last_result.png`

#### 🖼️ img2img (Модифікація зображення)

1. Вибиріть вхідне зображення
   - Натисніть "📂 Вибрати"

2. Введіть промпт для змін
   - Напр.: "oil painting style"

3. Встановіть Strength
   - **0.0** = не змінювати (повність оригіналу)
   - **0.5** = помірна змінення
   - **1.0** = близько до txt2img (сильна зміна)
   - Рекомендовано: **0.7**

4. Натисніть "🖼️ Генерувати"

#### 🎭 inpaint (Редагування з маскою)

1. Вибиріть зображення
   - Натисніть "📂 Вибрати"

2. **Малюйте маску у редакторі:**
   - Білі области = редагуватимуться
   - Чорні области = залишиться незмінено
   - Розмір пензля: регулятор у контролях
   - "🗑️ Очистити маску" = почати заново

3. Введіть промпт для редагування
   - Напр.: "blue eyes, smiling"

4. Натисніть "🎭 Генерувати"

### Приклади промптів

#### Хороші промпти (специфічні):
```
- "beautiful woman, elegant dress, intricate details, professional lighting, portrait"
- "steampunk airship, detailed mechanical gears, sunset sky, digital art"
- "japanese garden, stone lantern, maple trees, serene"
```

#### Погані промпти (занадто загальні):
```
- "cat" (замало деталей)
- "beautiful" (неконкретно)
- "random things" (не чіткий образ)
```

#### Negative промпти (що уникати):
```
- "blurry, low quality, distorted, ugly, bad anatomy"
- "watermark, text, logo"
```

## CLI Клієнт

### Встановлення

```bash
pip install requests pillow
python client_cli.py --help
```

### Команди

#### txt2img

```bash
# Простий приклад
python client_cli.py txt2img --prompt "cute cat"

# З параметрами
python client_cli.py txt2img \
  --prompt "cyberpunk city, neon lights" \
  --checkpoint sdxl \
  --width 768 \
  --height 512 \
  --steps 30 \
  --scale 7.5 \
  --output my_image.png

# З negative промптом
python client_cli.py txt2img \
  --prompt "beautiful sunset" \
  --negative-prompt "blurry, low quality" \
  --output sunset.png
```

#### img2img

```bash
# Модифікувати зображення
python client_cli.py img2img \
  --image input.png \
  --prompt "oil painting style" \
  --strength 0.75 \
  --output output.png

# З negative промптом
python client_cli.py img2img \
  --image photo.jpg \
  --prompt "anime style" \
  --negative-prompt "realistic" \
  --strength 0.6 \
  --output anime_version.png
```

#### inpaint

```bash
# Редагувати зображення з маскою
python client_cli.py inpaint \
  --image original.png \
  --mask mask.png \
  --prompt "blue eyes" \
  --output edited.png

# З додатковими параметрами
python client_cli.py inpaint \
  --image photo.jpg \
  --mask mask.jpg \
  --prompt "beautiful sunset background" \
  --checkpoint sdxl \
  --output background_changed.png
```

#### status

```bash
# Перевірити доступність сервера
python client_cli.py status

# Вивід:
# ✅ Сервер доступний!
#    gpu_available: true
#    model_loaded: sd15
#    memory_available: 2048
```

### Налаштування серверу

```bash
# Використовувати власний сервер
python client_cli.py --server http://192.168.1.100:5000 txt2img --prompt "cat"

# Або встановити в config.json:
# {
#   "server_url": "http://my-server:5000"
# }
```

## Batch-обробка

### Скрипт для обробки багатьох зображень

Створіть `batch_processing.py`:

```python
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Список промптів
prompts = [
    "beautiful landscape, mountains, sunrise",
    "cyberpunk city, neon lights",
    "fantasy castle, magical atmosphere",
    "underwater world, coral reef",
]

# Генерувати для кожного промпту
for i, prompt in enumerate(prompts):
    print(f"\n[{i+1}/{len(prompts)}] Генерування: {prompt}")
    
    cmd = [
        "python", "client_cli.py", "txt2img",
        "--prompt", prompt,
        "--checkpoint", "sd15",
        "--steps", "30",
        "--output", f"output_{i:02d}.png"
    ]
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ Помилка при генеруванні {i}")

print("\n✅ Готово!")
```

Запуск:
```bash
python batch_processing.py
```

### Скрипт для img2img з папкою

```python
#!/usr/bin/env python3
import subprocess
from pathlib import Path

input_dir = Path("input_images")
output_dir = Path("output_images")
output_dir.mkdir(exist_ok=True)

prompt = "oil painting style, masterpiece"

for image_path in input_dir.glob("*.png"):
    output_path = output_dir / f"painted_{image_path.name}"
    
    print(f"Обробка: {image_path}")
    
    cmd = [
        "python", "client_cli.py", "img2img",
        "--image", str(image_path),
        "--prompt", prompt,
        "--strength", "0.7",
        "--output", str(output_path)
    ]
    
    subprocess.run(cmd)

print("✅ Готово!")
```

## Розширене використання

### Створення маски програмно

```python
from PIL import Image, ImageDraw

# Завантажити зображення
img = Image.open("photo.jpg").convert("RGB")

# Створити маску
mask = Image.new("L", img.size, 0)  # Чорна маска
draw = ImageDraw.Draw(mask)

# Нарисувати білу область для редагування
draw.rectangle([100, 100, 300, 300], fill=255)

# Зберегти
mask.save("mask.png")
```

### Використання LoRA

Якщо LoRA підтримуються на сервері:

```bash
python client_cli.py txt2img \
  --prompt "cute anime girl, lora:anime_style:1.0" \
  --checkpoint sd15 \
  --output anime.png
```

### Запуск локального сервера

Якщо у вас є GPU:

```bash
# У папці TEST_EASY/server
python -c "from easy_wrapper import EasyGenerator; gen = EasyGenerator(); print('✅ Готово до генерування')"

# Або запустіть свій локальний Flask сервер
python -m flask run --host 0.0.0.0 --port 5000
```

## Розв'язання проблем

### Помилка: "Не можна підключитися до сервера"

1. Перевірити URL у config.json
2. Перевірити чи Colab notebook запущено
3. Перевірити ngrok tunnel активна
4. Перезапустити Colab сервер

### Помилка: "Out of Memory"

- Зменшіть ширину/висоту
- Зменшіть кількість steps
- Використовуйте sd15 замість sdxl
- На Colab перезапустіть kernel

### Генерування дуже повільне

- Використовуйте менші розміри (512x512)
- Зменшіть steps (20 замість 50)
- На GPU-менш потужному користайтеся sd15

### Результати низької якості

- Підвищіть steps (30-50)
- Уточніть промпт (більше деталей)
- Використовуйте sdxl checkpoint
- Звалюйте negative prompt

### Маска не працює у inpaint

- Переконайтеся, що маска чорна/біла
- Маска має той самий розмір що оригінальне зображення
- Білі області буде змінено, чорні залишаться

## Клавіші у GUI

| Клавіша | Дія |
|---------|-----|
| Ctrl+O | Вибрати файл |
| Ctrl+Q | Закрити |
| Enter | Генерувати (у деяких полях) |
| Tab | Перейти до наступного поля |

## Конфіг параметри

### config.json

```json
{
  "server_url": "http://localhost:5000",              // Адреса сервера
  "default_checkpoint": "sd15",                       // Модель за замовчанням
  "default_width": 512,                               // Ширина за замовчанням
  "default_height": 512,                              // Висота за замовчанням
  "default_steps": 20,                                // Кроки за замовчанням
  "default_scale": 7.5,                               // Масштаб за замовчанням
  "timeout": 600,                                     // Timeout в секундах
  "colab_server_url": "https://YOUR_NGROK_URL.ngrok.io"  // Для Colab
}
```

## Получення допомоги

```bash
python client_cli.py --help
python client_cli.py txt2img --help
python client_cli.py img2img --help
python client_cli.py inpaint --help
python client_gui.py --help
```

---

**Автор**: TEST_EASY Project  
**Ліцензія**: MIT  
**Останнє оновлення**: 2024
