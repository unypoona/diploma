import openai
import logging
from openai import OpenAI
from aroundmego import settings


client = OpenAI(api_key=settings.OPEN_AI_TOKEN)
# Настройка логирования для обработки ошибок
logger = logging.getLogger(__name__)

# Функция для генерации описания через GPT
def generate_description(place_name):
    print('gpt generate')
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "you are a guide in St. Petersburg, your task is to give a tour and tell interesting facts about the place you are asked about. Answer in Russian. The text is 2-3 paragraphs long, no other text formatting is necessary."},
                {"role": "user",
                 "content": f"{place_name}"}
            ]
        )
        result = completion.choices[0].message.content.lower()
        print(result)
        return result
    except Exception as e:
        logger.error(f"Ошибка при генерации описания через GPT: {e}")
        return "Описание недоступно."
