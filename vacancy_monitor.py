import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient

# ===== НАСТРОЙКИ =====

# Ваши API-ключи
API_ID = 0                    # YOUR_API_ID (число)
API_HASH = "your_api_hash"    # YOUR_API_HASH
PHONE = "+1234567890"         # YOUR_PHONE_NUMBER

# Каналы для мониторинга
CHANNELS = [
    "your_channel_1",
    "your_channel_2",
    # Добавьте свои каналы
]

# Ключевые слова для поиска
KEYWORDS = [
    # Data Analyst
    'data analyst', 'дата аналитик', 'аналитик данных',
    'junior analyst', 'младший аналитик',
    # Marketing Analyst
    'marketing analyst', 'маркетинговый аналитик', 'маркетолог-аналитик',
    'marketing data analyst',
    # Product Analyst
    'product analyst', 'продуктовый аналитик',
    'product data analyst',
    # BI
    'bi analyst', 'bi-аналитик', 'bi аналитик',
    # Web
    'web analyst', 'веб-аналитик', 'веб аналитик',
    # Общие
    'sql analyst', 'crm analyst', 'python analyst'
]

# Слова-фильтры для remote 
# REMOTE_KEYWORDS = ['remote', 'удалённо', 'удаленно', 'удалёнка', 'удаленка']

# За сколько часов назад искать (24 = последние сутки)
HOURS_BACK = 24

# ===== КОНЕЦ НАСТРОЕК =====


async def main():
    # Подключение к Telegram
    client = TelegramClient('vacancy_session', API_ID, API_HASH)
    await client.start()
    print('✅ Подключение к Telegram успешно\n')

    # Время, начиная с которого ищем
    since = datetime.now(timezone.utc) - timedelta(hours=HOURS_BACK)

    found_count = 0
    results = []

    for channel_username in CHANNELS:
        try:
            channel = await client.get_entity(channel_username)
            print(f'📡 Сканирую: @{channel_username}')

            async for message in client.iter_messages(channel, offset_date=since, reverse=True):
                if message.text is None:
                    continue

                text_lower = message.text.lower()

                # Проверяем, содержит ли сообщение хотя бы одно ключевое слово
                matched_keywords = [kw for kw in KEYWORDS if kw in text_lower]

                if matched_keywords:
                    found_count += 1
                    result = {
                        'channel': channel_username,
                        'date': message.date.strftime('%Y-%m-%d %H:%M'),
                        'keywords': ', '.join(matched_keywords),
                        'text': message.text[:500],  # первые 500 символов
                        'link': f'https://t.me/{channel_username}/{message.id}'
                    }
                    results.append(result)

                    # Пересылаем в Saved Messages (Избранное)
                    await client.forward_messages('me', message)

        except Exception as e:
            print(f'   ⚠️ Ошибка в @{channel_username}: {e}')

    # Итоговый отчёт
    print(f'\n{"="*50}')
    print(f'🔍 Найдено вакансий: {found_count}')
    print(f'📅 Период: последние {HOURS_BACK} часов')
    print(f'{"="*50}\n')

    for i, r in enumerate(results, 1):
        print(f'--- Вакансия {i} ---')
        print(f'Канал: @{r["channel"]}')
        print(f'Дата: {r["date"]}')
        print(f'Совпадения: {r["keywords"]}')
        print(f'Ссылка: {r["link"]}')
        print(f'Текст: {r["text"][:200]}...')
        print()

    # Сохраняем результаты в файл
    with open('vacancies_report.txt', 'w', encoding='utf-8') as f:
        f.write(f'Отчёт по вакансиям — {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
        f.write(f'Найдено: {found_count}\n')
        f.write(f'Период: последние {HOURS_BACK} часов\n\n')

        for i, r in enumerate(results, 1):
            f.write(f'--- Вакансия {i} ---\n')
            f.write(f'Канал: @{r["channel"]}\n')
            f.write(f'Дата: {r["date"]}\n')
            f.write(f'Совпадения: {r["keywords"]}\n')
            f.write(f'Ссылка: {r["link"]}\n')
            f.write(f'Текст:\n{r["text"]}\n\n')

    print(f'💾 Отчёт сохранён в vacancies_report.txt')

    await client.disconnect()


# Запуск
asyncio.run(main())