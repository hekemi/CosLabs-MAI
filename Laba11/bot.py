import io
import os
import math
import asyncio
import numpy as np
import matplotlib.pyplot as plt

from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BufferedInputFile,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

FUNC_LABELS = {
    "sqrt": "√x",
    "inv": "1/x",
    "exp": "e^x",
}


class DomainError(Exception):
    pass


class CalcState(StatesGroup):
    waiting_x = State()


router = Router()


def apply_func(name: str, x: float) -> float:
    if name == "sqrt":
        if x < 0:
            raise DomainError("Подкоренное выражение < 0")
        return math.sqrt(x)
    if name == "inv":
        if x == 0:
            raise DomainError("Деление на 0")
        return 1.0 / x
    if name == "exp":
        return math.exp(x)
    raise ValueError(f"Неизвестная функция: {name}")


def eval_chain(chain: list[str], x: float) -> float:
    v = x
    for f in chain:  # [F3, F2, F1]
        v = apply_func(f, v)
    return v


def chain_text(chain: list[str]) -> str:
    if not chain:
        return "x -> y (цепочка не собрана)"
    return " -> ".join(["x"] + [FUNC_LABELS[f] for f in chain] + ["y"])


def expected_slot(chain_len: int) -> str:
    return ["F3", "F2", "F1"][chain_len]


def select_keyboard(slot_name: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="√x", callback_data=f"pick:{slot_name}:sqrt")],
        [InlineKeyboardButton(text="1/x", callback_data=f"pick:{slot_name}:inv")],
        [InlineKeyboardButton(text="e^x", callback_data=f"pick:{slot_name}:exp")],
    ])


def main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Собрать модель", callback_data="build")],
        [
            InlineKeyboardButton(text="Показать цепочку", callback_data="show"),
            InlineKeyboardButton(text="Очистить", callback_data="clear"),
        ],
        [
            InlineKeyboardButton(text="Вычислить y(x)", callback_data="calc"),
            InlineKeyboardButton(text="Построить график", callback_data="plot"),
        ],
        [InlineKeyboardButton(text="Сгенерировать VBA", callback_data="vba")],
    ])


def generate_vba(chain: list[str]) -> str:
    lines = [
        "Option Explicit",
        "",
        "Public Function GeneratedModel(ByVal x As Double) As Variant",
        "    On Error GoTo DomainError",
        "    Dim t As Double",
        "    t = x",
    ]
    for i, f in enumerate(chain, start=1):
        if f == "sqrt":
            lines += [
                f"    ' Шаг {i}: √x",
                "    If t < 0 Then",
                "        GeneratedModel = CVErr(xlErrNum)",
                "        Exit Function",
                "    End If",
                "    t = Sqr(t)",
            ]
        elif f == "inv":
            lines += [
                f"    ' Шаг {i}: 1/x",
                "    If t = 0 Then",
                "        GeneratedModel = CVErr(xlErrDiv0)",
                "        Exit Function",
                "    End If",
                "    t = 1# / t",
            ]
        elif f == "exp":
            lines += [
                f"    ' Шаг {i}: e^x",
                "    t = Exp(t)",
            ]
    lines += [
        "",
        "    GeneratedModel = t",
        "    Exit Function",
        "",
        "DomainError:",
        "    GeneratedModel = CVErr(xlErrNum)",
        "End Function",
        "",
        "Public Sub RunGeneratedModel()",
        "    Dim x As Double",
        "    Dim y As Variant",
        "    x = CDbl(InputBox(\"Введите x\"))",
        "    y = GeneratedModel(x)",
        "    If IsError(y) Then",
        "        MsgBox \"x вне области определения\", vbExclamation",
        "    Else",
        "        MsgBox \"y = \" & CStr(y), vbInformation",
        "    End If",
        "End Sub",
    ]
    return "\n".join(lines)


async def get_chain(state: FSMContext) -> list[str]:
    data = await state.get_data()
    return data.get("chain", [])


async def set_chain(state: FSMContext, chain: list[str]):
    await state.update_data(chain=chain)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await set_chain(state, [])
    await state.clear()
    await message.answer(
        "Мини CASE-система.\nСоберите: y = F1(F2(F3(x))).",
        reply_markup=main_keyboard()
    )


