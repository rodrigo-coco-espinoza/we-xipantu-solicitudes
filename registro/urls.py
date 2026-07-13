from django.urls import path

from . import views

app_name = "registro"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("descanso-complementario/", views.descanso_complementario, name="descanso_complementario"),
    path("dias-administrativos/", views.dias_administrativos, name="dias_administrativos"),
    path("cargar-horas/", views.cargar_horas, name="cargar_horas"),
    path("descontar-horas/", views.descontar_horas, name="descontar_horas"),
    path("funcionarias/<int:funcionaria_id>/historial/", views.historial_horas, name="historial_horas"),
    path("descontar-dias/", views.descontar_dias, name="descontar_dias"),
    path("funcionarias/<int:funcionaria_id>/historial-dias/", views.historial_dias, name="historial_dias"),
    path("cargar-dias-equipo/", views.cargar_dias_equipo, name="cargar_dias_equipo"),
]
