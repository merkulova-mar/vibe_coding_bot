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
    "иван": ["сервер", "linux", "бэкенд", "backend"],
    "оля": ["frontend", "react", "верстка", "ui", "дизайн"],
    "мария": ["финансы", "отчет", "налоги", "зарплата"],
}

# Маппинг для упоминаний — впишите реальные username через @
MENTIONS = {
    "иван": "@ivan_username",
    "оля": "@olga_username",
    "мария": "@maria_username",
    "ксения": "@ksenia_username",
    "евгения": "@evgenia_username",
    "дмитрий": "@dmitry_username",
    "инесса": "@inessa_username",
    "изабелла": "@izabella_username",
    "канат": "@kanat_username"
}

PHOTOS = {
    "иван": "",  # сюда можно добавить file_id позже
    "оля": "",
    "мария": "",
    "ксения": "AgACAgIAAxkBAAMYaIJCTP_J4j6fWK_hmLZDiyH-vqYAAp_0MRsOLRhI7tpiaRD7stoBAAMCAAN4AAM2BA",
    "евгения": "AgACAgIAAxkBAAMbaIJEvq4Ofk-qeSAb15dFkD1_JUMAAqD0MRsOLRhIjpySg4RAbYABAAMCAAN4AAM2BA",
    "дмитрий": "AgACAgIAAxkBAAMdaIJFJRPLodBKt8ttOklnsjpK4KUAAqH0MRsOLRhIb0u6Yj7h5GYBAAMCAAN4AAM2BA",
    "инесса": "AgACAgIAAxkBAAMfaIJFMZFDMiLJ3ubZJzg7SOUjoTAAAqL0MRsOLRhIkKU_j7KCWjABAAMCAAN4AAM2BA",
    "изабелла": "AgACAgIAAxkBAAMhaIJFQTXIQjp1PnbSYJ8t9fQDM0oAAqP0MRsOLRhI3X5T5vgm_X0BAAMCAAN4AAM2BA",
    "канат": "AgACAgIAAxkBAAMLaIJAY25KLoByqupVgS8mCBra6lMAAhf0MRusUhFIYddKCGwWd80BAAMCAAN4AAM2BA"
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
        "Привет! Задайте мне вопрос — я подскажу, кто из сотрудников может помочь по теме. "
        "Пример: 'Кто решает проблемы с сервером и дизайном?'\n\n"
        "Доступные темы и эксперты:\n"
        + '\n'.join(f"— {p.title()}: {', '.join(KEYWORDS[p])}" for p in KEYWORDS)
    )

@dp.message(lambda message: message.text is not None)
async def find_expert(message: types.Message):
    if not message.text:
        return  # Игнорируем не-текстовые сообщения
    text = message.text.lower()
    words = re.findall(r'\w+', text, re.UNICODE)
    norm_words = [normalize_word(w) for w in words]
    found = set()
    for w in norm_words:
        if w in word_to_person:
            found.add(word_to_person[w])
    if not found:
        await message.answer("Не нашёл подходящего специалиста. Попробуйте переформулировать вопрос.")
    else:
        for person in found:
            caption = f"{person.title()} ({MENTIONS.get(person, person)}) может помочь вам!"
            photo = PHOTOS.get(person)
            if photo:
                await message.answer_photo(photo, caption=caption)
            else:
                await message.answer(caption)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
