import asyncio
import os
import random
from loguru import logger

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import FSInputFile

from PIL import Image, ImageDraw, ImageFont

from config import token, width, height, code_length

bot = Bot(token)
dp = Dispatcher()


class CaptchaStates(StatesGroup):
    captcha = State()


def generate_captcha(width, height, code_length):
    captcha_image = Image.new("RGB", (width, height), color="white")
    captcha_draw = ImageDraw.Draw(captcha_image)
    font = ImageFont.truetype("ArialRegular.ttf", 40)  # Путь к шрифту и размер шрифта
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
    num_lines = random.randint(2, 3)  # Количество линий шума
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


@dp.message(Command(commands=["start"]))
async def captcha(message: types.Message, state: FSMContext):
    logger.info("Пользователь запустил команду /start.")
    await message.answer("Введите цифры и буквы с картинки соблюдая регистр:")

    image, captcha_number = generate_captcha(width=width, height=height, code_length=code_length)
    await state.update_data(captcha_number=captcha_number)
    captcha_image = "image.jpg"
    image.save(captcha_image)
    await message.answer_photo(photo=FSInputFile("image.jpg", filename="Captcha"))
    os.remove(captcha_image)
    await state.set_state(CaptchaStates.captcha)


@dp.message(CaptchaStates.captcha, F.text)
async def captcha_handler(message: types.Message, state: FSMContext):
    user_answer = message.text
    data = await state.get_data()
    captcha_number = data.get("captcha_number")
    logger.debug(f"Пользователь ввел ответ: {user_answer}. Ожидаемый ответ: {captcha_number}.")

    if user_answer == str(captcha_number):
        await message.answer("Поздравляю, вы прошли капчу!")
        logger.info("Пользователь успешно прошел капчу.")

        await state.clear()
    else:
        await message.answer("Вы ввели неправильно капчу, попробуйте еще раз.")
        logger.info("Пользователь ввел неправильно капчу.")



async def main():
    logger.info("Бот успешно запущен.")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())

