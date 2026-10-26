from datetime import date
from decimal import Decimal

from django.db import transaction
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render

from .forms import (
    AbonoHorasCompensadasForm,
    SolicitudDescansoComplementarioForm,
    SolicitudPermisoDiasAdministrativosForm,
)
from .models import (
    AbonoDiasAdministrativos,
    AbonoHorasCompensadas,
    DatosJardin,
    Estamento,
    Funcionaria,
    SolicitudDescansoComplementario,
    SolicitudPermisoDiasAdministrativos,
)

GRUPOS_ESTAMENTO = [
    (Estamento.PROFESIONAL, "Educadoras"),
    (Estamento.TECNICO, "Técnicos"),
    (Estamento.AUXILIAR, "Personal auxiliar"),
]


def dashboard(request):
    return render(request, "registro/dashboard.html", {"jardin": DatosJardin})


def descanso_complementario(request):
    grupos = []
    for valor, titulo in GRUPOS_ESTAMENTO:
        filas = [
            {
                "funcionaria": f,
                "nombre_corto": f.nombre_corto(),
                "horas_disponibles": f.saldo_horas_compensadas(),
                "horas_utilizadas_mes": f.horas_utilizadas_mes_actual(),
            }
            for f in Funcionaria.objects.filter(estamento=valor)
        ]
        grupos.append({"titulo": titulo, "filas": filas})
    return render(request, "registro/descanso_complementario.html", {"grupos": grupos})


def dias_administrativos(request):
    grupos = []
    for valor, titulo in GRUPOS_ESTAMENTO:
        filas = [
            {
                "funcionaria": f,
                "nombre_corto": f.nombre_corto(),
                "dias_disponibles": f.saldo_dias_administrativos(),
                "dias_utilizados_anio": f.dias_utilizados_anio_actual(),
            }
            for f in Funcionaria.objects.filter(estamento=valor)
        ]
        grupos.append({"titulo": titulo, "filas": filas})
    return render(request, "registro/dias_administrativos.html", {"grupos": grupos})


def cargar_horas(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    funcionaria = get_object_or_404(Funcionaria, pk=request.POST.get("funcionaria_id"))
    form = AbonoHorasCompensadasForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)

    abono = form.save(commit=False)
    abono.funcionaria = funcionaria
    abono.save()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se cargaron {abono.cantidad_horas} horas a {funcionaria.nombre_corto()}.",
            "horas_disponibles": str(funcionaria.saldo_horas_compensadas()),
        }
    )


def descontar_horas(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    funcionaria = get_object_or_404(Funcionaria, pk=request.POST.get("funcionaria_id"))
    form = SolicitudDescansoComplementarioForm(request.POST, funcionaria=funcionaria)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)

    solicitud = form.save(commit=False)
    solicitud.funcionaria = funcionaria
    solicitud.save()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se descontaron {solicitud.horas_solicitadas:.2f} horas a {funcionaria.nombre_corto()}.",
            "horas_disponibles": str(funcionaria.saldo_horas_compensadas()),
            "horas_utilizadas_mes": str(funcionaria.horas_utilizadas_mes_actual()),
        }
    )


def historial_horas(request, funcionaria_id):
    funcionaria = get_object_or_404(Funcionaria, pk=funcionaria_id)

    cargas = [
        {
            "id": abono.id,
            "fecha": abono.fecha.strftime("%d-%m-%Y"),
            "cantidad_horas": str(abono.cantidad_horas),
            "motivo": abono.motivo,
        }
        for abono in funcionaria.abonos_horas.all()
    ]
    usos = [
        {
            "id": solicitud.id,
            "dia": solicitud.dia.strftime("%d-%m-%Y"),
            "desde": solicitud.desde.strftime("%H:%M"),
            "hasta": solicitud.hasta.strftime("%H:%M"),
            "fecha_solicitud": solicitud.fecha_solicitud.strftime("%d-%m-%Y"),
            "horas_solicitadas": f"{solicitud.horas_solicitadas:.2f}",
        }
        for solicitud in funcionaria.solicitudes_descanso.all()
    ]

    return JsonResponse({"cargas": cargas, "usos": usos})


