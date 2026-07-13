from datetime import date, datetime
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


def validar_medio_dia(value):
    if (value * 2) % 1 != 0:
        raise ValidationError("La cantidad debe registrarse en medios días o días enteros (ej: 0.5, 1, 1.5, 2).")


class DatosJardin:
    """Datos institucionales fijos del jardín (no cambian, no requieren tabla)."""

    nombre = "Sala Cuna y Jardín Infantil We Xipantu"
    codigo = "13121001"
    rbd = None
    provincia = "Centro"
    direccion = "Club Hípico 5789, Pedro Aguirre Cerda"


class Estamento(models.TextChoices):
    AUXILIAR = "auxiliar", "Auxiliar"
    PROFESIONAL = "profesional", "Profesional"
    TECNICO = "tecnico", "Técnico"


class Cargo(models.TextChoices):
    AUXILIAR_SERVICIO = "auxiliar_servicio", "Auxiliar servicio jardín infantil"
    EDUCADORA_PARVULOS = "educadora_parvulos", "Educadora de párvulos pedagógica"
    TECNICO_PARVULOS = "tecnico_parvulos", "Técnico educadora de párvulo"


class CalidadJuridica(models.TextChoices):
    CONTRATA = "contrata", "Contrata"
    TITULAR = "titular", "Titular"


class NivelAtencion(models.TextChoices):
    MEDIO_MENOR = "medio_menor", "Medio menor"
    MEDIO_MAYOR = "medio_mayor", "Medio mayor"
    SALA_CUNA_MENOR = "sala_cuna_menor", "Sala cuna menor"
    SALA_CUNA_MAYOR = "sala_cuna_mayor", "Sala cuna mayor"
    SALA_CUNA_MENOR_MAYOR = "sala_cuna_menor_mayor", "Sala cuna menor y mayor"


class Funcionaria(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    rut = models.CharField(max_length=12)
    dv = models.CharField(max_length=1)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True)
    nombres = models.CharField(max_length=150)
    estamento = models.CharField(max_length=20, choices=Estamento.choices)
    cargo = models.CharField(max_length=30, choices=Cargo.choices)
    calidad_juridica = models.CharField(max_length=10, choices=CalidadJuridica.choices)
    fecha_ingreso = models.DateField()
    nivel_atencion = models.CharField(max_length=30, choices=NivelAtencion.choices, blank=True)
    grupo = models.CharField(max_length=10, blank=True, help_text="Ej: 1, 2, 3, 4, o '1 y 2' si combina grupos")
    jornada = models.PositiveIntegerField(help_text="Horas semanales, ej: 44")
    horario = models.CharField(max_length=200, blank=True)
    observaciones = models.TextField(blank=True)
    direccion_particular = models.CharField(max_length=255, blank=True)
    comuna_residencia = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)

    class Meta:
        ordering = ["apellido_paterno", "apellido_materno", "nombres"]
        verbose_name_plural = "Funcionarias"

    def __str__(self):
        return f"{self.apellido_paterno} {self.apellido_materno}, {self.nombres}"

    @property
    def rut_completo(self):
        return f"{self.rut}-{self.dv}"

    def nombre_corto(self):
        primer_nombre = self.nombres.split()[0] if self.nombres else ""
        return f"{primer_nombre} {self.apellido_paterno}".strip()

    def saldo_horas_compensadas(self):
        abonado = self.abonos_horas.aggregate(total=Sum("cantidad_horas"))["total"] or Decimal("0")
        usado = sum((s.horas_solicitadas for s in self.solicitudes_descanso.all()), Decimal("0"))
        return abonado - usado

    saldo_horas_compensadas.short_description = "Saldo horas compensadas"

    def horas_utilizadas_mes_actual(self):
        hoy = date.today()
        solicitudes = self.solicitudes_descanso.filter(dia__year=hoy.year, dia__month=hoy.month)
        return sum((s.horas_solicitadas for s in solicitudes), Decimal("0"))

    def saldo_dias_administrativos(self):
        abonado = self.abonos_dias.aggregate(total=Sum("cantidad_dias"))["total"] or Decimal("0")
        usado = self.solicitudes_permiso.aggregate(total=Sum("cantidad_dias"))["total"] or Decimal("0")
        return abonado - usado

    saldo_dias_administrativos.short_description = "Saldo días administrativos"

    def dias_utilizados_anio_actual(self):
        hoy = date.today()
        solicitudes = self.solicitudes_permiso.filter(desde__year=hoy.year)
        return solicitudes.aggregate(total=Sum("cantidad_dias"))["total"] or Decimal("0")


