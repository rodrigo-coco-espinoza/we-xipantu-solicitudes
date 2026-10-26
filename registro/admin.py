from django.contrib import admin

from .models import (
    AbonoDiasAdministrativos,
    AbonoHorasCompensadas,
    Funcionaria,
    SolicitudDescansoComplementario,
    SolicitudPermisoDiasAdministrativos,
)


@admin.register(Funcionaria)
class FuncionariaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "apellido_paterno",
        "apellido_materno",
        "nombres",
        "cargo",
        "estamento",
        "calidad_juridica",
        "jornada",
    )
    list_filter = ("estamento", "cargo", "calidad_juridica", "nivel_atencion")
    search_fields = ("codigo", "rut", "apellido_paterno", "apellido_materno", "nombres")
    ordering = ("apellido_paterno", "apellido_materno", "nombres")


@admin.register(AbonoHorasCompensadas)
class AbonoHorasCompensadasAdmin(admin.ModelAdmin):
    list_display = ("funcionaria", "cantidad_horas", "fecha", "motivo")
    list_filter = ("fecha",)
    search_fields = ("funcionaria__apellido_paterno", "funcionaria__apellido_materno", "funcionaria__nombres")
    autocomplete_fields = ("funcionaria",)
    date_hierarchy = "fecha"


@admin.register(SolicitudDescansoComplementario)
class SolicitudDescansoComplementarioAdmin(admin.ModelAdmin):
    list_display = ("funcionaria", "dia", "desde", "hasta", "fecha_solicitud")
    list_filter = ("dia",)
    search_fields = ("funcionaria__apellido_paterno", "funcionaria__apellido_materno", "funcionaria__nombres")
    autocomplete_fields = ("funcionaria",)
    date_hierarchy = "dia"


@admin.register(AbonoDiasAdministrativos)
class AbonoDiasAdministrativosAdmin(admin.ModelAdmin):
    list_display = ("funcionaria", "cantidad_dias", "fecha")
    list_filter = ("fecha",)
    search_fields = ("funcionaria__apellido_paterno", "funcionaria__apellido_materno", "funcionaria__nombres")
    autocomplete_fields = ("funcionaria",)
    date_hierarchy = "fecha"


@admin.register(SolicitudPermisoDiasAdministrativos)
class SolicitudPermisoDiasAdministrativosAdmin(admin.ModelAdmin):
    list_display = ("funcionaria", "cantidad_dias", "desde", "hasta", "fecha_solicitud")
    list_filter = ("desde",)
    search_fields = ("funcionaria__apellido_paterno", "funcionaria__apellido_materno", "funcionaria__nombres")
    autocomplete_fields = ("funcionaria",)
    date_hierarchy = "desde"
