# 📦 TEST_EASY - Документація встановлення

## Системні вимоги

### Мінімальні вимоги:
- **Python**: 3.8+
- **RAM**: 4GB (8GB рекомендовано)
- **Диск**: 5GB (для моделей)
- **Інтернет**: Для завантаження моделей з Hugging Face

### Опціональне:
- **NVIDIA GPU**: Значно швидше (CUDA 11.8+, CUDNN 8.6+)
- **AMD GPU**: Підтримується (ROCm)
- **Apple Silicon**: Підтримується (Metal Performance Shaders)

## Варіант 1: Google Colab (Рекомендовано для більшості)

### Переваги:
✅ Безплатна GPU  
✅ Немає встановлення  
✅ Автоматичне налаштування  
✅ Публічна URL для клієнта  

### Кроки:

1. **Відкрити Colab**
   - Перейдіть на https://colab.research.google.com
   - Натисніть "Новий notebook"

2. **Встановити залежності**
   ```python
   !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 -q
   !pip install diffusers transformers safetensors accelerate flask flask-cors pyngrok pillow requests -q
   ```

3. **Завантажити сервер**
   
   Скопіюйте код з `TEST_EASY/server/colab_server.py` в Colab ячейку і виконайте.
   
   Або завантажте `remote_colab.ipynb`:
   ```python
   # У Colab
   from google.colab import files
   files.upload()
   # Вибиріть remote_colab.ipynb
   ```

4. **Запустити сервер**
   ```python
   # У останній ячейці вже готовий код
   # Просто натисніть Run
   # Видите URL: https://abcd-1234.ngrok.io
   ```

5. **Скопіювати URL**
   - Скопіюйте публічну ngrok URL

