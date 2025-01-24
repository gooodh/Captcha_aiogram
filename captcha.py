
import random

from loguru import logger

from PIL import Image, ImageDraw, ImageFont


def generate_captcha(width, height, code_length):
    captcha_image = Image.new("RGB", (width, height), color="white")
    captcha_draw = ImageDraw.Draw(captcha_image)
    font = ImageFont.truetype("ArialRegular.ttf", 45)  # Путь к шрифту и размер шрифта
    # Генерация случайного проверочного кода
    captcha_code = "".join(
        random.choices("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=code_length)
    )
    logger.debug(f"Сгенерирован код капчи: {captcha_code}")

    # Получить размеры текста
    bbox = captcha_draw.textbbox((0, 0), captcha_code, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
    ]  # Список RGB цветов (красный, зеленый, синий)
    for i, char in enumerate(captcha_code):
        color = random.choice(colors)
        x = text_x + i * (text_width // code_length)
        captcha_draw.text((x, text_y), char, font=font, fill=color)
    # Добавить шум в виде линий
    num_lines = random.randint(2, 33)  # Количество линий шума
    for _ in range(num_lines):
        x1 = random.randint(0, width - 1)
        y1 = 0
        x2 = random.randint(0, width - 1)
        y2 = height - 1
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        captcha_draw.line([(x1, y1), (x2, y2)], fill=color, width=1)

    # Добавить шум в виде точек
    num_points = random.randint(999, 1000)  # Количество точек шума
    for _ in range(num_points):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        captcha_draw.point((x, y), fill=color)

    return captcha_image, captcha_code
