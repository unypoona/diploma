from django.db import models


class Author(models.Model):
    """
    Модель для хранения информации об авторе описаний достопримечательностей.

    Атрибуты:
        name (CharField): Имя автора.
        email (EmailField): Электронная почта автора, уникальное поле.
        created_at (DateTimeField): Дата и время создания записи об авторе.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Description(models.Model):
    """
    Модель для хранения описаний достопримечательностей.

    Атрибуты:
        content (TextField): Текстовое описание.
        author (ForeignKey): Ссылка на автора описания, может быть пустой.
        image_url (URLField): Ссылка на изображение, может быть пустой.
        created_at (DateTimeField): Дата и время создания записи.
    """
    content = models.TextField()
    author = models.ForeignKey(Author, null=True, blank=True, on_delete=models.SET_NULL)
    image_url = models.URLField(max_length=500, null=True, blank=True)  # Ссылка на изображение
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content[:50]


class Place(models.Model):
    """
    Модель для хранения информации о достопримечательностях.

    Атрибуты:
        name (CharField): Название достопримечательности.
        latitude (DecimalField): Широта местоположения.
        longitude (DecimalField): Долгота местоположения.
        created_at (DateTimeField): Дата и время создания записи.
    """
    name = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(models.Model):
    """
    Модель для хранения информации о пользователях системы.

    Атрибуты:
        username (CharField): Имя пользователя, может быть пустым.
        email (EmailField): Электронная почта пользователя, уникальное поле.
        telegram_id (CharField): Telegram ID пользователя, уникальное поле, может быть пустым.
        created_at (DateTimeField): Дата и время создания записи о пользователе.
    """
    username = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    telegram_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username or self.email


class UserQuery(models.Model):
    """
    Модель для хранения информации о запросах пользователей.

    Атрибуты:
        user (ForeignKey): Ссылка на пользователя, сделавшего запрос.
        place (ForeignKey): Ссылка на место, к которому относится запрос, может быть пустой.
        latitude (DecimalField): Широта местоположения пользователя при запросе.
        longitude (DecimalField): Долгота местоположения пользователя при запросе.
        query_time (DateTimeField): Время запроса.
        created_at (DateTimeField): Дата и время создания записи о запросе.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, null=True, blank=True, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    query_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Query by {self.user} at {self.query_time}"


class Subscription(models.Model):
    """
    Модель для хранения информации о подписках пользователей на авторов.

    Атрибуты:
        user (ForeignKey): Ссылка на пользователя.
        author (ForeignKey): Ссылка на автора, на которого подписан пользователь.
        created_at (DateTimeField): Дата и время создания записи о подписке.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} подписан на {self.author}"


class PlaceDescription(models.Model):
    """
    Промежуточная модель для связи мест и их описаний.

    Атрибуты:
        place (ForeignKey): Ссылка на место.
        description (ForeignKey): Ссылка на описание.

    Метаданные:
        unique_together: Связка места и описания должна быть уникальной.
    """
    place = models.ForeignKey(Place, related_name='descriptions', on_delete=models.CASCADE)
    description = models.ForeignKey(Description, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('place', 'description'),)

    def __str__(self):
        return f"{self.place.name} - {self.description.content[:50]}"
