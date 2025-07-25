import re
from aiogram import Bot, Dispatcher, types
import pymorphy2
import asyncio
import os
from aiogram.filters import Command, Filter

# Получаем токен из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Словарь сотрудников и их ключевых слов (будут нормализованы)
KEYWORDS = {
    "ксения": ["flow", "английский", "upskill", "сквозная английского", "funnel by channel", "маркетинг английский"],
    "евгения": ["открутки", "reskill маркетинг"],
    "канат": ["английский", "тьюторы английский", "финансы английский"],
    "инесса": ["b2b"],
    "изабелла": ["crm", "срм", "рассылки"],
    "дмитрий": ["amo", "кураторская", "отдел продаж", "квалифицированный лид"],
    "привлечение": [
        "маркетинговая аналитика", "каналы привлечения", "трафик", "конверсия", "фритрек",
        "конверсия в регистрацию", "рекламные кампании", "cpa", "cpc", "cpm", "roi маркетинга",
        "атрибуция", "первый клик", "последний клик", "cac", "эффективность креативов",
        "воронка привлечения", "attribution", "атрибуция", "аквизитион"
    ],
    "пользовательский опыт": ["трудоустройство", "доходимость", "спринты"],
    "bi и моделирования": [
        "bcr", "bookings", "revenue", "cash in", "cash out", "финансы", "выручка", "букингс",
        "доступы даталенс", "доступы datalens", "доступы к отчету", "новый отчет", "pr",
        "выпускники", "карьерный центр", "прогнозирование", "бюджетирование", "рефоркаст",
        "программа акселерации"
    ]
}

# Маппинг для упоминаний — впишите реальные username через @
MENTIONS = {
    "ксения": "@kseniiathe",
    "евгения": "@evenolt",
    "канат": "@Kanat_Bizh",
    "инесса": "@weareinthistogether0",
    "изабелла": "@bellochka_bellochka",
    "дмитрий": "@dmikhaltsovd"
}

PHOTOS = {
    "ксения": "AgACAgIAAxkBAAMYaIJCTP_J4j6fWK_hmLZDiyH-vqYAAp_0MRsOLRhI7tpiaRD7stoBAAMCAAN4AAM2BA",
    "евгения": "AgACAgIAAxkBAAMbaIJEvq4Ofk-qeSAb15dFkD1_JUMAAqD0MRsOLRhIjpySg4RAbYABAAMCAAN4AAM2BA",
    "дмитрий": "AgACAgIAAxkBAAMdaIJFJRPLodBKt8ttOklnsjpK4KUAAqH0MRsOLRhIb0u6Yj7h5GYBAAMCAAN4AAM2BA",
    "инесса": "AgACAgIAAxkBAAMfaIJFMZFDMiLJ3ubZJzg7SOUjoTAAAqL0MRsOLRhIkKU_j7KCWjABAAMCAAN4AAM2BA",
    "изабелла": "AgACAgIAAxkBAAMhaIJFQTXIQjp1PnbSYJ8t9fQDM0oAAqP0MRsOLRhI3X5T5vgm_X0BAAMCAAN4AAM2BA",
    "канат": "AgACAgIAAxkBAAMLaIJAY25KLoByqupVgS8mCBra6lMAAhf0MRusUhFIYddKCGwWd80BAAMCAAN4AAM2BA"
}

links = {
    "ксения": "https://staff.yandex-team.ru/dksenianalyst",
    "евгения": "https://staff.yandex-team.ru/evgeniyaolt",
    "канат": "https://staff.yandex-team.ru/kanat-bizh",
    "инесса": "https://staff.yandex-team.ru/krasikovaia",
    "изабелла": "https://staff.yandex-team.ru/zatikyan-ia",
    "дмитрий": "https://staff.yandex-team.ru/dmikhaltsovd"
}

morph = pymorphy2.MorphAnalyzer(lang='ru')

def normalize_word(word):
    return morph.parse(word)[0].normal_form

# Подготовим обратный индекс: нормальная форма слова -> сотрудник
word_to_person = {}
for person, words in KEYWORDS.items():
    for w in words:
        norm = normalize_word(w.lower())
        word_to_person[norm] = person

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Задай мне вопрос — я подскажу, кто из сотрудников может помочь по теме. "
        "\n Пример: 'Кто может помочь с вопросом по продажам b2b?'"
    )

@dp.message(lambda message: message.text is not None)
async def find_expert(message: types.Message):
    if not message.text:
        return  # Игнорируем не-текстовые сообщения
    text = message.text.lower()
    words = re.findall(r'\w+', text, re.UNICODE)
    norm_words = [normalize_word(w) for w in words]

    # Ключевые сотрудники-отделы
    analytic_depts = ["привлечение", "пользовательский опыт", "bi и моделирования"]
    # Проверка на "английский"
    has_english = "английский" in norm_words
    # Ключевые слова для "привлечение"
    attraction_keywords = set(normalize_word(w.lower()) for w in KEYWORDS.get("привлечение", []))
    has_attraction = any(w in norm_words for w in attraction_keywords)

    # 1. Если "привлечение" и "английский" — Ксения
    if has_attraction and has_english:
        person = "ксения"
    # 2. Если не "привлечение", но есть "английский" — Канат
    elif has_english:
        person = "канат"
    else:
        # 3. Проверяем, относится ли вопрос к аналитическим отделам
        for dept in analytic_depts:
            dept_keywords = set(normalize_word(w.lower()) for w in KEYWORDS.get(dept, []))
            if any(w in norm_words for w in dept_keywords):
                await message.answer(f"Этот вопрос относится к отделу аналитики — {dept.title()}\nЗадайте свой вопрос в канале https://mattermost.practicum.yandex/practicum/channels/analytics_communications")
                return
        # 4. Обычный поиск по ключевым словам (только первого найденного сотрудника)
        person = None
        for w in norm_words:
            if w in word_to_person:
                person = word_to_person[w]
                break
    if not person:
        await message.answer("Не нашёл подходящего специалиста. Попробуй переформулировать вопрос или спроси в канале https://mattermost.practicum.yandex/practicum/channels/analytics_communications.")
    else:
        link = links.get(person)
        caption = f"{person.title()} ({MENTIONS.get(person, person)}) может помочь вам!"
        if link:
            caption += f"\nПрофиль: {link}"
        photo = PHOTOS.get(person)
        if photo:
            await message.answer_photo(photo, caption=caption)
        else:
            await message.answer(caption)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
