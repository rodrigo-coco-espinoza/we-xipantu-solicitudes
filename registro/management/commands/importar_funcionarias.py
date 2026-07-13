import csv
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from registro.models import CalidadJuridica, Cargo, Estamento, Funcionaria, NivelAtencion

MAPA_ESTAMENTO = {
    "AUXILIAR": Estamento.AUXILIAR,
    "PROFESIONAL": Estamento.PROFESIONAL,
    "TECNICO": Estamento.TECNICO,
}

MAPA_CARGO = {
    "AUXILIAR SERVICIO JARD.INFANTIL": Cargo.AUXILIAR_SERVICIO,
    "E.PARV.PEDAG.": Cargo.EDUCADORA_PARVULOS,
    "TEC.EDUC.PARVULOS": Cargo.TECNICO_PARVULOS,
}

MAPA_CALIDAD_JURIDICA = {
    "CONTRATA": CalidadJuridica.CONTRATA,
    "TITULAR": CalidadJuridica.TITULAR,
}

MAPA_NIVEL_ATENCION = {
    "": "",
    "NIVEL MEDIO MENOR": NivelAtencion.MEDIO_MENOR,
    "NIVEL MEDIO MAYOR": NivelAtencion.MEDIO_MAYOR,
    "SALA CUNA MENOR": NivelAtencion.SALA_CUNA_MENOR,
    "SALA CUNA MAYOR": NivelAtencion.SALA_CUNA_MAYOR,
    "SALA CUNA MENOR Y MAYOR": NivelAtencion.SALA_CUNA_MENOR_MAYOR,
}


class Command(BaseCommand):
    help = "Importa/actualiza funcionarias desde un CSV separado por ';' (identifica por código)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path")

    def handle(self, *args, **options):
        ruta = options["csv_path"]
        creadas = 0
        actualizadas = 0

        with open(ruta, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo, delimiter=";")
            lector.fieldnames = [nombre.strip() for nombre in lector.fieldnames]
            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    datos = self._mapear_fila(fila)
                except (KeyError, ValueError) as error:
                    raise CommandError(f"Fila {numero_fila}: {error}") from error

                codigo = datos.pop("codigo")
                _, creada = Funcionaria.objects.update_or_create(codigo=codigo, defaults=datos)
                if creada:
                    creadas += 1
                else:
                    actualizadas += 1

        self.stdout.write(self.style.SUCCESS(f"{creadas} funcionarias creadas, {actualizadas} actualizadas."))

    def _mapear_fila(self, fila):
        estamento_csv = fila["ESTAMENTO"].strip().upper()
        cargo_csv = fila["CARGO"].strip().upper()
        calidad_csv = fila["C. JURIDICA"].strip().upper()
        nivel_csv = fila["NIVEL DE ATENCION"].strip().upper()

        if estamento_csv not in MAPA_ESTAMENTO:
            raise ValueError(f"estamento desconocido: {estamento_csv!r}")
        if cargo_csv not in MAPA_CARGO:
            raise ValueError(f"cargo desconocido: {cargo_csv!r}")
        if calidad_csv not in MAPA_CALIDAD_JURIDICA:
            raise ValueError(f"calidad jurídica desconocida: {calidad_csv!r}")
        if nivel_csv not in MAPA_NIVEL_ATENCION:
            raise ValueError(f"nivel de atención desconocido: {nivel_csv!r}")

        return {
            "codigo": fila["CODIGO FUNC."].strip(),
            "rut": fila["RUT"].strip(),
            "dv": fila["DV"].strip(),
            "apellido_paterno": fila["A. PATERNO"].strip(),
            "apellido_materno": fila["A. MATERNO"].strip(),
            "nombres": fila["NOMBRES"].strip(),
            "estamento": MAPA_ESTAMENTO[estamento_csv],
            "cargo": MAPA_CARGO[cargo_csv],
            "calidad_juridica": MAPA_CALIDAD_JURIDICA[calidad_csv],
            "fecha_ingreso": datetime.strptime(fila["FECHA DE INGRESO"].strip(), "%d-%m-%Y").date(),
            "nivel_atencion": MAPA_NIVEL_ATENCION[nivel_csv],
            "grupo": fila["GRUPO"].strip().replace(" Y ", " y "),
            "jornada": int(fila["JORNADA"].strip().split()[0]),
            "horario": fila["HORARIO"].strip(),
            "observaciones": fila["OBSERVACIONES"].strip(),
            "direccion_particular": fila["DIRECCION PARTICULAR"].strip(),
            "comuna_residencia": fila["COMUNA DE RESIDENCIA"].strip(),
            "telefono": fila["TELEFONOS"].strip(),
            "correo": fila["CORREO"].strip(),
        }
