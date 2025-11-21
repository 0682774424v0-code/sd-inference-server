"""
client_gui.py - Графічний клієнт для TEST_EASY

Простий GUI клієнт з підтримкою:
- txt2img
- img2img
- inpaint з редактором маски
"""

import sys
import json
import requests
import base64
from pathlib import Path
from PIL import Image, ImageDraw
import io

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox,
        QComboBox, QTextEdit, QFileDialog, QTabWidget, QScrollArea,
        QMessageBox, QProgressDialog, QFrame
    )
    from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QSize
    HAVE_QT = True
except ImportError:
    HAVE_QT = False
    print("⚠️  PyQt5 не встановлено. Встановіть: pip install PyQt5")


class MaskCanvas(QWidget):
    """Редактор масок для inpaint"""
    
    def __init__(self, image_path=None):
        super().__init__()
        self.image = None
        self.mask = None
        self.brush_size = 20
        self.is_drawing = False
        self.last_point = QPoint()
        
        self.init_canvas(image_path)
        self.setMinimumSize(512, 512)
    
    def init_canvas(self, image_path):
        """Ініціалізувати канвас"""
        if image_path and Path(image_path).exists():
            self.image = Image.open(image_path).convert("RGB")
            # Зменшити розмір для зручності
            self.image.thumbnail((512, 512), Image.Resampling.LANCZOS)
        else:
            self.image = Image.new("RGB", (512, 512), color=(255, 255, 255))
        
        self.mask = Image.new("L", self.image.size, 0)  # Чорна маска
    
    def mousePressEvent(self, event):
        """Почати малювання"""
        if event.button() == Qt.LeftButton:
            self.is_drawing = True
            self.last_point = event.pos()
    
    def mouseMoveEvent(self, event):
        """Малювання під час руху миші"""
        if self.is_drawing:
            self.draw_point(event.pos(), color=255)  # Біла для редагування
            self.last_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """Зупинити малювання"""
        if event.button() == Qt.LeftButton:
            self.is_drawing = False
    
    def draw_point(self, pos, color):
        """Намалювати точку на масці"""
        draw = ImageDraw.Draw(self.mask)
        x, y = pos.x(), pos.y()
        
        # Масштабування відносно розміру віджета
        scale_x = self.mask.width / self.width()
        scale_y = self.mask.height / self.height()
        
        x = int(x * scale_x)
        y = int(y * scale_y)
        
        r = self.brush_size
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
    
    def paintEvent(self, event):
        """Намалювати компонент"""
        painter = QPainter(self)
        
        # Конвертувати PIL Image в QPixmap
        pil_image = self.image.convert("RGB")
        data = pil_image.tobytes("raw", "RGB")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        
        # Масштабувати для відображення
        scaled = pixmap.scaled(
            self.width(), self.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled)
        
        # Показати маску напівпрозорою
        mask_pil = self.mask.convert("RGBA")
        mask_data = mask_pil.tobytes("raw", "RGBA")
        mask_qimage = QImage(mask_data, mask_pil.width, mask_pil.height, QImage.Format_RGBA8888)
        mask_pixmap = QPixmap.fromImage(mask_qimage)
        scaled_mask = mask_pixmap.scaled(
            self.width(), self.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        
        painter.setOpacity(0.3)
        painter.drawPixmap(0, 0, scaled_mask)
    
    def clear_mask(self):
        """Очистити маску"""
        self.mask = Image.new("L", self.image.size, 0)
        self.update()
    
    def get_mask(self):
        """Отримати маску"""
        return self.mask
    
    def set_brush_size(self, size):
        """Встановити розмір пензля"""
        self.brush_size = max(1, min(50, size))


class GeneratorThread(QThread):
    """Thread для генерації без блокування UI"""
    finished = pyqtSignal(Image.Image)
    error = pyqtSignal(str)
    
    def __init__(self, generator_func, params):
        super().__init__()
        self.generator_func = generator_func
        self.params = params
    
    def run(self):
        try:
            result = self.generator_func(**self.params)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class EasyClientGUI(QMainWindow):
    """Основний GUI класс"""
    
    def __init__(self):
        super().__init__()
        
        # Конфіг
        self.config_file = "config.json"
        self.load_config()
        
        # HTTP клієнт
        self.session = requests.Session()
        
        self.initUI()
    
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
            }
            self.save_config()
    
    def save_config(self):
        """Зберегти конфіг"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def initUI(self):
        """Ініціалізувати UI"""
        self.setWindowTitle("🎨 TEST_EASY Client")
        self.setGeometry(100, 100, 900, 700)
        
        # Головний виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        
        # URL сервера
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Сервер URL:"))
        self.url_input = QLineEdit(self.config.get("server_url", ""))
        url_layout.addWidget(self.url_input)
        test_btn = QPushButton("🧪 Тест")
        test_btn.clicked.connect(self.test_server)
        url_layout.addWidget(test_btn)
        layout.addLayout(url_layout)
        
        # Таби для різних режимів
        self.tabs = QTabWidget()
        
        # txt2img таб
        self.tabs.addTab(self.create_txt2img_tab(), "🎨 txt2img")
        
        # img2img таб
        self.tabs.addTab(self.create_img2img_tab(), "🖼️ img2img")
        
        # inpaint таб
        self.tabs.addTab(self.create_inpaint_tab(), "🎭 inpaint")
        
        layout.addWidget(self.tabs)
        main_widget.setLayout(layout)
    
    def create_txt2img_tab(self):
        """Створити txt2img таб"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Промпт
        layout.addWidget(QLabel("Промпт:"))
        self.txt2img_prompt = QTextEdit()
        self.txt2img_prompt.setMinimumHeight(80)
        layout.addWidget(self.txt2img_prompt)
        
        # Negative prompt
        layout.addWidget(QLabel("Negative Prompt:"))
        self.txt2img_negative = QTextEdit()
        self.txt2img_negative.setMinimumHeight(50)
        layout.addWidget(self.txt2img_negative)
        
        # Параметри
        params_layout = QVBoxLayout()
        
        # Checkpoint
        params_layout.addWidget(QLabel("Checkpoint:"))
        self.txt2img_checkpoint = QComboBox()
        self.txt2img_checkpoint.addItems(["sd15", "sd21", "sdxl"])
        params_layout.addWidget(self.txt2img_checkpoint)
        
        # Розмір
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.txt2img_width = QSpinBox()
        self.txt2img_width.setValue(self.config.get("default_width", 512))
        self.txt2img_width.setSingleStep(64)
        size_layout.addWidget(self.txt2img_width)
        size_layout.addWidget(QLabel("Height:"))
        self.txt2img_height = QSpinBox()
        self.txt2img_height.setValue(self.config.get("default_height", 512))
        self.txt2img_height.setSingleStep(64)
        size_layout.addWidget(self.txt2img_height)
        params_layout.addLayout(size_layout)
        
        # Steps та Scale
        advanced_layout = QHBoxLayout()
        advanced_layout.addWidget(QLabel("Steps:"))
        self.txt2img_steps = QSpinBox()
        self.txt2img_steps.setValue(self.config.get("default_steps", 20))
        self.txt2img_steps.setRange(1, 100)
        advanced_layout.addWidget(self.txt2img_steps)
        advanced_layout.addWidget(QLabel("Scale:"))
        self.txt2img_scale = QDoubleSpinBox()
        self.txt2img_scale.setValue(self.config.get("default_scale", 7.5))
        self.txt2img_scale.setRange(1.0, 20.0)
        self.txt2img_scale.setSingleStep(0.5)
        advanced_layout.addWidget(self.txt2img_scale)
        params_layout.addLayout(advanced_layout)
        
        layout.addLayout(params_layout)
        
        # Кнопка генерації
        self.txt2img_btn = QPushButton("🎨 Генерувати")
        self.txt2img_btn.clicked.connect(self.do_txt2img)
        layout.addWidget(self.txt2img_btn)
        
        # Результат
        self.txt2img_result = QLabel()
        self.txt2img_result.setMinimumHeight(300)
        layout.addWidget(self.txt2img_result)
        
        widget.setLayout(layout)
        return widget
    
    def create_img2img_tab(self):
        """Створити img2img таб"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Вибір зображення
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("Зображення:"))
        self.img2img_file = QLineEdit()
        img_layout.addWidget(self.img2img_file)
        browse_btn = QPushButton("📂 Вибрати")
        browse_btn.clicked.connect(lambda: self.browse_image("img2img"))
        img_layout.addWidget(browse_btn)
        layout.addLayout(img_layout)
        
        # Промпт
        layout.addWidget(QLabel("Промпт:"))
        self.img2img_prompt = QTextEdit()
        self.img2img_prompt.setMinimumHeight(80)
        layout.addWidget(self.img2img_prompt)
        
        # Параметри
        params_layout = QVBoxLayout()
        
        params_layout.addWidget(QLabel("Strength (0.0-1.0):"))
        self.img2img_strength = QDoubleSpinBox()
        self.img2img_strength.setValue(0.75)
        self.img2img_strength.setRange(0.0, 1.0)
        self.img2img_strength.setSingleStep(0.05)
        params_layout.addWidget(self.img2img_strength)
        
        layout.addLayout(params_layout)
        
        # Кнопка
        self.img2img_btn = QPushButton("🖼️ Генерувати")
        self.img2img_btn.clicked.connect(self.do_img2img)
        layout.addWidget(self.img2img_btn)
        
        # Результат
        self.img2img_result = QLabel()
        self.img2img_result.setMinimumHeight(300)
        layout.addWidget(self.img2img_result)
        
        widget.setLayout(layout)
        return widget
    
    def create_inpaint_tab(self):
        """Створити inpaint таб"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Вибір зображення
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("Зображення:"))
        self.inpaint_file = QLineEdit()
        img_layout.addWidget(self.inpaint_file)
        browse_btn = QPushButton("📂 Вибрати")
        browse_btn.clicked.connect(lambda: self.browse_image("inpaint"))
        img_layout.addWidget(browse_btn)
        layout.addLayout(img_layout)
        
        # Редактор маски
        layout.addWidget(QLabel("Редактор маски (білий = редагувати):"))
        self.mask_canvas = MaskCanvas()
        layout.addWidget(self.mask_canvas)
        
        # Контролі маски
        mask_controls = QHBoxLayout()
        brush_label = QLabel("Розмір пензля:")
        mask_controls.addWidget(brush_label)
        brush_spin = QSpinBox()
        brush_spin.setValue(20)
        brush_spin.setRange(1, 50)
        brush_spin.valueChanged.connect(self.mask_canvas.set_brush_size)
        mask_controls.addWidget(brush_spin)
        clear_btn = QPushButton("🗑️ Очистити маску")
        clear_btn.clicked.connect(self.mask_canvas.clear_mask)
        mask_controls.addWidget(clear_btn)
        layout.addLayout(mask_controls)
        
        # Промпт
        layout.addWidget(QLabel("Промпт:"))
        self.inpaint_prompt = QTextEdit()
        self.inpaint_prompt.setMinimumHeight(60)
        layout.addWidget(self.inpaint_prompt)
        
        # Кнопка
        self.inpaint_btn = QPushButton("🎭 Генерувати")
        self.inpaint_btn.clicked.connect(self.do_inpaint)
        layout.addWidget(self.inpaint_btn)
        
        # Результат
        self.inpaint_result = QLabel()
        self.inpaint_result.setMinimumHeight(250)
        layout.addWidget(self.inpaint_result)
        
        widget.setLayout(layout)
        return widget
    
    def browse_image(self, mode):
        """Вибрати зображення"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Вибрати зображення", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            if mode == "img2img":
                self.img2img_file.setText(file_path)
            elif mode == "inpaint":
                self.inpaint_file.setText(file_path)
                self.mask_canvas.init_canvas(file_path)
                self.mask_canvas.update()
    
    def test_server(self):
        """Тестувати сервер"""
        url = self.url_input.text() or self.config.get("server_url", "")
        
        try:
            response = self.session.get(f"{url}/status", timeout=5)
            if response.status_code == 200:
                QMessageBox.information(self, "✅ Успіх", "Сервер доступний!")
            else:
                QMessageBox.warning(self, "❌ Помилка", f"HTTP {response.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Помилка", f"Не можна підключитися: {e}")
    
    def do_txt2img(self):
        """Виконати txt2img"""
        url = self.url_input.text() or self.config.get("server_url", "")
        
        params = {
            "prompt": self.txt2img_prompt.toPlainText(),
            "negative_prompt": self.txt2img_negative.toPlainText(),
            "checkpoint": self.txt2img_checkpoint.currentText(),
            "width": self.txt2img_width.value(),
            "height": self.txt2img_height.value(),
            "steps": self.txt2img_steps.value(),
            "scale": self.txt2img_scale.value(),
        }
        
        self.generate_image(f"{url}/txt2img", params, self.txt2img_result)
    
    def do_img2img(self):
        """Виконати img2img"""
        url = self.url_input.text() or self.config.get("server_url", "")
        file_path = self.img2img_file.text()
        
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "❌ Помилка", "Виберіть зображення")
            return
        
        image = Image.open(file_path).convert("RGB")
        image_base64 = self.image_to_base64(image)
        
        params = {
            "prompt": self.img2img_prompt.toPlainText(),
            "image": image_base64,
            "strength": self.img2img_strength.value(),
        }
        
        self.generate_image(f"{url}/img2img", params, self.img2img_result)
    
    def do_inpaint(self):
        """Виконати inpaint"""
        url = self.url_input.text() or self.config.get("server_url", "")
        file_path = self.inpaint_file.text()
        
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "❌ Помилка", "Виберіть зображення")
            return
        
        image = Image.open(file_path).convert("RGB")
        image_base64 = self.image_to_base64(image)
        mask_base64 = self.image_to_base64(self.mask_canvas.get_mask())
        
        params = {
            "prompt": self.inpaint_prompt.toPlainText(),
            "image": image_base64,
            "mask": mask_base64,
        }
        
        self.generate_image(f"{url}/inpaint", params, self.inpaint_result)
    
    def generate_image(self, url, params, result_label):
        """Генерувати зображення"""
        try:
            response = self.session.post(url, json=params, timeout=600)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    image_base64 = data.get('image', '')
                    image = self.base64_to_image(image_base64)
                    
                    pixmap = QPixmap.fromImage(self.pil_to_qimage(image))
                    scaled = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
                    result_label.setPixmap(scaled)
                    
                    # Зберегти результат
                    image.save("last_result.png")
                    QMessageBox.information(self, "✅ Успіх", "Зображення готово!\nЗбережено в last_result.png")
                else:
                    QMessageBox.critical(self, "❌ Помилка", data.get('error', 'Unknown error'))
            else:
                QMessageBox.critical(self, "❌ Помилка", f"HTTP {response.status_code}")
        
        except Exception as e:
            QMessageBox.critical(self, "❌ Помилка", f"Помилка запиту: {e}")
    
    @staticmethod
    def image_to_base64(image):
        """Конвертувати PIL Image в base64"""
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    @staticmethod
    def base64_to_image(img_base64):
        """Конвертувати base64 в PIL Image"""
        img_data = base64.b64decode(img_base64)
        return Image.open(io.BytesIO(img_data))
    
    @staticmethod
    def pil_to_qimage(pil_image):
        """Конвертувати PIL Image в QImage"""
        rgb_image = pil_image.convert("RGB")
        data = rgb_image.tobytes("raw", "RGB")
        qimage = QImage(data, rgb_image.width, rgb_image.height, QImage.Format_RGB888)
        return qimage


def main():
    """Головна функція"""
    if not HAVE_QT:
        print("❌ PyQt5 не встановлено. Встановіть:")
        print("   pip install PyQt5")
        return
    
    app = QApplication(sys.argv)
    client = EasyClientGUI()
    client.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
