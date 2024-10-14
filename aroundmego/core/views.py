from .models import Place, Description, Author, PlaceDescription
from math import radians, cos, sin, asin, sqrt
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
import re
from django.contrib import messages
from .forms import UserRegisterForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from .gpt_utils import generate_description



def haversine(lon1, lat1, lon2, lat2):
    """
    Функция для расчета расстояния между двумя точками по их географическим координатам (долгота и широта)
    с использованием формулы гаверсинуса.

    Args:
        lon1, lat1: Географические координаты первой точки (долгота, широта).
        lon2, lat2: Географические координаты второй точки (долгота, широта).

    Returns:
        Расстояние в километрах между двумя точками.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371
    return c * r


@login_required
def index(request):
    """
    Представление для обработки GET и POST запросов на главной странице.
    Возвращает список достопримечательностей в радиусе 5 км от указанных координат.

    Args:
        request: HTTP запрос.

    Returns:
        Если POST-запрос, возвращает список достопримечательностей в формате JSON.
        Если GET-запрос, отображает главную страницу с авторами.
    """
    if request.method == 'POST' and request.POST.get('action') == 'get_pois':
        latitude = float(request.POST.get('latitude'))
        longitude = float(request.POST.get('longitude'))

        poi_list = []
        places = Place.objects.all()
        for place in places:
            distance = haversine(longitude, latitude, place.longitude, place.latitude)
            if distance <= 5:
                descriptions = place.descriptions.all()
                if descriptions.exists():
                    first_description = descriptions.first().description
                    address = first_description.content if first_description else 'Адрес не указан'
                else:
                    address = 'Адрес не указан'

                poi_list.append({
                    "name": place.name,
                    "address": address,
                    "description": address,
                    "image_url": first_description.image_url if first_description else '',
                    "longitude": place.longitude,
                    "latitude": place.latitude
                })

        return JsonResponse({'pois': poi_list})

    authors = Author.objects.all()
    return render(request, 'core/index.html', {'authors': authors})


def format_description(description):
    """
    Функция для форматирования текста описания в HTML формат с добавлением параграфов и нумерованных списков.

    Args:
        description: Строка с текстом описания.

    Returns:
        Строка с отформатированным HTML текстом.
    """
    paragraphs = re.split(r'(?<=[.!?])\s+|\n', description)
    formatted_paragraphs = [f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()]
    formatted_text = " ".join(formatted_paragraphs)

    formatted_text = re.sub(r'(\d+\.\s)', r'</li><li>\1', formatted_text)
    formatted_text = formatted_text.replace('</li><li>', '<ul><li>', 1)
    formatted_text += '</li></ul>' if '<li>' in formatted_text else ''

    return formatted_text


from django.http import JsonResponse
from .models import Place, Author, PlaceDescription


def get_poi_description(request):
    """
    Представление для получения описания выбранной достопримечательности,
    с возможностью выбора описания от конкретного автора.
    Если автор с id=1, используется описание из функции get_gpt_description.
    """
    if request.method == 'POST' and request.POST.get('action') == 'get_poi_description':
        place_name = request.POST.get('place_name')
        selected_author_id = request.POST.get('author_id')

        if not place_name:
            return JsonResponse({'error': 'Название достопримечательности не указано'}, status=400)

        # Найдем достопримечательность
        place = Place.objects.filter(name=place_name).first()
        if not place:
            return JsonResponse({'error': 'Достопримечательность не найдена'}, status=404)

        description_object = None

        # Если автор выбран и его id = 1, то используем функцию из gpt_utils.py
        if selected_author_id and int(selected_author_id) == 1:
            # Получаем описание с помощью функции get_gpt_description
            gpt_description = generate_description(place_name)

            formatted_description = format_description(gpt_description)
            image_url = "https://www.pnp.ru/upload/entities/2022/06/16/19/article/detailPicture/e1/06/6c/ca/b2f318ee768375c2a404e41bad2da835.jpg"
            author_name = "GPT-Автор"

            return JsonResponse(
                {'description': formatted_description, 'image_url': image_url, 'author_name': author_name},
                status=200
            )

        # Если автор не id=1 или автор не выбран, используем старую логику
        if selected_author_id:
            try:
                author = Author.objects.get(id=selected_author_id)
                description_object = PlaceDescription.objects.filter(place=place, description__author=author).first()
            except Author.DoesNotExist:
                return JsonResponse({'error': 'Автор не найден'}, status=404)

        # Если описание по автору не найдено, возьмем первое доступное описание
        if not description_object:
            description_object = place.descriptions.first()

        if description_object and description_object.description:
            description = description_object.description.content
            author_name = description_object.description.author.name if description_object.description.author else "Неизвестен"
            image_url = description_object.description.image_url or "https://cdn.tripster.ru/thumbs2/4073fe44-549d-11ed-9d0b-8671fed585d2.1220x600.jpeg"
        else:
            description = "Описание не найдено."
            author_name = "Неизвестен"
            image_url = "https://cdn.tripster.ru/thumbs2/4073fe44-549d-11ed-9d0b-8671fed585d2.1220x600.jpeg"

        formatted_description = format_description(description)
        return JsonResponse(
            {'description': formatted_description, 'image_url': image_url, 'author_name': author_name},
            status=200
        )

    return JsonResponse({'error': 'Неверный запрос'}, status=400)


def register(request):
    """
    Представление для регистрации нового пользователя.

    Args:
        request: HTTP запрос.

    Returns:
        Если POST запрос с корректными данными, регистрирует пользователя и перенаправляет на главную страницу.
        Если GET запрос, отображает форму регистрации.
    """
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')  # Убедитесь, что происходит редирект
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    """
    Представление для входа пользователя в систему.

    Args:
        request: HTTP запрос.

    Returns:
        Если POST запрос с корректными данными, аутентифицирует пользователя и перенаправляет на главную страницу.
        Если GET запрос или некорректные данные, отображает форму входа.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('index')
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """
    Представление для выхода пользователя из системы.

    Args:
        request: HTTP запрос.

    Returns:
        Перенаправляет пользователя на главную страницу после выхода из системы.
    """
    logout(request)
    return redirect('index')


@login_required
def place_descriptions(request, place_id):
    """
    Представление для отображения описаний конкретной достопримечательности.

    Args:
        request: HTTP запрос.
        place_id: Идентификатор достопримечательности.

    Returns:
        Шаблон с информацией об описании достопримечательности.
    """
    place = get_object_or_404(Place, id=place_id)
    author = getattr(request.user, 'author', None)

    if author:
        description = Description.objects.filter(place=place, author=author).first()
        if not description:
            description = Description.objects.filter(place=place, author__isnull=True).first()
    else:
        description = Description.objects.filter(place=place, author__isnull=True).first()

    return render(request, 'core/place_descriptions.html', {'place': place, 'description': description})
