import re
from aiogram import Bot, Dispatcher, types
import pymorphy2
import asyncio
import os
from aiogram.filters import Command, Filter
import random

# Получаем токен из переменной окружения
API_TOKEN = os.getenv("API_TOKEN")

# Словарь сотрудников и их ключевых слов (будут нормализованы)
KEYWORDS = {
    "ксения": ["flow", "английский", "upskill", "сквозная английского", "funnel by channel", "маркетинг английский","эксперимент"],
    "евгения": ["открутки", "reskill маркетинг"],
    "канат": ["английский", "тьюторы английский", "финансы английский"],
    "инесса": ["b2b"],
    "изабелла": ["crm", "срм", "рассылки"],
    "дмитрий": ["amo", "кураторская", "отдел продаж", "квалифицированный лид", "заявка"],
    "привлечение": [
        "маркетинговая аналитика", "канал привлечения", "трафик", "конверсия", "фритрек",
        "конверсия в регистрацию", "рекламные кампании", "cpa", "cpc", "cpm", "roi маркетинга",
        "атрибуция", "первый клик", "последний клик", "cac", "эффективность креативов",
        "воронка привлечения", "attribution","эксперимент", "атрибуция", "аквизитион", "acquisition", "acqusition", "aquisation", "acquisiton", "acqisition", "acquisitionn", "acquisishon", "acqusishon", "acquizition", "acquesition", "acquisicion", "acquisitin", "acquisishan", "acquisation", "acquisitian","аквизишн", "аквузишн", "акуизейшн", "аквизитон", "аквизишн", "аквизишнн", "аквизишон", "аквузишон", "аквизишн", "аквезишн", "аквизишн", "аквизитин", "аквизишан", "аквизейшн", "аквизитиан", "эксперимент"
    ],
    "пользовательский опыт": ["трудоустройство", "доходимость", "спринты", "зарплаты экспертам"],
    "bi и моделирования": [
        "bcr", "bookings", "revenue", "cash in", "cash out", "финансы", "выручка", "букингс",
        "доступы даталенс", "доступы datalens", "доступы к отчету", "новый отчет", "pr",
        "выпускники", "карьерный центр", "прогнозирование", "бюджетирование", "рефоркаст",
        "программа акселерации", "расхождения"
    ], 
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
    "канат": "AgACAgIAAxkBAAMLaIJAY25KLoByqupVgS8mCBra6lMAAhf0MRusUhFIYddKCGwWd80BAAMCAAN4AAM2BA",
    "привлечение": [
        "AgACAgIAAxkBAAOHaIN5W1jgZxHllhg0TL4ELUpQLFEAAlv0MRsqBSBIw6MyTWZ9b2IBAAMCAAN5AAM2BA",
        "AgACAgIAAxkBAAOHaIN5W1jgZxHllhg0TL4ELUpQLFEAAlv0MRsqBSBIw6MyTWZ9b2IBAAMCAAN5AAM2BA"
    ],
    "bi и моделирования": [
        "AgACAgIAAxkBAAOSaIN9cuZvzub40VNGCY5qAoI1OB4AAnT0MRsqBSBI1197h6zuWf0BAAMCAAN5AAM2BA",
        "AgACAgIAAxkBAAOzaIOFvTyqOmFYflQGmkhlAnLhdU0AArL0MRsqBSBIZirkBEM7JVoBAAMCAAN5AAM2BA"
    ],
    "пользовательский опыт": [
        "AgACAgIAAxkBAAPoaIOSmklzvzEt7-LMASrk1lgPr14AAkP3MRsuziBIzGuK_KK4kCYBAAMCAAN5AAM2BA"
    ]
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

def normalize_phrase(phrase):
    return ' '.join([normalize_word(w) for w in re.findall(r'\w+', phrase.lower(), re.UNICODE)])

NORMALIZED_KEYWORDS = {
    person: [normalize_phrase(phrase) for phrase in phrases]
    for person, phrases in KEYWORDS.items()
}

# Подготовим обратный индекс: нормальная форма слова -> сотрудник
word_to_person = {}
for person, words in KEYWORDS.items():
    for w in words:
        norm = normalize_word(w.lower())
        word_to_person[norm] = person

# Список неаналитических ключевых слов
NOT_ANALYTICS_KEYWORDS = [
    "разметка страниц", "интеграция", "я-форма", "отпуск", "командировка", "больничный", "канцелярия", "ремонт", "доставка", "обед",
    "чай", "кофе", "питание", "пропуск", "безопасность", "уборка", "мебель", "оргтехника", "it поддержка", "транспорт",
    "переезд", "корпоратив", "праздник", "подарок", "мероприятие", "страховка", "медосмотр", "документы", "печать", "подпись",
    "юрист", "аренда", "интернет", "связь", "курьер", "логистика", "склад", "инвентаризация", "закупка", "снабжение",
    "договор", "счет", "оплата", "касса", "банк", "карта", "парковка", "охрана", "уборщица", "сантехник", "разметить", "разметить"
]

NOT_ANALYTICS_PHOTOS = [
    "AgACAgIAAxkBAAOUaIN-wN4lEqiL5gk-5e2Fl6bPgiAAAnz0MRsqBSBIIg1UJOGNevwBAAMCAAN4AAM2BA",
    "AgACAgIAAxkBAAOWaIN_MLQvI5Ca0JCGaAQuBOjqch8AAmL5MRsLkhlI4MqVwEeNR5wBAAMCAAN4AAM2BA",
    "AgACAgIAAxkBAAOYaIN_SE1nvaIEV7Ke8h2MfzXyqckAAoP0MRsqBSBIFbDUaWb6LakBAAMCAAN4AAM2BA",
    "AgACAgIAAxkBAAOaaIN_UhTzf140W72Pab4AAQHSoY3IAAKE9DEbKgUgSDvl_RWOztaPAQADAgADbQADNgQ",
    "AgACAgIAAxkBAAOcaIN_okaFw9uL-61ShaIuR2zs3wsAAof0MRsqBSBIC88LiSU0LMcBAAMCAAN4AAM2BA"
]

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command(commands=["start", "help"]))
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Задай мне вопрос — я подскажу, кто из сотрудников может помочь по теме. "
        "Пример: 'Кто может помочь с вопросом по продажам b2b?'"
    )

