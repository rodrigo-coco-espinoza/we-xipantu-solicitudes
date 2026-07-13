from datetime import datetime
from decimal import Decimal

from django import forms

from .models import (
    AbonoHorasCompensadas,
    SolicitudDescansoComplementario,
    SolicitudPermisoDiasAdministrativos,
)


class AbonoHorasCompensadasForm(forms.ModelForm):
    class Meta:
        model = AbonoHorasCompensadas
        fields = ["cantidad_horas", "fecha", "motivo"]
        widgets = {
            "cantidad_horas": forms.NumberInput(attrs={"step": "0.01", "min": "0.01"}),
            "fecha": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
            "motivo": forms.TextInput(),
        }
        labels = {
            "cantidad_horas": "Número de horas",
            "fecha": "Fecha",
            "motivo": "Motivo",
        }

    def clean_cantidad_horas(self):
        cantidad = self.cleaned_data["cantidad_horas"]
        if cantidad <= Decimal("0"):
            raise forms.ValidationError("La cantidad de horas debe ser mayor a 0.")
        return cantidad


class SolicitudDescansoComplementarioForm(forms.ModelForm):
    class Meta:
        model = SolicitudDescansoComplementario
        fields = ["dia", "desde", "hasta", "fecha_solicitud"]
        widgets = {
            "dia": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
            "desde": forms.TimeInput(attrs={"type": "time"}),
            "hasta": forms.TimeInput(attrs={"type": "time"}),
            "fecha_solicitud": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
        }
        labels = {
            "dia": "Día",
            "desde": "Desde",
            "hasta": "Hasta",
            "fecha_solicitud": "Fecha de solicitud",
        }

    def __init__(self, *args, funcionaria=None, **kwargs):
        self.funcionaria = funcionaria
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        dia = cleaned_data.get("dia")
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")

        if desde and hasta and hasta <= desde:
            raise forms.ValidationError("La hora 'hasta' debe ser posterior a la hora 'desde'.")

        if dia and desde and hasta and self.funcionaria is not None:
            inicio = datetime.combine(dia, desde)
            fin = datetime.combine(dia, hasta)
            horas_solicitadas = Decimal(str((fin - inicio).total_seconds() / 3600))
            disponibles = self.funcionaria.saldo_horas_compensadas()
            if horas_solicitadas > disponibles:
                raise forms.ValidationError(
                    f"La funcionaria solo tiene {disponibles} horas disponibles."
                )

        return cleaned_data


class SolicitudPermisoDiasAdministrativosForm(forms.ModelForm):
    class Meta:
        model = SolicitudPermisoDiasAdministrativos
        fields = ["cantidad_dias", "desde", "hasta", "fecha_solicitud"]
        widgets = {
            "cantidad_dias": forms.NumberInput(attrs={"step": "0.5", "min": "0.5"}),
            "desde": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
            "hasta": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
            "fecha_solicitud": forms.DateInput(attrs={"type": "date", "lang": "es-CL"}),
        }
        labels = {
            "cantidad_dias": "Cantidad de días",
            "desde": "Desde",
            "hasta": "Hasta",
            "fecha_solicitud": "Fecha de solicitud",
        }

    def __init__(self, *args, funcionaria=None, **kwargs):
        self.funcionaria = funcionaria
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        desde = cleaned_data.get("desde")
        hasta = cleaned_data.get("hasta")
        cantidad_dias = cleaned_data.get("cantidad_dias")

        if desde and hasta and hasta < desde:
            raise forms.ValidationError("La fecha 'hasta' debe ser posterior o igual a la fecha 'desde'.")

        if cantidad_dias and self.funcionaria is not None:
            disponibles = self.funcionaria.saldo_dias_administrativos()
            if cantidad_dias > disponibles:
                raise forms.ValidationError(
                    f"La funcionaria solo tiene {disponibles} días disponibles."
                )

        return cleaned_data
