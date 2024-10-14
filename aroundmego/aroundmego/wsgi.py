"""
WSGI config for aroundmego project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import threading
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aroundmego.settings")

application = get_wsgi_application()

# Импортируем после настройки приложения
def start_bot():
    from core.telegram_bot import start_bot
    start_bot()

# Запуск бота в отдельном потоке
bot_thread = threading.Thread(target=start_bot)
bot_thread.setDaemon(True)
bot_thread.start()
