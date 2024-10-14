from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Основная страница
    path('get_poi_description/', views.get_poi_description, name='get_poi_description'),  # Маршрут для описания
    path('register/', views.register, name='register'),  # Маршрут для регистрации
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),


    ]
