from django.urls import path
from .views import listaGestores, crearGestor, editarGestor, eliminarGestor

urlpatterns = [
    #CRUD GESTORES
    path('gestores/', listaGestores, name='gestores'),
    path('gestores/crear/', crearGestor, name='crear_gestor'),
    path('gestores/<int:id>/', editarGestor, name='editar_gestor'),
    path('gestores/<int:id>/', eliminarGestor, name='eliminar_gestor')
]