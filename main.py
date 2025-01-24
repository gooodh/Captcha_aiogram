import asyncio
import os
from loguru import logger

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.types import FSInputFile


from captcha import generate_captcha
from config import token, width, height, code_length

bot = Bot(token)
dp = Dispatcher()


class CaptchaStates(StatesGroup):
    captcha = State()


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

