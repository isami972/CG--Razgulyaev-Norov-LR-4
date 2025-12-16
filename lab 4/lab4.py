import tkinter as tk
from tkinter import filedialog, messagebox
import math

# --- Блок для автоматической установки Pillow ---
import sys
import subprocess
try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    print("Библиотека Pillow не найдена. Выполняется установка...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        print("\nБиблиотека Pillow успешно установлена. Пожалуйста, перезапустите скрипт.")
    except Exception as e:
        print(f"Ошибка при установке Pillow: {e}")
        print("Пожалуйста, установите библиотеку вручную командой: pip install Pillow")
    sys.exit()
# -----------------------------------------

class Lab4App:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №4 - Овал (эллипс)")
        self.root.geometry("1000x900")

        self.images = {}  # Будем хранить все 4 изображения
        self.create_widgets()

    def create_widgets(self):
        input_frame = tk.Frame(self.root, pady=10)
        input_frame.pack(fill=tk.X)

        tk.Label(input_frame, text="Длина главной оси (a):").pack(side=tk.LEFT, padx=5)
        self.axis_a_var = tk.StringVar(value="200")
        tk.Entry(input_frame, textvariable=self.axis_a_var, width=10).pack(side=tk.LEFT)

        tk.Label(input_frame, text="Длина малой оси (b):").pack(side=tk.LEFT, padx=5)
        self.axis_b_var = tk.StringVar(value="100")
        tk.Entry(input_frame, textvariable=self.axis_b_var, width=10).pack(side=tk.LEFT)

        build_btn = tk.Button(input_frame, text="Построить овал", command=self.draw_oval)
        build_btn.pack(side=tk.LEFT, padx=20)

        # Кнопка сохранения всех 4 изображений
        save_btn = tk.Button(input_frame, text="Сохранить все", command=self.save_all_images)
        save_btn.pack(side=tk.LEFT, padx=5)

        # Информация
        info_label = tk.Label(input_frame, text="Овал (эллипс) с осями a и b", fg="blue")
        info_label.pack(side=tk.LEFT, padx=20)

        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.canvases = {}
        self.algorithm_names = {
            "equation": "По уравнению эллипса",
            "parametric": "Параметрический",
            "bresenham": "Алгоритм Брезенхема для эллипса",
            "builtin": "Встроенные средства"
        }

        for i, (algo_key, algo_name) in enumerate(self.algorithm_names.items()):
            frame = tk.LabelFrame(canvas_frame, text=algo_name, padx=5, pady=5)
            frame.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="nsew")
            canvas_frame.grid_rowconfigure(i // 2, weight=1)
            canvas_frame.grid_columnconfigure(i % 2, weight=1)

            canvas = tk.Canvas(frame, bg='white')
            canvas.pack(fill=tk.BOTH, expand=True)
            self.canvases[algo_key] = canvas

    def save_all_images(self):
        """Сохраняет все 4 изображения с разными алгоритмами"""
        if not self.images:
            messagebox.showwarning("Предупреждение", "Сначала постройте овал!")
            return
            
        # Спрашиваем папку для сохранения
        folder_path = filedialog.askdirectory(title="Выберите папку для сохранения изображений")
        
        if not folder_path:
            return
            
        try:
            saved_files = []
            for algo_key, image in self.images.items():
                algo_name = self.algorithm_names[algo_key].replace(" ", "_").lower()
                filename = f"ellipse_{algo_name}.png"
                file_path = f"{folder_path}/{filename}"
                image.save(file_path)
                saved_files.append(filename)
            
            messagebox.showinfo("Успех", f"Все 4 изображения сохранены в папку:\n{folder_path}\n\nСохраненные файлы:\n" + "\n".join(saved_files))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файлы:\n{e}")

    def draw_ellipse_by_equation(self, draw, cx, cy, a, b, color="black"):
        """Рисует эллипс по каноническому уравнению"""
        a2 = a * a
        b2 = b * b
        
        # Рисуем первую четверть
        for x in range(0, a + 1):
            if a2 != 0:
                y = int(b * math.sqrt(1 - x*x / a2))
                # Симметрично отображаем на все 4 четверти
                points = [
                    (cx + x, cy + y),
                    (cx + x, cy - y),
                    (cx - x, cy + y),
                    (cx - x, cy - y)
                ]
                for px, py in points:
                    draw.point((px, py), fill=color)
        
        # Рисуем по y для более плавной кривой
        for y in range(0, b + 1):
            if b2 != 0:
                x = int(a * math.sqrt(1 - y*y / b2))
                points = [
                    (cx + x, cy + y),
                    (cx + x, cy - y),
                    (cx - x, cy + y),
                    (cx - x, cy - y)
                ]
                for px, py in points:
                    draw.point((px, py), fill=color)

    def draw_ellipse_parametric(self, draw, cx, cy, a, b, color="black"):
        """Рисует эллипс параметрическим методом"""
        steps = 360  # Количество точек
        for i in range(steps + 1):
            angle = 2 * math.pi * i / steps
            x = cx + int(a * math.cos(angle))
            y = cy + int(b * math.sin(angle))
            draw.point((x, y), fill=color)

    def draw_ellipse_bresenham(self, draw, cx, cy, a, b, color="black"):
        """Алгоритм Брезенхема для эллипса"""
        a2 = a * a
        b2 = b * b
        two_a2 = 2 * a2
        two_b2 = 2 * b2
        
        # Регион 1
        x = 0
        y = b
        d = int(b2 - a2 * b + 0.25 * a2)
        
        while two_b2 * x <= two_a2 * y:
            # Симметрично отображаем на все 4 четверти
            points = [
                (cx + x, cy + y),
                (cx - x, cy + y),
                (cx + x, cy - y),
                (cx - x, cy - y)
            ]
            for px, py in points:
                draw.point((px, py), fill=color)
            
            x += 1
            if d < 0:
                d += two_b2 * x + b2
            else:
                y -= 1
                d += two_b2 * x - two_a2 * y + b2
        
        # Регион 2
        d = int(b2 * (x + 0.5) * (x + 0.5) + a2 * (y - 1) * (y - 1) - a2 * b2)
        
        while y >= 0:
            # Симметрично отображаем на все 4 четверти
            points = [
                (cx + x, cy + y),
                (cx - x, cy + y),
                (cx + x, cy - y),
                (cx - x, cy - y)
            ]
            for px, py in points:
                draw.point((px, py), fill=color)
            
            y -= 1
            if d > 0:
                d += a2 - two_a2 * y
            else:
                x += 1
                d += two_b2 * x - two_a2 * y + a2

    def draw_oval(self):
        try:
            a = int(self.axis_a_var.get())  # Полуось по X
            b = int(self.axis_b_var.get())  # Полуось по Y
            
            if a <= 0 or b <= 0:
                messagebox.showerror("Ошибка", "Длины осей должны быть положительными числами!")
                return
                
        except ValueError:
            messagebox.showerror("Ошибка", "Параметры должны быть целыми числами!")
            return

        padding = 40
        img_width = a * 2 + padding * 2
        img_height = b * 2 + padding * 2

        cx = img_width // 2
        cy = img_height // 2

        for algo, canvas in self.canvases.items():
            image = Image.new("RGB", (img_width, img_height), "white")
            draw = ImageDraw.Draw(image)

            # Рисуем оси координат
            draw.line([(padding, cy), (img_width - padding, cy)], fill="lightgray", width=1)
            draw.line([(cx, padding), (cx, img_height - padding)], fill="lightgray", width=1)
            
            # Подписи осей
            draw.text((img_width - padding + 5, cy - 10), "X", fill="gray")
            draw.text((cx + 5, padding + 5), "Y", fill="gray")

            if algo == "builtin":
                # Встроенный метод для эллипса
                draw.ellipse(
                    [cx - a, cy - b, cx + a, cy + b],
                    outline="black",
                    width=1
                )
            elif algo == "parametric":
                self.draw_ellipse_parametric(draw, cx, cy, a, b)
            elif algo == "bresenham":
                self.draw_ellipse_bresenham(draw, cx, cy, a, b)
            elif algo == "equation":
                self.draw_ellipse_by_equation(draw, cx, cy, a, b)

            # Подпись с параметрами
            params_text = f"a={a}, b={b}"
            draw.text((10, 10), params_text, fill="blue")

            # Сохраняем изображение для этого алгоритма
            self.images[algo] = image

            # Отображаем на Canvas
            photo = ImageTk.PhotoImage(image)
            canvas.delete("all")
            canvas.create_image(0, 0, anchor=tk.NW, image=photo)
            canvas.image = photo

        messagebox.showinfo("Успех", f"Овал построен!\nПолуоси: a={a}, b={b}\n"
                                    f"Уравнение эллипса: (x²/{a}²) + (y²/{b}²) = 1")

if __name__ == "__main__":
    root = tk.Tk()
    app = Lab4App(root)
    root.mainloop()