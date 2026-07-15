from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación y usuarios (RF_1 – RF_7, RNF_1)
    path('api/users/', include('apps.users.urls')),

    # Parches y membresías (RF_8 – RF_11)
    path('api/parches/', include('apps.parches.urls')),

    # Eventos y suscripciones (RF_12 – RF_19, RF_22, RF_26, RF_29, RF_32)
    path('api/parches/', include('apps.eventos.urls')),
    path('api/',         include('apps.eventos.urls')),  # rutas sin parche_id (deudas-pendientes, participantes)

    # Finanzas, balance e historial (RF_21, RF_23, RF_24, RF_25, RF_27, RF_28, RF_29)
    path('api/parches/', include('apps.finanzas.urls')),
    path('api/finanzas/', include('apps.finanzas.urls')),  # rutas globales (boletin, balance/mensual)

    # Espacios de ahorro (RF_20)
    path('api/parches/', include('apps.ahorros.urls')),
    path('api/ahorros/', include('apps.ahorros.urls')),   # ruta para aportar sin parche_id

    # Soporte y feedback (RF_30)
    path('api/soporte/', include('apps.soporte.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)