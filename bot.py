import re
from aiogram import Bot, Dispatcher, types
import pymorphy2
import asyncio

# ВСТАВЬТЕ сюда свой токен, выданный BotFather
API_TOKEN = "ВАШ_ТОКЕН_ТУТ"

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
    "мария": "@maria_username"
}

morph = pymorphy2.MorphAnalyzer()

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

@dp.message(commands=["start", "help"])
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет! Задайте мне вопрос — я подскажу, кто из сотрудников может помочь по теме. "
        "Пример: 'Кто решает проблемы с сервером и дизайном?'\n\n"
        "Доступные темы и эксперты:\n"
        + '\n'.join(f"— {p.title()}: {', '.join(KEYWORDS[p])}" for p in KEYWORDS)
    )

@dp.message()
async def find_expert(message: types.Message):
    # Регулярка ловит слова, игнорируя знаки пунктуации
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
        response = "Вот, кто может помочь:\n"
        for person in found:
            response += f"- {person.title()} ({MENTIONS.get(person, person)})\n"
        await message.answer(response)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
