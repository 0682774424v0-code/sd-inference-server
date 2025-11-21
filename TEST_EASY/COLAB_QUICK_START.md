# 🚀 TEST_EASY на Google Colab - Швидкий Гайд

> Запуск сервера TEST_EASY на безплатній NVIDIA GPU

## Передумови

- Google Account
- Браузер (Chrome, Firefox, Safari)
- Клієнт на вашому комп'ютері

## Крок 1: Відкрити Google Colab

1. Перейдіть на https://colab.research.google.com
2. Натисніть **"New notebook"** або **"File → New notebook"**
3. Назвіть notebook (напр. "TEST_EASY Server")

## Крок 2: Встановити залежності

Скопіюйте в першу ячейку Colab:

```python
# Встановити PyTorch (GPU CUDA 11.8)
!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q

# Встановити Stable Diffusion залежності
!pip install diffusers transformers safetensors accelerate -q

# Встановити Flask та ngrok
!pip install flask flask-cors pyngrok pillow requests -q

print("✅ Залежності встановлені!")
```

**Натисніть Play (▶️)** або **Ctrl+Enter**

Чекайте 1-2 хвилини на встановлення.

## Крок 3: Налаштувати ngrok (ОДИН РАЗ)

```python
import os
from pyngrok import ngrok

# Зареєструйтеся на https://ngrok.com
# Скопіюйте AuthToken з https://dashboard.ngrok.com/auth/your-authtoken

# Встановіть токен
os.environ['NGROK_AUTHTOKEN'] = 'YOUR_AUTHTOKEN_HERE'  # ← ЗАМІНІТЬ НА ВАШИЙ!

print("✅ ngrok налаштовано!")
```

## Крок 4: Завантажити код сервера

Скопіюйте **ВСЮ** папку `server/colab_server.py` в ячейку:

```python
# Основна функція сервера
import base64
import io
import torch
from diffusers import AutoPipelineForText2Image, AutoPipelineForImage2Image
from diffusers import StableDiffusionInpaintPipeline
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyngrok import ngrok
import os

app = Flask(__name__)
CORS(app)

# ===== SimpleGenerator =====

class SimpleGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.current_model = None
        self.txt2img_pipe = None
        self.img2img_pipe = None
        self.inpaint_pipe = None
    
    def load_txt2img(self, checkpoint="sd15"):
        if self.current_model == checkpoint and self.txt2img_pipe is not None:
            return
        
        print(f"Loading {checkpoint} for txt2img...")
        model_id = {
            "sd15": "runwayml/stable-diffusion-v1-5",
            "sd21": "stabilityai/stable-diffusion-2-1",
            "sdxl": "stabilityai/stable-diffusion-xl-base-1.0"
        }.get(checkpoint, checkpoint)
        
        self.txt2img_pipe = AutoPipelineForText2Image.from_pretrained(
            model_id, torch_dtype=self.dtype
        ).to(self.device)
        
        self.current_model = checkpoint
    
    def load_img2img(self, checkpoint="sd15"):
        if self.current_model == checkpoint and self.img2img_pipe is not None:
            return
        
        print(f"Loading {checkpoint} for img2img...")
        model_id = {
            "sd15": "runwayml/stable-diffusion-v1-5",
            "sd21": "stabilityai/stable-diffusion-2-1",
            "sdxl": "stabilityai/stable-diffusion-xl-img2img-1.0"
        }.get(checkpoint, checkpoint)
        
        self.img2img_pipe = AutoPipelineForImage2Image.from_pretrained(
            model_id, torch_dtype=self.dtype
        ).to(self.device)
        
        self.current_model = checkpoint
    
    def load_inpaint(self, checkpoint="sd15"):
        if self.current_model == checkpoint and self.inpaint_pipe is not None:
            return
        
        print(f"Loading {checkpoint} for inpaint...")
        model_id = {
            "sd15": "runwayml/stable-diffusion-v1-5",
            "sd21": "stabilityai/stable-diffusion-2-1",
        }.get(checkpoint, "runwayml/stable-diffusion-v1-5")
        
        self.inpaint_pipe = StableDiffusionInpaintPipeline.from_pretrained(
            model_id, torch_dtype=self.dtype
        ).to(self.device)
        
        self.current_model = checkpoint
    
    def txt2img(self, prompt, checkpoint="sd15", width=512, height=512, steps=20, scale=7.5, **kwargs):
        self.load_txt2img(checkpoint)
        
        image = self.txt2img_pipe(
            prompt=prompt,
            height=height,
            width=width,
            num_inference_steps=steps,
            guidance_scale=scale
        ).images[0]
        
        return image
    
    def img2img(self, prompt, image, checkpoint="sd15", strength=0.75, steps=20, **kwargs):
        self.load_img2img(checkpoint)
        
        result = self.img2img_pipe(
            prompt=prompt,
            image=image,
            strength=strength,
            num_inference_steps=int(steps * strength)
        ).images[0]
        
        return result
    
    def inpaint(self, prompt, image, mask, checkpoint="sd15", steps=20, **kwargs):
        self.load_inpaint(checkpoint)
        
        result = self.inpaint_pipe(
            prompt=prompt,
            image=image,
            mask_image=mask,
            num_inference_steps=steps
        ).images[0]
        
        return result


generator = SimpleGenerator()

# ===== Helper Functions =====

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def base64_to_image(img_base64):
    img_data = base64.b64decode(img_base64)
    return Image.open(io.BytesIO(img_data))

# ===== Routes =====

@app.route('/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'ok',
        'gpu': torch.cuda.is_available(),
        'device': 'cuda' if torch.cuda.is_available() else 'cpu',
        'current_model': generator.current_model
    })

@app.route('/txt2img', methods=['POST'])
def txt2img_endpoint():
    try:
        data = request.json
        image = generator.txt2img(**data)
        return jsonify({'success': True, 'image': image_to_base64(image)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/img2img', methods=['POST'])
def img2img_endpoint():
    try:
        data = request.json
        image_base64 = data.pop('image')
        image = base64_to_image(image_base64)
        result = generator.img2img(image=image, **data)
        return jsonify({'success': True, 'image': image_to_base64(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/inpaint', methods=['POST'])
def inpaint_endpoint():
    try:
        data = request.json
        image_base64 = data.pop('image')
        mask_base64 = data.pop('mask')
        image = base64_to_image(image_base64)
        mask = base64_to_image(mask_base64)
        result = generator.inpaint(image=image, mask=mask, **data)
        return jsonify({'success': True, 'image': image_to_base64(result)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== Launch =====

if __name__ == '__main__':
    from PIL import Image
    
    print("Starting Flask server...")
    
    # Запустити ngrok
    public_url = ngrok.connect(5000, "http")
    print(f"\n{'='*50}")
    print(f"✅ PUBLIC URL: {public_url}")
    print(f"{'='*50}\n")
    print("⚠️  СКОПІЮЙТЕ ЦЬОМУ URL В client/config.json\n")
    
    # Запустити Flask
    app.run(port=5000)
```

