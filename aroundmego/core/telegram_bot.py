import os
import django
import telebot
import logging
from telebot import types
from django.conf import settings
from math import radians, cos, sin, asin, sqrt
from .gpt_utils import generate_description

# Устанавливаем Django настройки для доступа к моделям и конфигурации
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aroundmego.settings')
django.setup()

# Импортируем модели из проекта
from core.models import Place, Description, PlaceDescription

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
TOKEN = settings.TELEGRAM_TOKEN
bot = telebot.TeleBot(TOKEN)

# Глобальные переменные для хранения состояния и геолокации
latitude = None
longitude = None
current_description_message_id = None  # ID сообщения с описанием достопримечательности
current_image_message_id = None  # ID сообщения с картинкой достопримечательности
last_poi_index = None  # Индекс последней выбранной достопримечательности

def haversine(lon1, lat1, lon2, lat2):
    """
    Рассчитывает расстояние между двумя точками по их географическим координатам (широта и долгота).

    Args:
        lon1, lat1 (float): Долгота и широта первой точки.
        lon2, lat2 (float): Долгота и широта второй точки.

    Returns:
        float: Расстояние между двумя точками в километрах.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Радиус Земли в километрах
    return c * r


def get_poi(latitude, longitude, radius_km=5):
    """
    Получает список достопримечательностей в заданном радиусе с проверкой наличия описаний.

    Args:
        latitude (float): Широта текущего местоположения пользователя.
        longitude (float): Долгота текущего местоположения пользователя.
        radius_km (int, optional): Радиус поиска достопримечательностей в километрах. По умолчанию 5 км.

    Returns:
        list: Список достопримечательностей с описаниями и изображениями.
    """
    places = Place.objects.all()
    poi_list = []

    for place in places:
        distance = haversine(longitude, latitude, place.longitude, place.latitude)
        if distance <= radius_km:
            place_description_obj = place.descriptions.first()
            if place_description_obj:
                description_obj = place_description_obj.description
                description_content = description_obj.content if description_obj else ''
                image_url = description_obj.image_url if description_obj and description_obj.image_url else ''
            else:
                description_content = ''
                image_url = ''

            poi_list.append({
                "name": place.name,
                "address": description_content or 'Адрес не указан',
                "description": description_content,
                "image_url": image_url,
                "longitude": place.longitude,
                "latitude": place.latitude
            })

    return poi_list


def default_keyboard():
    """
    Создает клавиатуру с кнопкой для отправки геолокации и кнопкой "Настройки".

    Returns:
        types.ReplyKeyboardMarkup: Клавиатура с двумя кнопками.
    """
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    location_button = types.KeyboardButton("Отправить свою геолокацию", request_location=True)
    settings_button = types.KeyboardButton("Настройки")
    markup.add(location_button, settings_button)
    return markup


@bot.message_handler(func=lambda message: True)
def send_default(message):
    """
    Обработчик всех входящих сообщений. Отправляет клавиатуру по умолчанию с запросом геолокации.

    Args:
        message (telebot.types.Message): Входящее сообщение от пользователя.
    """
    bot.send_message(
        message.chat.id,
        "Нажми на кнопку ниже, чтобы отправить свою геолокацию.",
        reply_markup=default_keyboard()
    )


@bot.message_handler(content_types=['location'])
def handle_location(message):
    """
    Обработчик сообщений с геолокацией пользователя.

    Args:
        message (telebot.types.Message): Входящее сообщение с геолокацией.
    """
    global latitude, longitude

    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        bot.send_message(message.chat.id, f"Спасибо! Ваша геолокация: широта {latitude}, долгота {longitude}")

        poi_list = get_poi(latitude, longitude, radius_km=5)
        if poi_list:
            markup = create_poi_keyboard(poi_list)
            bot.send_message(message.chat.id, "Выберите достопримечательность из списка:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Не удалось найти достопримечательности поблизости.")


def create_poi_keyboard(poi_list):
    """
    Создает инлайн-клавиатуру с доступными достопримечательностями.

    Args:
        poi_list (list): Список достопримечательностей.

    Returns:
        types.InlineKeyboardMarkup: Инлайн-клавиатура с кнопками для каждой достопримечательности.
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, poi in enumerate(poi_list):
        button = types.InlineKeyboardButton(
            text=f"{poi['name']}, адрес: {poi['address']}",
            callback_data=f"poi_{i}"
        )
        markup.add(button)
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('poi_'))
def callback_poi(call):
    """
    Обработчик кликов по инлайн-кнопкам с достопримечательностями.

    Args:
        call (telebot.types.CallbackQuery): Входящий запрос с выбором достопримечательности.
    """
    global current_description_message_id, current_image_message_id, last_poi_index

    index = int(call.data.split('_')[1])

    if last_poi_index == index:
        if current_description_message_id:
            bot.delete_message(call.message.chat.id, current_description_message_id)
            current_description_message_id = None

        if current_image_message_id:
            bot.delete_message(call.message.chat.id, current_image_message_id)
            current_image_message_id = None

        last_poi_index = None
        bot.answer_callback_query(call.id)
        return

    poi_list = get_poi(latitude, longitude, radius_km=5)
    selected_poi = poi_list[index]
    place_name = selected_poi['name']

    place = Place.objects.get(name=place_name)

    place_description_obj = place.descriptions.first()
    if place_description_obj and place_description_obj.description:
        description = place_description_obj.description.content
    else:
        description = generate_description(place.name)

        if not place_description_obj:
            new_description = Description(content=description)
            new_description.save()
            place_description_obj = PlaceDescription(place=place, description=new_description)
            place_description_obj.save()

    if current_description_message_id:
        bot.delete_message(call.message.chat.id, current_description_message_id)
        current_description_message_id = None

    if current_image_message_id:
        bot.delete_message(call.message.chat.id, current_image_message_id)
        current_image_message_id = None

    description_text = f"{selected_poi['name']},\n{selected_poi['description']}"

    image_url = selected_poi['image_url'] if selected_poi['image_url'] else "https://media.istockphoto.com/id/1022815966/ru/%D1%84%D0%BE%D1%82%D0%BE/%D1%81%D0%B0%D0%BD%D0%BA%D1%82-%D0%BF%D0%B5%D1%82%D0%B5%D1%80%D0%B1%D1%83%D1%80%D0%B3-%D1%85%D1%80%D0%B0%D0%BC-%D1%81%D0%BF%D0%B0%D1%81%D0%B8%D1%82%D0%B5%D0%BB%D1%8F-%D0%BD%D0%B0-%D0%BF%D1%80%D0%BE%D0%BB%D0%B8%D1%82%D0%BE%D0%B9-%D0%BA%D1%80%D0%BE%D0%B2%D0%B8-%D1%80%D0%BE%D1%81%D1%81%D0%B8%D1%8F.jpg?s=612x612&w=0&k=20&c=xffe9fgyuIxzNauVOtYZD0tk2wQ-J-HlYN7WTj10O-Y="

    try:
        if image_url:
            sent_image_message = bot.send_photo(call.message.chat.id, image_url)
            current_image_message_id = sent_image_message.message_id

        sent_message = bot.send_message(call.message.chat.id, description_text)
        current_description_message_id = sent_message.message_id

    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения: {e}")

    last_poi_index = index
    bot.answer_callback_query(call.id)


def start_bot():
    """
    Запускает бота в режиме постоянного опроса сообщений.
    """
    bot.polling(none_stop=True)


if __name__ == "__main__":
    logger.info('Запуск бота...')
    start_bot()
