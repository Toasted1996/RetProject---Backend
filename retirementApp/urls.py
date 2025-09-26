from django.urls import path
from .views import inicio,listaGestores, crearGestor, editarGestor, eliminarGestor, custom_login, custom_logout, register_user

urlpatterns = [
    path('', inicio, name='inicio'),
    


    #Autenticacion integrada en Django
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('register/', register_user, name='register'),

    #URLs CRUD GESTORES
    path('gestores/', listaGestores, name='gestores'),
    path('gestores/crear/', crearGestor, name='crear_gestor'),
    path('gestores/<int:id>/', editarGestor, name='editar_gestor'),
    path('gestores/<int:id>/', eliminarGestor, name='eliminar_gestor')
]