**Натисніть Play (▶️)**

Чекайте, поки сервер не запуститься.

## Крок 5: Скопіювати URL

Коли побачите:
```
✅ PUBLIC URL: https://abcd-1234.ngrok.io
```

**Скопіюйте цю URL** (крім https://)

## Крок 6: Налаштувати Клієнт

На своєму комп'ютері:

1. Відкрийте `TEST_EASY/client/config.json`
2. Замініть `server_url`:

```json
{
  "server_url": "https://YOUR_URL.ngrok.io",  // ← Вставте URL звідси
  "default_checkpoint": "sd15",
  ...
}
```

3. Збережіть файл

## Крок 7: Запустити Клієнт

На своєму комп'ютері:

```bash
cd TEST_EASY/client
python client_gui.py
```

Або CLI:
```bash
python client_cli.py status
```

## Крок 8: Генерувати!

В GUI введіть промпт та натисніть "Генерувати"!

```bash
# Або CLI:
python client_cli.py txt2img --prompt "cute cat"
```

## 🔄 Повторне Запускання

### Другого дня:

1. Відкрийте Colab notebook
2. Запустіть ячейку з кодом сервера знову
3. **Видите НОВУ URL** (стара не працює!)
4. Оновіть `config.json` новою URL

## ⚙️ Параметри Colab

### Якщо повільно:

1. **Включити Premium GPU:**
   - Натисніть ⚙️ → "Runtime type" → "T4 GPU"
   - Або спробуйте "A100 GPU" (якщо доступна)

2. **Включити кешування:**
   ```python
   import os
   os.environ['TRANSFORMERS_CACHE'] = '/tmp/huggingface'
   os.environ['HF_HOME'] = '/tmp/huggingface'
   ```

3. **Експрес-версія:**
   ```python
   # Використовувати float16 (швидше, менше памяті)
   torch.dtype = torch.float16
   ```

## 🆘 Проблеми

### "Import Error: No module named..."
- Перезапустіть Runtime: Runtime → "Restart runtime"
- Переустановіть залежності

### "Timeout після 10 хвилин"
- Colab вимикає неактивні ячейки
- Натисніть Play кожні 10 хвилин
- Або продовжите підписку на Colab Pro

### "Out of Memory"
- Зменшіть розмір: 256x256 або 512x384
- Зменшіть steps: 10-20
- Використовуйте sd15 замість sdxl

### "Connection refused"
- Перевірте URL у config.json
- Перевірте Colab notebook все ще запущений
- Перезапустіть обидва

## 💡 Поради

1. **Завжди мати ngrok tab відкритим** - URL може змінитися
2. **Робіть скріншоти URL** - Щоб не забути
3. **Тримайте Runtime запущеним** - Закрийте Colab - значить сервер вимкнеться
4. **Використовуйте GPU T4** - За замовчуванням
5. **Завантажуйте моделі один раз** - Потім лежать в /content

## 📊 Часи генерування

| Модель | GPU T4 | Розмір | Steps |
|--------|--------|--------|-------|
| sd15 | ~30 сек | 512x512 | 20 |
| sd21 | ~35 сек | 512x512 | 20 |
| sdxl | ~60 сек | 512x512 | 20 |

## ✅ Чек-лист

- [ ] Відкрити Colab
- [ ] Встановити залежності
- [ ] Налаштувати ngrok token
- [ ] Вставити код сервера
- [ ] Копіювати URL
- [ ] Оновити config.json
- [ ] Запустити клієнт
- [ ] Генерувати першу картину!

## 🎉 Готово!

Тепер у вас є:
- ✅ Безплатний сервер на Colab
- ✅ GUI клієнт на вашому комп'ютері
- ✅ Генерування картин через GPU!

**Приємного використання!** 🎨

---

**Дополнительно:**
- 📘 Детальна установка: [SETUP.md](../docs/SETUP.md)
- 🎯 Використання: [USAGE.md](../docs/USAGE.md)
- 🆘 Проблеми: [TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)
