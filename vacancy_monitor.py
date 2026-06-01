import asyncio
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient

# ===== SETTINGS =====

# Your API keys
API_ID = 0                    # YOUR_API_ID
API_HASH = "your_api_hash"    # YOUR_API_HASH
PHONE = "+1234567890"         # YOUR_PHONE_NUMBER

# Channels for monitoring
CHANNELS = [
    "your_channel_1",
    "your_channel_2",
    # Add your channels
]

# Search keywords
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

# Filter words for remote
# REMOTE_KEYWORDS = ['remote', 'удалённо', 'удаленно', 'удалёнка', 'удаленка']

# How many hours back should search (24 = last day)
HOURS_BACK = 24

# ===== END OF SETTINGS =====


async def main():
    # Connecting to Telegram
    client = TelegramClient('vacancy_session', API_ID, API_HASH)
    await client.start()
    print('✅ Connecting to Telegram successfully\n')

    # The time from which we are searching
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

                # Check if the message contains at least one keyword
                matched_keywords = [kw for kw in KEYWORDS if kw in text_lower]

                if matched_keywords:
                    found_count += 1
                    result = {
                        'channel': channel_username,
                        'date': message.date.strftime('%Y-%m-%d %H:%M'),
                        'keywords': ', '.join(matched_keywords),
                        'text': message.text[:500],  # first 500 characters
                        'link': f'https://t.me/{channel_username}/{message.id}'
                    }
                    results.append(result)

                    # Forward to Saved Messages
                    await client.forward_messages('me', message)

        except Exception as e:
            print(f'   ⚠️ Error in @{channel_username}: {e}')

    # Final report
    print(f'\n{"="*50}')
    print(f'🔍 Job openings found: {found_count}')
    print(f'📅 Period: last {HOURS_BACK} hours')
    print(f'{"="*50}\n')

    for i, r in enumerate(results, 1):
        print(f'--- Vacancy {i} ---')
        print(f'Channel: @{r["channel"]}')
        print(f'Date: {r["date"]}')
        print(f'Coincidences: {r["keywords"]}')
        print(f'Link: {r["link"]}')
        print(f'Text: {r["text"][:200]}...')
        print()

    # Save the results to a file
    with open('vacancies_report.txt', 'w', encoding='utf-8') as f:
        f.write(f'Vacancy Report — {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
        f.write(f'Found: {found_count}\n')
        f.write(f'Period: last {HOURS_BACK} hours\n\n')

        for i, r in enumerate(results, 1):
            f.write(f'--- Vacancy {i} ---\n')
            f.write(f'Channel: @{r["channel"]}\n')
            f.write(f'Date: {r["date"]}\n')
            f.write(f'Coincidences: {r["keywords"]}\n')
            f.write(f'Link: {r["link"]}\n')
            f.write(f'Text:\n{r["text"]}\n\n')

    print(f'💾 The report is saved in vacancies_report.txt')

    await client.disconnect()


# Launch
asyncio.run(main())