@dp.message(lambda message: message.text is not None)
async def find_expert(message: types.Message):
    if not message.text:
        return  # Игнорируем не-текстовые сообщения
    text = message.text.lower()
    words = re.findall(r'\w+', text, re.UNICODE)
    norm_words = [normalize_word(w) for w in words]
    norm_text = ' '.join(norm_words)

    # Проверка на неаналитические ключевые слова
    for phrase in NOT_ANALYTICS_KEYWORDS:
        phrase_words = [normalize_word(w) for w in re.findall(r'\w+', phrase.lower(), re.UNICODE)]
        if all(w in norm_words for w in phrase_words):
            photo_id = random.choice(NOT_ANALYTICS_PHOTOS)
            await message.answer_photo(photo_id, caption="Наши аналитики великолепны, но не всемогущи. Возможно вам поможет разработка")
            return

    analytic_depts = ["привлечение", "пользовательский опыт", "bi и моделирования"]
    has_english = "английский" in norm_words
    attraction_phrases = NORMALIZED_KEYWORDS.get("привлечение", [])
    has_attraction = any(phrase in norm_text for phrase in attraction_phrases)

    if has_attraction and has_english:
        person = "ксения"
    elif has_english:
        person = "канат"
    else:
        for dept in analytic_depts:
            dept_phrases = NORMALIZED_KEYWORDS.get(dept, [])
            if any(phrase in norm_text for phrase in dept_phrases):
                photo = PHOTOS.get(dept)
                text = f"Этот вопрос относится к отделу аналитики — {dept.title()}\nЗадай свой вопрос в канале \nhttps://mattermost.practicum.yandex/practicum/channels/analytics_communications"
                if photo:
                    if dept in ["привлечение", "bi и моделирования","пользовательский опыт"] and isinstance(photo, list):
                        photo = random.choice(photo)
                    await message.answer_photo(photo, caption=text)
                else:
                    await message.answer(text)
                return
        person = None
        for person_key, norm_phrases in NORMALIZED_KEYWORDS.items():
            if person_key in analytic_depts:
                continue
            if any(phrase in norm_text for phrase in norm_phrases):
                person = person_key
                break
    if not person:
        await message.answer("Я не нашёл подходящего специалиста. Попробуй переформулировать вопрос или спроси в канале https://mattermost.practicum.yandex/practicum/channels/analytics_communications.")
        await message.answer_photo("AgACAgIAAxkBAAOeaIOAGDKIjkAgZoweLFXPLQKWCtgAAnj5MRvKQiBI6iilAUx2Rp4BAAMCAANtAAM2BA")
    else:
        link = links.get(person)
        caption = f"Твой аналитик {person.title()} ({MENTIONS.get(person, person)})! Мы всегда готовы помочь тебе!"
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
