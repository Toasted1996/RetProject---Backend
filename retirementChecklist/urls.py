from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Rutas de la app principal
    path('', include('retirementApp.urls')),
    # Rutas de autenticacion integrada en Django
    path('accounts/', include('django.contrib.auth.urls'))
]

# Configuración para archivos estáticos (CSS, JS, imágenes del proyecto)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Configuración para archivos media (imágenes subidas por usuarios)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