def eliminar_abono_horas(request, abono_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    abono = get_object_or_404(AbonoHorasCompensadas, pk=abono_id)
    funcionaria = abono.funcionaria
    abono.delete()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se eliminó la carga de horas de {funcionaria.nombre_corto()}.",
            "horas_disponibles": str(funcionaria.saldo_horas_compensadas()),
        }
    )


def eliminar_solicitud_descanso(request, solicitud_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    solicitud = get_object_or_404(SolicitudDescansoComplementario, pk=solicitud_id)
    funcionaria = solicitud.funcionaria
    solicitud.delete()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se eliminó el registro de horas utilizadas de {funcionaria.nombre_corto()}.",
            "horas_disponibles": str(funcionaria.saldo_horas_compensadas()),
            "horas_utilizadas_mes": str(funcionaria.horas_utilizadas_mes_actual()),
        }
    )


def cargar_dias_equipo(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    dias_nuevos = Decimal("6")
    hoy = date.today()
    resultados = []

    with transaction.atomic():
        for funcionaria in Funcionaria.objects.all():
            saldo_actual = funcionaria.saldo_dias_administrativos()
            if saldo_actual > 0:
                AbonoDiasAdministrativos.objects.create(
                    funcionaria=funcionaria,
                    cantidad_dias=-saldo_actual,
                    fecha=hoy,
                )
            AbonoDiasAdministrativos.objects.create(
                funcionaria=funcionaria,
                cantidad_dias=dias_nuevos,
                fecha=hoy,
            )
            resultados.append(
                {
                    "funcionaria_id": funcionaria.id,
                    "dias_disponibles": str(funcionaria.saldo_dias_administrativos()),
                }
            )

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se cargaron {dias_nuevos} días administrativos a todo el equipo.",
            "funcionarias": resultados,
        }
    )


def descontar_dias(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    funcionaria = get_object_or_404(Funcionaria, pk=request.POST.get("funcionaria_id"))
    form = SolicitudPermisoDiasAdministrativosForm(request.POST, funcionaria=funcionaria)
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors.get_json_data()}, status=400)

    solicitud = form.save(commit=False)
    solicitud.funcionaria = funcionaria
    solicitud.save()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se descontaron {solicitud.cantidad_dias} días a {funcionaria.nombre_corto()}.",
            "dias_disponibles": str(funcionaria.saldo_dias_administrativos()),
            "dias_utilizados_anio": str(funcionaria.dias_utilizados_anio_actual()),
        }
    )


def historial_dias(request, funcionaria_id):
    funcionaria = get_object_or_404(Funcionaria, pk=funcionaria_id)

    cargas = [
        {
            "fecha": abono.fecha.strftime("%d-%m-%Y"),
            "cantidad_dias": str(abono.cantidad_dias),
        }
        for abono in funcionaria.abonos_dias.all()
    ]
    usos = [
        {
            "id": solicitud.id,
            "desde": solicitud.desde.strftime("%d-%m-%Y"),
            "hasta": solicitud.hasta.strftime("%d-%m-%Y"),
            "fecha_solicitud": solicitud.fecha_solicitud.strftime("%d-%m-%Y"),
            "cantidad_dias": str(solicitud.cantidad_dias),
        }
        for solicitud in funcionaria.solicitudes_permiso.all()
    ]

    return JsonResponse({"cargas": cargas, "usos": usos})


def eliminar_solicitud_permiso(request, solicitud_id):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    solicitud = get_object_or_404(SolicitudPermisoDiasAdministrativos, pk=solicitud_id)
    funcionaria = solicitud.funcionaria
    solicitud.delete()

    return JsonResponse(
        {
            "ok": True,
            "mensaje": f"Se eliminó el registro de días utilizados de {funcionaria.nombre_corto()}.",
            "dias_disponibles": str(funcionaria.saldo_dias_administrativos()),
            "dias_utilizados_anio": str(funcionaria.dias_utilizados_anio_actual()),
        }
    )
