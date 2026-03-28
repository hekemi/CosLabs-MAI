"""
Телеграм-бот для получения курсов валют ЦБ РФ.

Запуск:
    1. Установите зависимости: pip install -r requirements.txt
    2. Скопируйте .env.example в .env и укажите токен бота.
    3. Запустите: python bot.py

Используемая библиотека: aiogram 3.x (https://docs.aiogram.dev/)
"""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from currency import fetch_currencies, CurrencyFetchError

# ---------------------------------------------------------------------------
# Настройка логирования
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Инициализация бота
# ---------------------------------------------------------------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError(
        "Токен бота не задан. Укажите переменную окружения BOT_TOKEN "
        "или создайте файл .env на основе .env.example."
    )

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------

CURRENCIES_PER_ROW = 5
HELP_TEXT = (
    "💰 <b>Бот курсов валют ЦБ РФ</b>\n\n"
    "Данные берутся с официального сайта Центрального Банка России "
    "(те же данные, что публикует <i>www.rbc.ru</i> в разделе «Курсы ЦБ РФ»).\n\n"
    "<b>Команды:</b>\n"
    "/start — приветствие и список команд\n"
    "/rates — показать все доступные валюты\n"
    "/help — эта справка"
)


async def build_currency_keyboard() -> InlineKeyboardMarkup:
    """Создаёт инлайн-клавиатуру со списком всех доступных валют."""
    currencies = await fetch_currencies()
    codes = sorted(currencies.keys())

    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []

    for code in codes:
        row.append(
            InlineKeyboardButton(text=code, callback_data=f"rate:{code}")
        )
        if len(row) == CURRENCIES_PER_ROW:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return InlineKeyboardMarkup(inline_keyboard=rows)


# ---------------------------------------------------------------------------
# Обработчики команд
# ---------------------------------------------------------------------------

@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, <b>{message.from_user.full_name}</b>! 👋\n\n" + HELP_TEXT,
        parse_mode="HTML",
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")


@dp.message(Command("rates"))
async def cmd_rates(message: Message) -> None:
    """Отправляет клавиатуру с выбором валюты."""
    processing = await message.answer("⏳ Загружаю список валют…")
    try:
        keyboard = await build_currency_keyboard()
        await processing.edit_text(
            "📋 <b>Выберите валюту</b>, чтобы узнать её текущий курс к рублю:",
            parse_mode="HTML",
            reply_markup=keyboard,
        )
    except CurrencyFetchError as exc:
        logger.error("Ошибка при загрузке списка валют: %s", exc)
        await processing.edit_text(
            f"❌ Не удалось загрузить список валют: {exc}"
        )
    except Exception as exc:
        logger.exception("Неожиданная ошибка при загрузке списка валют: %s", exc)
        await processing.edit_text(
            "❌ Не удалось загрузить список валют. Попробуйте позже."
        )


# ---------------------------------------------------------------------------
# Обработчик нажатий инлайн-кнопок
# ---------------------------------------------------------------------------

@dp.callback_query(F.data.startswith("rate:"))
async def on_currency_selected(callback: CallbackQuery) -> None:
    """Показывает курс выбранной валюты."""
    code = callback.data.split(":", 1)[1]
    await callback.answer()  # убираем «часики» на кнопке

    try:
        currencies = await fetch_currencies()
    except CurrencyFetchError as exc:
        logger.error("Ошибка при загрузке курсов: %s", exc)
        await callback.message.answer(f"❌ {exc}")
        return
    except Exception as exc:
        logger.exception("Неожиданная ошибка при загрузке курсов: %s", exc)
        await callback.message.answer(
            "❌ Не удалось получить данные с сайта ЦБ РФ. Попробуйте позже."
        )
        return

    currency = currencies.get(code)
    if not currency:
        await callback.message.answer(
            f"⚠️ Валюта <b>{code}</b> не найдена в списке ЦБ РФ.",
            parse_mode="HTML",
        )
        return

    text = (
        f"💱 <b>Курс ЦБ РФ</b>\n\n"
        f"{currency}\n\n"
        f"📌 <i>Курс за 1 ед.: {currency.rate_per_one:.4f} руб.</i>"
    )
    await callback.message.answer(text, parse_mode="HTML")


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------

async def main() -> None:
    logger.info("Бот запущен. Ожидание сообщений…")
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
