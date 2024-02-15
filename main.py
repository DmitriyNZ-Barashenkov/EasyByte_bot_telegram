import asyncio
import logging
from aiogram import Bot
from aiogram.client.session import aiohttp
from aiogram.filters import Command
from aiogram import Dispatcher
from aiogram.types import Message
from dotenv import load_dotenv
import os

load_dotenv()


dp = Dispatcher()

bot = Bot(os.getenv("TOKEN"))


logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] -  %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
logging.info("Отладочная информация")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@dp.message(Command(commands=["start", "Start", "старт", "Старт"]))
async def cmd_start(message: Message):
    await message.answer(f"  Привет, {message.from_user.full_name}!\n"
                         f"Приветствую вас! Я бот, который поможет вам конвертировать валюты. Вот список доступных команд:\n"
                         f"/start - начать работу с ботом\n /help - получить информацию о доступных командах\n /convert - выбрать валюту и конвертировать ее.\n"
                         f"Чтобы воспользоваться командой /convert, "
                         f"вам нужно будет выбрать валюту, которую вы хотите сконвертировать, "
                         f"а затем валюту, в которую вы хотите ее конвертировать. Пример: 10 USD RUB\n"
                         f"Например, что бы конвертировать доллары в евро, вам нужно будет выбрать USD и EUR.\n"
                         f"Не стесняйтесь задавать вопросы или просить помощи - я всегда готов помочь вам в конвертации валюты.")

@dp.message(Command(commands=["Help", "help", "Хелп", "хелп", "Помощь", "помощь"]))
async def cmd_help(message: Message):
    await message.answer(f"Чем могу помочь, {message.from_user.first_name}? Привет! Я бот, который поможет тебе конвертировать валюты быстро и без лишних усилий. Вот список доступных команд:\n "
                         f"/start: запускает бота и позволяет начать использовать его функции.\n"
                         f"/help: выводит список доступных команд и краткую информацию о каждой из них.\n"
                         f"/convert: позволяет конвертировать одну валюту в другую. Просто укажи валюту, которую нужно конвертировать, "
                         f"ее сумму, а также валюту, в которую хочешь произвести конвертацию.\n"
                         f"Например, чтобы конвертировать 100 долларов в евро, введи следующую команду: /convert 100 USD to EUR"
                         f"Я обработаю твой запрос и предоставлю тебе актуальные данные о конвертации валюты.\n"
                         f"Если у тебя есть вопросы или нужна помощь, не стесняйся обращаться к команде /help. Я всегда готов помочь!")

@dp.message(Command(commands=["convert", "conv", "конвертировать"]))
async def cmd_convert(message: Message):
    #await message.answer("Введите сумму и валюту для конвертации (например, '10 USD to RUB'):")
    # разбивается на части с помощью метода split(),
    # чтобы получить сумму, исходную валюту и целевую валюту.
    user_input = message.text.split()

    if len(user_input) != 4:
        await message.answer("Неверный формат команды! Пожалуйста, используйте: /convert <сумма> <из_валюты> <в_валюту>")
        return

    amount = float(user_input[1])
    from_currency = user_input[2].upper()
    to_currency = user_input[3].upper()

    # Отправляем запрос к сервису конвертации валют
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await message.answer("Не удалось получить данные о курсе валют.")
                return

            data = await response.json()

    if to_currency not in data['rates']:
        await message.answer("Неверно указана валюта для конвертации!")
        return

    rate = data['rates'][to_currency]
    result = amount * rate

    await message.reply(f"{amount} {from_currency} = {result} {to_currency}")


@dp.message()
async def handle_text(message: Message):
    logger.info(f"Пользователь {message.from_user.username} отправил сообщение: {message.text}")
    text = message.text.lower()
    if text.startswith('привет'):
        await message.answer("Привет!")
    elif text.startswith('пока') or text.startswith('до свидания'):
        await message.answer("Пока!")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

