from django.urls import path
from .views import inicio,listaGestores, crearGestor, editarGestor, eliminarGestor, register_user, custom_login, custom_logout, crearExpediente, listaExpedientes, editarExpediente, eliminarExpediente, detalleExpediente

urlpatterns = [
    path('', inicio, name='inicio'),
    


    #Autenticacion integrada en Django
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),  
    path('register/', register_user, name='register'),

    #URLs CRUD GESTORES
    path('gestores/', listaGestores, name='gestores'),
    path('gestores/crear/', crearGestor, name='crear_gestor'),
    path('gestores/editar/<int:id>/', editarGestor, name='editar_gestor'), 
    path('gestores/eliminar/<int:id>/', eliminarGestor, name='eliminar_gestor'),
    #path('gestores/detalle/<int:id>/', detalleGestor, name='detalle_gestor'),
    
    
    
    #URLs CRUD EXPEDIENTES
    path('expedientes/', listaExpedientes, name='expedientes'),
    path('expedientes/crear/', crearExpediente, name='crear_expediente'),
    path('expedientes/editar/<int:id>/', editarExpediente, name='editar_expediente'),
    path('expedientes/eliminar/<int:id>/', eliminarExpediente, name='eliminar_expediente'),
    path('expedientes/detalle/<int:id>/', detalleExpediente, name='detalle_expediente')
]