6. **Налаштувати клієнт (на своєму комп'ютері)**
   
   Отримайте токен ngrok:
   - Зареєструйтеся на https://ngrok.com
   - СкопіюйтеAuthToken
   - У Colab додайте:
   ```python
   os.environ['NGROK_AUTHTOKEN'] = 'YOUR_TOKEN'
   ```

## Варіант 2: Локальна установка (Windows/Linux/Mac)

### Встановлення Python

#### Windows:
```powershell
# Завантажити з https://www.python.org/downloads/
# Або використовувати Anaconda:
# https://www.anaconda.com/download

# Перевірити
python --version
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install python3-venv python3-pip
python3 --version
```

#### macOS:
```bash
# Встановити Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Встановити Python
brew install python@3.11

python3 --version
```

### Налаштування проекту

#### 1. Клонувати/завантажити проект

```bash
# Якщо використовуєте Git
git clone <repository-url>
cd TEST_EASY

# Або просто завантажити ZIP та розпакувати
cd TEST_EASY
```

#### 2. Створити віртуальне середовище

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Встановити залежності

```bash
# Базові залежності
pip install --upgrade pip setuptools wheel

# PyTorch (CPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Або PyTorch (NVIDIA GPU - CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Або PyTorch (AMD GPU - ROCm)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7

# Основні залежності
pip install -r requirements.txt
```

### requirements.txt для локальної установки

```
diffusers==0.24.0
transformers==4.36.0
safetensors==0.4.0
accelerate==0.24.0
omegaconf==2.3.0
pillow==10.1.0
requests==2.31.0
flask==3.0.0
flask-cors==4.0.0
pyngrok==5.2.2
opencv-python==4.8.0
numpy==1.24.0
PyQt5==5.15.9
```

Встановити:
```bash
pip install -r requirements.txt
```

## Варіант 3: Docker (Для продвинутих користувачів)

### Dockerfile

```dockerfile
FROM nvidia/cuda:11.8.0-runtime-ubuntu22.04

WORKDIR /app

# Встановити Python
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    git curl

# Копіювати проект
COPY TEST_EASY /app/TEST_EASY

# Встановити залежності
RUN pip install --upgrade pip && \
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 && \
    pip install -r /app/TEST_EASY/requirements.txt

WORKDIR /app/TEST_EASY

# Запустити сервер
CMD ["python", "server/colab_server.py"]
```

Збірка та запуск:
```bash
docker build -t test-easy-server .
docker run --gpus all -p 5000:5000 test-easy-server
```

## Установка клієнтів

### GUI Клієнт (на своєму комп'ютері)

#### Вимоги:
- Python 3.8+
- PyQt5
- requests
- Pillow

#### Встановлення:

```bash
# 1. Перейти в папку клієнта
cd TEST_EASY/client

# 2. Встановити залежності
pip install PyQt5 requests pillow

# 3. Запустити
python client_gui.py
```

#### Оновлення конфігу

Відредагуйте `config.json`:
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

### CLI Клієнт

#### Встановлення:

```bash
cd TEST_EASY/client

# Встановити залежності
pip install requests pillow

# Запустити
python client_cli.py --help
```

#### Приклади:

```bash
# txt2img
python client_cli.py txt2img --prompt "cute cat"

# img2img
python client_cli.py img2img --image input.png --prompt "oil painting"

# inpaint
python client_cli.py inpaint --image photo.png --mask mask.png --prompt "blue eyes"
```

## Завантаження моделей

### Першого запуску

При першому запуску будуть автоматично завантажені моделі (~5-10GB):

```
Завантаження моделей:
1. Stable Diffusion 1.5 (4GB)
2. CLIP encoder (1GB)
3. VAE decoder (500MB)
```

Це може зайняти 5-30 хвилин залежно від інтернету.

### Керування моделями

Моделі зберігаються в:
```
~/.cache/huggingface/hub/
```

### Прискорення завантаження

```python
# У config.json або коді
{
  "cache_dir": "/path/to/fast/ssd",
  "torch_dtype": "float16"  # Швидше та менше памяті
}
```

## Розв'язання проблем

### "ModuleNotFoundError: No module named 'torch'"

```bash
# Переустановити PyTorch
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### "CUDA not available"

```bash
# Перевірити CUDA
python -c "import torch; print(torch.cuda.is_available())"

# Якщо False, встановити PyTorch CPU версію
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### "Out of Memory"

```python
# Зменшіть розмір моделі
# У config.json:
{
  "torch_dtype": "float16",  # Замість float32
  "enable_attention_slicing": true
}
```

### "ConnectionError: не можна завантажити модель"

```bash
# Перевірити інтернет
ping huggingface.co

# Встановити Hugging Face токен
huggingface-cli login
# Введіть токен з https://huggingface.co/settings/tokens
```

## Перевірка установки

### Тест сервера

```bash
cd TEST_EASY/server
python -c "from easy_wrapper import EasyGenerator; g = EasyGenerator(); print('✅ OK')"
```

### Тест клієнта

```bash
cd TEST_EASY/client
python client_cli.py status
```

### Повна перевірка

```bash
# Запустити тести (якщо доступні)
python -m pytest tests/
```

## Обновлення

### Оновити залежності

```bash
pip install --upgrade -r requirements.txt
```

### Оновити моделі

```bash
# Видалити кеш
rm -rf ~/.cache/huggingface/hub/

# При наступному запуску буде завантажено нові версії
```

## Оптимізація продуктивності

### Для швидкого генерування:

```python
# У easy_wrapper.py або config
config = {
    "torch_dtype": "float16",
    "enable_attention_slicing": True,
    "use_safetensors": True,
    "use_xformers": True,  # Якщо доступно
}
```

### Встановити xformers (NVIDIA)

```bash
pip install xformers --no-deps
```

### Включити cuDNN на NVIDIA

```bash
export CUDNN_PATH=/path/to/cudnn
export LD_LIBRARY_PATH=$CUDNN_PATH/lib:$LD_LIBRARY_PATH
```

## Наступні кроки

1. ✅ Встановити залежності
2. ✅ Запустити сервер (Colab або локально)
3. ✅ Запустити клієнт
4. 📖 Прочитати [USAGE.md](USAGE.md) для прикладів
5. 🎨 Почати генерувати!

---

**Допомога**:
- 📘 Документація: [README.md](../README.md)
- 🎯 Користування: [USAGE.md](USAGE.md)
- 🆘 Проблеми: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 📧 Контакт: [Support](mailto:support@example.com)
