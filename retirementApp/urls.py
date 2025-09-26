from django.urls import path
from .views import listaGestores, crearGestor

urlpatterns = [
    #CRUD GESTORES
    path('gestores/', listaGestores, name='gestores'),
    path('gestores/crear/', crearGestor, name='crear_gestor')
]