class AbonoHorasCompensadas(models.Model):
    """Carga de horas: cuando a la funcionaria se le reconocen horas por trabajar fuera de jornada."""

    funcionaria = models.ForeignKey(
        Funcionaria, related_name="abonos_horas", on_delete=models.PROTECT
    )
    cantidad_horas = models.DecimalField(max_digits=5, decimal_places=2)
    fecha = models.DateField(default=date.today)
    motivo = models.CharField(max_length=255, blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]
        verbose_name = "Abono de horas compensadas"
        verbose_name_plural = "Abonos de horas compensadas"

    def __str__(self):
        return f"{self.funcionaria} +{self.cantidad_horas}h ({self.fecha})"


class SolicitudDescansoComplementario(models.Model):
    """Uso de horas compensadas: nombre oficial del trámite."""

    funcionaria = models.ForeignKey(
        Funcionaria, related_name="solicitudes_descanso", on_delete=models.PROTECT
    )
    dia = models.DateField()
    desde = models.TimeField()
    hasta = models.TimeField()
    fecha_solicitud = models.DateField(default=date.today)
    documento = models.FileField(
        upload_to="descansos_complementarios/%Y/%m/", blank=True, null=True
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dia", "-creado"]
        verbose_name = "Solicitud de descanso complementario"
        verbose_name_plural = "Solicitudes de descanso complementario"

    def __str__(self):
        return f"{self.funcionaria} {self.dia} {self.desde}-{self.hasta}"

    @property
    def horas_solicitadas(self):
        inicio = datetime.combine(self.dia, self.desde)
        fin = datetime.combine(self.dia, self.hasta)
        return Decimal(str((fin - inicio).total_seconds() / 3600))


class AbonoDiasAdministrativos(models.Model):
    """Carga de días: una vez al año, la institución determina la cantidad."""

    funcionaria = models.ForeignKey(
        Funcionaria, related_name="abonos_dias", on_delete=models.PROTECT
    )
    cantidad_dias = models.DecimalField(max_digits=4, decimal_places=1)
    fecha = models.DateField(default=date.today)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-creado"]
        verbose_name = "Abono de días administrativos"
        verbose_name_plural = "Abonos de días administrativos"

    def __str__(self):
        return f"{self.funcionaria} +{self.cantidad_dias}d ({self.fecha})"


class SolicitudPermisoDiasAdministrativos(models.Model):
    """Uso de días administrativos: nombre oficial 'Solicitud de permiso (con goce de remuneraciones)'."""

    funcionaria = models.ForeignKey(
        Funcionaria, related_name="solicitudes_permiso", on_delete=models.PROTECT
    )
    cantidad_dias = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        validators=[MinValueValidator(Decimal("0.5")), validar_medio_dia],
    )
    desde = models.DateField()
    hasta = models.DateField()
    fecha_solicitud = models.DateField(default=date.today)
    documento = models.FileField(
        upload_to="solicitudes_permiso/%Y/%m/", blank=True, null=True
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-desde", "-creado"]
        verbose_name = "Solicitud de permiso (días administrativos)"
        verbose_name_plural = "Solicitudes de permiso (días administrativos)"

    def __str__(self):
        return f"{self.funcionaria} {self.cantidad_dias}d ({self.desde} a {self.hasta})"