@router.callback_query(F.data == "build")
async def cb_build(callback: CallbackQuery, state: FSMContext):
    await set_chain(state, [])
    await state.clear()
    await callback.message.answer("Выберите F3:", reply_markup=select_keyboard("F3"))
    await callback.answer()


@router.callback_query(F.data.startswith("pick:"))
async def cb_pick(callback: CallbackQuery, state: FSMContext):
    _, slot, func = callback.data.split(":")
    chain = await get_chain(state)

    need = expected_slot(len(chain))
    if slot != need:
        await callback.message.answer(f"Сначала выберите {need}.")
        await callback.answer()
        return

    chain.append(func)
    await set_chain(state, chain)

    if len(chain) < 3:
        nxt = expected_slot(len(chain))
        await callback.message.answer(
            f"{slot} = {FUNC_LABELS[func]}\nВыберите {nxt}:",
            reply_markup=select_keyboard(nxt)
        )
    else:
        await callback.message.answer(
            f"Модель собрана:\n{chain_text(chain)}",
            reply_markup=main_keyboard()
        )
    await callback.answer()


@router.callback_query(F.data == "show")
async def cb_show(callback: CallbackQuery, state: FSMContext):
    chain = await get_chain(state)
    await callback.message.answer(chain_text(chain), reply_markup=main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "clear")
async def cb_clear(callback: CallbackQuery, state: FSMContext):
    await set_chain(state, [])
    await state.clear()
    await callback.message.answer("Цепочка очищена.", reply_markup=main_keyboard())
    await callback.answer()


@router.callback_query(F.data == "calc")
async def cb_calc(callback: CallbackQuery, state: FSMContext):
    chain = await get_chain(state)
    if len(chain) != 3:
        await callback.message.answer("Сначала соберите F3, F2, F1.")
        await callback.answer()
        return
    await state.set_state(CalcState.waiting_x)
    await callback.message.answer("Введите x (например: 1.5)")
    await callback.answer()


@router.message(CalcState.waiting_x)
async def on_x(message: Message, state: FSMContext):
    chain = await get_chain(state)
    txt = (message.text or "").strip().replace(",", ".")
    try:
        x = float(txt)
    except ValueError:
        await message.answer("Некорректное число. Введите x ещё раз.")
        return

    try:
        y = eval_chain(chain, x)
        await message.answer(f"x = {x}\ny = {y}")
    except DomainError:
        await message.answer("Значение x не попадает в область определения функции.")
    except Exception:
        await message.answer("Ошибка вычисления.")

    await state.clear()


@router.callback_query(F.data == "plot")
async def cb_plot(callback: CallbackQuery, state: FSMContext):
    chain = await get_chain(state)
    if len(chain) != 3:
        await callback.message.answer("Сначала соберите F3, F2, F1.")
        await callback.answer()
        return

    xs = np.linspace(-5, 5, 600)
    ys = []
    for xv in xs:
        try:
            ys.append(eval_chain(chain, float(xv)))
        except Exception:
            ys.append(np.nan)

    if np.all(np.isnan(ys)):
        await callback.message.answer("На диапазоне [-5;5] нет точек ОДЗ.")
        await callback.answer()
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(xs, ys, linewidth=2)
    ax.set_title(chain_text(chain))
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)

    buf = io.BytesIO()
    fig.tight_layout()
    fig.savefig(buf, format="png", dpi=130)
    plt.close(fig)
    img_bytes = buf.getvalue()

    photo = BufferedInputFile(img_bytes, filename="plot.png")
    await callback.message.answer_photo(photo=photo)
    await callback.answer()


@router.callback_query(F.data == "vba")
async def cb_vba(callback: CallbackQuery, state: FSMContext):
    chain = await get_chain(state)
    if len(chain) != 3:
        await callback.message.answer("Сначала соберите F3, F2, F1.")
        await callback.answer()
        return

    code = generate_vba(chain)
    await callback.message.answer(f"Ваш VBA-код:\n\n{code}")
    await callback.answer()


async def main():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Укажи BOT_TOKEN в переменной окружения")

    bot = Bot(token=token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("Bot is running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())