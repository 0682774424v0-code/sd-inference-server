# 🎨 TEST_EASY - Просто & Легко Stable Diffusion

> Спрощена версія sd-inference-server з підтримкою txt2img, img2img, inpaint. Сервер на Google Colab, клієнт Python GUI/CLI.

![Status](https://img.shields.io/badge/status-beta-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 🚀 Швидкий старт (30 секунд)

### Варіант 1: Google Colab (Рекомендовано)

1. **Відкрити Colab**
   ```
   https://colab.research.google.com/
   ```

2. **Копіювати код з `server/colab_server.py`** → Запустити

3. **Скопіювати ngrok URL** з виводу

4. **На своєму комп'ютері:**
   ```bash
   pip install PyQt5 requests pillow
   python client/client_gui.py
   ```

5. **Встановити URL** у конфігу → Генерувати!

### Варіант 2: Локально

```bash
# Встановити
pip install torch diffusers transformers PyQt5 requests pillow
cd TEST_EASY/server
python colab_server.py

# В іншому терміналі
cd TEST_EASY/client
python client_gui.py
```

## 📋 Характеристики

| Режим | GUI | CLI | Опис |
|-------|-----|-----|------|
| **txt2img** | ✅ | ✅ | Текст → Зображення |
| **img2img** | ✅ | ✅ | Модифікація зображення |
| **inpaint** | ✅ | ✅ | Редагування з маскою |

### Моделі

- ✅ Stable Diffusion 1.5 (швидка)
- ✅ Stable Diffusion 2.1 (якісніша)  
- ✅ Stable Diffusion XL (найякісніша)
- ✅ LoRA підтримка
- ✅ Upscaling (4x)

### Особливості

- 🔄 Асинхронна генерація (без заморозки GUI)
- 🎨 Редактор масок для inpaint
- 📊 Відображення статусу GPU
- 💾 Автозбереження результатів
- 🌐 Colab + ngrok для хмари
- 🖥️ Потенціал EXE компіляції

## 📁 Структура проекту

```
TEST_EASY/
├── 📘 README.md                    # Цей файл
├── server/
│   ├── colab_server.py             # Flask сервер для Colab
│   ├── easy_wrapper.py             # Ядро генерування
│   └── requirements.txt
├── client/
│   ├── client_gui.py               # GUI клієнт (PyQt5)
│   ├── client_cli.py               # CLI клієнт
│   ├── config.json                 # Конфіг
│   └── README_CLIENT.md
├── docs/
│   ├── SETUP.md                    # Встановлення
│   ├── USAGE.md                    # Використання
│   ├── API.md                      # API документація
│   └── TROUBLESHOOTING.md          # Розв'язання проблем
└── examples/
    ├── example_txt2img.py          # Приклади txt2img
    ├── example_img2img.py          # Приклади img2img
    ├── example_inpaint.py          # Приклади inpaint
    └── batch_txt2img.py            # Batch обробка
```

## 🔧 Встановлення

### Вимоги

- **Python** 3.8+
- **RAM** 4GB+ (8GB рекомендовано)
- **VRAM** для GPU (опціонально, але рекомендовано)
- **Internet** для завантаження моделей

### Залежності

```bash
pip install torch diffusers transformers
pip install accelerate safetensors pillow
pip install flask flask-cors pyngrok requests
pip install PyQt5 opencv-python  # Для GUI
```

### Крок за кроком

1. **Клонувати/Завантажити**
   ```bash
   cd TEST_EASY
   ```

2. **Віртуальне середовище** (рекомендовано)
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # або
   venv\Scripts\activate     # Windows
   ```

3. **Встановити залежності**
   ```bash
   pip install -r server/requirements.txt
   pip install PyQt5  # Для GUI
   ```

4. **Завантажити моделі** (при першому запуску автоматично)

## 💻 Використання

### GUI Клієнт

```bash
python client/client_gui.py
```

**Інтерфейс:**
- 📝 **txt2img** - Введіть промпт, натисніть генерувати
- 🖼️ **img2img** - Виберіть зображення, встановіть strength
- 🎭 **inpaint** - Малюйте маску, редагуйте область

### CLI Клієнт

```bash
# txt2img
python client/client_cli.py txt2img --prompt "cute cat" --steps 30

# img2img
python client/client_cli.py img2img --image input.png --prompt "oil painting" --strength 0.7

# inpaint
python client/client_cli.py inpaint --image photo.png --mask mask.png --prompt "blue eyes"

# status
python client/client_cli.py status
```

### Сервер

**Colab:**
```python
# Скопіюйте код з server/colab_server.py в Colab
# Виконайте ячейки
# Сервер запуститься з ngrok URL
```

**Локально:**
```bash
cd server
python colab_server.py
# Запустити на http://localhost:5000
```

## 🎨 Приклади

### txt2img - Простий кіт

```python
python client/client_cli.py txt2img \
  --prompt "cute fluffy cat, professional photo, 4k, detailed" \
  --checkpoint sd15 \
  --steps 30 \
  --output cat.png
```

### img2img - Художній стиль

```python
python client/client_cli.py img2img \
  --image photo.jpg \
  --prompt "oil painting style, masterpiece" \
  --strength 0.75 \
  --output painting.png
```

### inpaint - Змінити очі

```python
python client/client_cli.py inpaint \
  --image portrait.jpg \
  --mask eyes_mask.png \
  --prompt "beautiful blue eyes" \
  --output portrait_blue_eyes.jpg
```

### Batch обробка

```bash
python examples/batch_txt2img.py --mode prompts --output results/
```

## 📊 Архітектура

```
┌─────────────────────────────────────┐
│  Клієнт (GUI/CLI)                   │
│  client_gui.py / client_cli.py       │
└──────────────┬──────────────────────┘
               │ JSON + base64 images
               │ HTTP (requests)
               ▼
┌─────────────────────────────────────┐
│  Сервер (Flask)                     │
│  colab_server.py / Flask app        │
└──────────────┬──────────────────────┘
               │ Python API
               ▼
┌─────────────────────────────────────┐
│  Генератор (PyTorch)                │
│  easy_wrapper.py / SimpleGenerator  │
└──────────────┬──────────────────────┘
               │ Diffusers
               ▼
┌─────────────────────────────────────┐
│  Моделі (Hugging Face)              │
│  SD15 / SD21 / SDXL                 │
└─────────────────────────────────────┘
```

## 🔐 Безпека

- ✅ Локальна обробка на Colab (ваші дані не залишають сесію)
- ✅ HTTPS через ngrok tunnel
- ✅ Без зберігання даних на сервері
- ✅ Вихідний код відкритий

## 📈 Продуктивність

| Параметр | GPU T4 | GPU A100 | CPU |
|----------|--------|----------|-----|
| txt2img 512x512 | ~30 сек | ~5 сек | ~5 хвилин |
| img2img | ~20 сек | ~3 сек | ~3 хвилини |
| inpaint | ~20 сек | ~3 сек | ~3 хвилини |

**Поради для прискорення:**
- Використовуйте GPU (NVIDIA > AMD > CPU)
- Зменшіть розмір (512x512 < 768x512)
- Зменшіть steps (20 < 30 < 50)
- Включіть xformers: `pip install xformers`

## 🐛 Розв'язання проблем

### "Не можна підключитися до сервера"

```bash
# Перевірити URL
python client/client_cli.py status --server http://your-url

# Перевірити ngrok tunnel активна (Colab)
# Перезапустити сервер
```

### "Out of Memory"

```bash
# Зменшіть розмір або steps
# Використовуйте float16
# На CPU - додайте доп. пам'ять swap
```

### "Сервер перепаває"

```bash
# Перезапустити kernel (Colab)
# Очистити кеш моделей
# rm -rf ~/.cache/huggingface/hub/
```

## 📚 Документація

- **[SETUP.md](docs/SETUP.md)** - Детальна встановлення
- **[USAGE.md](docs/USAGE.md)** - Путівник користувача
- **[API.md](docs/API.md)** - API специфікація
- **[TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - FAQ

## 🎓 Навчальні матеріали

### Приклади

```bash
# txt2img варіації
python examples/example_txt2img.py --example 1

# Batch обробка
python examples/batch_txt2img.py --mode styles

# Параметри
python examples/batch_txt2img.py --mode params
```

### Промпт-інженерія

**Добрі промпти:**
```
- "beautiful woman, elegant dress, intricate details, professional lighting"
- "steampunk airship, detailed mechanical, sunset sky, digital art"
- "japanese garden, stone lantern, serene atmosphere, detailed"
```

**Негативні промпти:**
```
- "blurry, low quality, distorted, ugly, deformed"
- "watermark, text, signature, extra limbs"
```

## 🚀 Майбутні функції

- [ ] LoRA менеджер
- [ ] Controlnet підтримка
- [ ] Batch процесс з прогресом
- [ ] EXE компіляція (PyInstaller)
- [ ] Вебінтерфейс
- [ ] API документація з Swagger
- [ ] Docker підтримка
- [ ] GPU вибір
- [ ] Історія генерацій
- [ ] Image-to-image варіанти

## 💬 Внески

Приєднуйтесь до розвитку!

```bash
# Fork → Clone → Edit → Push → PR
git clone <your-fork>
cd TEST_EASY
# Внесіть зміни
git push origin feature/your-feature
```

## 📄 Ліцензія

MIT License - див. [LICENSE](LICENSE)

## 🙏 Подякування

- [Stable Diffusion](https://github.com/CompVis/stable-diffusion)
- [diffusers](https://github.com/huggingface/diffusers)
- [Hugging Face](https://huggingface.co/)
- [PyTorch](https://pytorch.org/)

## 👨‍💻 Автори

- TEST_EASY Project
- Community Contributors

## 📞 Контакти

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/example/TEST_EASY/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/example/TEST_EASY/discussions)

## ⭐ Допоможіть проекту

Якщо вам подобається TEST_EASY, будь ласка:
- ⭐ Дайте зірку на GitHub
- 🔄 Поділіться з друзями
- 💬 Залиште відгук
- 🐛 Повідомте про баги
- 🎨 Внесіть удосконалення

---

**Останнє оновлення:** Грудень 2024  
**Версія:** 1.0.0-beta  
**Статус:** Активний розвиток 🚀

```
╔════════════════════════════════════════╗
║  🎨 Тепер генеруй!                     ║
║  TEST_EASY - Простота в дії            ║
╚════════════════════════════════════════╝
```
