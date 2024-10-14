import os
import django

# Устанавливаем настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aroundmego.settings')
django.setup()

# Импортируем модели
from core.models import Place, Description  # Используем ваше приложение core

# Создаем описания для новых достопримечательностей
descriptions_unique = [
    Description(content="Египетский зал в Эрмитаже — содержит коллекцию древнеегипетских артефактов, включая статуи богов и мумии."),
    Description(content="Золотой павлин в Эрмитаже — уникальные часы XVIII века, являющиеся шедевром механического искусства."),
    Description(content="Музей Фаберже — частный музей с крупнейшей коллекцией ювелирных изделий Карла Фаберже."),
    Description(content="Юсуповский дворец — знаменит своим богатым убранством и местом убийства Григория Распутина."),
    Description(content="Гранд Макет Россия — музей миниатюр, где представлены самые значимые города и объекты России."),
    Description(content="Доходный дом трёх Бенуа — один из самых крупных доходных домов в Петербурге, построенный в 1912 году."),
    Description(content="Часовня Ксении Блаженной — место паломничества, где исполняются желания, написанные на записках."),
    Description(content="Двор с замком на Канонерской — сказочное место с домом, напоминающим средневековый замок с драконами."),
    Description(content="Сангальский сад — часть исторического комплекса завода Сан-Галли, созданного в 1853 году."),
    Description(content="«Кулич и Пасха» — необычная церковь, выполненная в виде пасхальных блюд."),
    Description(content="Дом Бака — доходный дом начала XX века, известный своими витражами и галереями."),
    Description(content="Буддийский храм «Дацан Гунзэчойнэй» — редкий пример буддийского храма в европейском стиле."),
    Description(content="Соборная мечеть Санкт-Петербурга — крупнейшая мечеть в России и Европе."),
    Description(content="«Башня грифонов» — мистическое здание с алхимическими символами, скрытое во дворах Васильевского острова."),
    Description(content="Котельная «Камчатка» — легендарное место работы Виктора Цоя, ныне музей-клуб группы «Кино»."),
    Description(content="Двор духов на Васильевском острове — мистическое место с загадочной атмосферой и легендами."),
    Description(content="Церковь Александра Невского в Петергофе — готическая капелла, построенная для Марии Фёдоровны."),
    Description(content="Дача Громова — дача XIX века в стиле модерн, использовавшаяся как место отдыха петербуржцев."),
    Description(content="Лютеранская кирха Святого Михаила — один из старейших лютеранских храмов на Васильевском острове."),
    Description(content="Музей-квартира Достоевского — место, где писатель провел последние годы и написал свои знаменитые произведения.")
]

# Сохраняем описания в базу
Description.objects.bulk_create(descriptions_unique)

# Создаем новые объекты Place
places_unique = [
    Place(name="Египетский зал в Эрмитаже", latitude=59.9400, longitude=30.3150, description=descriptions_unique[0]),
    Place(name="Золотой павлин в Эрмитаже", latitude=59.9400, longitude=30.3150, description=descriptions_unique[1]),
    Place(name="Музей Фаберже", latitude=59.9350, longitude=30.3320, description=descriptions_unique[2]),
    Place(name="Юсуповский дворец", latitude=59.9290, longitude=30.2970, description=descriptions_unique[3]),
    Place(name="Гранд Макет Россия", latitude=59.9230, longitude=30.3180, description=descriptions_unique[4]),
    Place(name="Доходный дом трёх Бенуа", latitude=59.9447, longitude=30.3584, description=descriptions_unique[5]),
    Place(name="Часовня Ксении Блаженной", latitude=59.9353, longitude=30.2583, description=descriptions_unique[6]),
    Place(name="Двор с замком", latitude=59.9210, longitude=30.3080, description=descriptions_unique[7]),
    Place(name="Сангальский сад", latitude=59.9140, longitude=30.3560, description=descriptions_unique[8]),
    Place(name="«Кулич и Пасха»", latitude=59.9097, longitude=30.3067, description=descriptions_unique[9]),
    Place(name="Дом Бака", latitude=59.9380, longitude=30.3660, description=descriptions_unique[10]),
    Place(name="Буддийский храм «Дацан Гунзэчойнэй»", latitude=59.9878, longitude=30.1861, description=descriptions_unique[11]),
    Place(name="Соборная мечеть", latitude=59.9570, longitude=30.3212, description=descriptions_unique[12]),
    Place(name="Башня грифонов", latitude=59.9362, longitude=30.3167, description=descriptions_unique[13]),
    Place(name="Котельная «Камчатка»", latitude=59.9500, longitude=30.2833, description=descriptions_unique[14]),
    Place(name="Двор духов", latitude=59.9420, longitude=30.2780, description=descriptions_unique[15]),
    Place(name="Церковь Александра Невского в Петергофе", latitude=59.8745, longitude=29.8770, description=descriptions_unique[16]),
    Place(name="Дача Громова", latitude=59.9710, longitude=30.2850, description=descriptions_unique[17]),
    Place(name="Лютеранская кирха Святого Михаила", latitude=59.9390, longitude=30.2920, description=descriptions_unique[18]),
    Place(name="Музей-квартира Достоевского", latitude=59.9292, longitude=30.3528, description=descriptions_unique[19])
]

# Сохраняем объекты в базу данных
Place.objects.bulk_create(places_unique)

print("20 уникальных достопримечательностей Санкт-Петербурга успешно добавлены в базу данных!")
