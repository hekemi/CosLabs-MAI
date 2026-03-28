"""
Модуль для получения курсов валют ЦБ РФ.

Данные берутся из официального XML-фида Центрального Банка России
(те же данные, что публикует www.rbc.ru в разделе «Курсы ЦБ РФ»).
"""

import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
import aiohttp

CBR_XML_URL = "https://www.cbr.ru/scripts/XML_daily.asp"


class CurrencyFetchError(Exception):
    """Ошибка при получении данных с сервера ЦБ РФ."""


class Currency:
    """Представляет одну валюту с её курсом к рублю."""

    def __init__(self, char_code: str, name: str, nominal: int, value: float):
        self.char_code = char_code
        self.name = name
        self.nominal = nominal
        self.value = value

    @property
    def rate_per_one(self) -> float:
        """Курс за одну единицу валюты."""
        return self.value / self.nominal

    def __str__(self) -> str:
        return (
            f"<b>{self.char_code}</b> — {self.name}\n"
            f"Курс: {self.value:.4f} руб. за {self.nominal} ед."
        )


async def fetch_currencies(date: Optional[datetime] = None) -> dict[str, Currency]:
    """
    Асинхронно загружает курсы валют с сайта ЦБ РФ.

    :param date: Дата, на которую нужен курс (по умолчанию — сегодня).
    :return: Словарь {CharCode: Currency}.
    :raises CurrencyFetchError: При сетевой ошибке или некорректном ответе сервера.
    """
    params = {}
    if date:
        params["date_req"] = date.strftime("%d/%m/%Y")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                CBR_XML_URL,
                params=params,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                response.raise_for_status()
                content = await response.read()
    except aiohttp.ClientResponseError as exc:
        raise CurrencyFetchError(
            f"Сервер ЦБ РФ вернул ошибку {exc.status}: {exc.message}"
        ) from exc
    except aiohttp.ClientError as exc:
        raise CurrencyFetchError(
            f"Не удалось подключиться к серверу ЦБ РФ: {exc}"
        ) from exc

    try:
        root = ET.fromstring(content)
    except ET.ParseError as exc:
        raise CurrencyFetchError(
            f"Сервер ЦБ РФ вернул некорректный XML: {exc}"
        ) from exc

    currencies: dict[str, Currency] = {}

    for valute in root.findall("Valute"):
        char_code = valute.findtext("CharCode", "").strip()
        name = valute.findtext("Name", "").strip()
        nominal_text = valute.findtext("Nominal", "1").strip()
        value_text = valute.findtext("Value", "0").strip().replace(",", ".")

        try:
            nominal = int(nominal_text)
            value = float(value_text)
        except ValueError:
            continue

        if char_code:
            currencies[char_code] = Currency(char_code, name, nominal, value)

    return currencies
