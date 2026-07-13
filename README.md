# We Xipantu - Sistema de registro

Aplicación web local (sin nube) para que la directora de la Sala Cuna y Jardín
Infantil We Xipantu (JUNJI, Chile) registre y consulte:

- **Descanso complementario**: horas compensadas por trabajo fuera de jornada
  (carga y descuento de horas por funcionaria).
- **Días administrativos**: días de permiso con goce de remuneraciones (carga
  anual para todo el equipo y descuento por funcionaria).

No requiere conexión a internet ni instalación de servicios externos: corre
enteramente en el computador de la directora con Python + Django + SQLite.

## Stack técnico

- Python 3 + [Django 6](https://docs.djangoproject.com/en/6.0/)
- Base de datos SQLite (`db.sqlite3`, un solo archivo local)
- Frontend: HTML + CSS + JavaScript vanilla (sin frameworks ni build step)
- Sin dependencias de Node/npm

## Estructura del proyecto

```
core/                        Configuración del proyecto Django (settings, urls raíz)
registro/                    App principal
  models.py                  Funcionaria, AbonoHorasCompensadas,
                              SolicitudDescansoComplementario,
                              AbonoDiasAdministrativos,
                              SolicitudPermisoDiasAdministrativos
  views.py                   Vistas de páginas + endpoints AJAX (JSON)
  forms.py                   Formularios de carga/descuento
  urls.py                    Rutas de la app
  management/commands/
    importar_funcionarias.py Importa/actualiza funcionarias desde un CSV
  templates/registro/        Plantillas HTML
  static/registro/           CSS (paleta institucional), imágenes
data/                        Material fuente (CSV real, PDF institucional) - no versionado
Iniciar We Xipantu.bat       Acceso directo para iniciar el sistema (Windows)
```

## Modelo de datos (resumen)

- `Funcionaria`: ficha de cada trabajadora (rut, cargo, estamento, grupo, etc.),
  importada desde la planilla oficial del jardín.
- `AbonoHorasCompensadas` / `SolicitudDescansoComplementario`: ledger de carga
  y uso de horas compensadas. El saldo es siempre `suma(abonos) - suma(usos)`,
  nunca se edita ni elimina un registro histórico.
- `AbonoDiasAdministrativos` / `SolicitudPermisoDiasAdministrativos`: mismo
  patrón de ledger, pero para días administrativos (vencen a fin de año; la
  carga anual del equipo completo queda registrada como un movimiento de
  descuento del saldo remanente + un movimiento de carga de los días nuevos).

Ninguna vista permite editar o borrar cargas/usos ya guardados: todo el
historial queda como registro contable (append-only), consultable por
funcionaria desde la vista correspondiente (fila desplegable).

## Configuración del entorno de desarrollo

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py importar_funcionarias "data/base-funcionarias.csv"
python manage.py runserver
```

La app queda disponible en `http://127.0.0.1:8000/`.

### Importar/actualizar funcionarias

`importar_funcionarias` es idempotente: identifica a cada funcionaria por su
`codigo` y actualiza sus datos si ya existe, o la crea si es nueva. Seguro de
re-ejecutar cuando cambie la planilla oficial.

```bash
python manage.py importar_funcionarias "ruta/a/planilla.csv"
```

El CSV debe venir separado por `;` con las mismas columnas que la planilla
oficial JUNJI (ver `registro/management/commands/importar_funcionarias.py`
para el detalle exacto de columnas esperadas).

## Uso diario (en el PC de la directora)

Ver [MANUAL_DE_USO.md](MANUAL_DE_USO.md).

## Pendientes conocidos

- Configurar Django admin (`registro/admin.py` está vacío) para edición
  administrativa directa de datos si llegara a ser necesario.
- Crear una cuenta de superusuario si en algún momento se necesita el panel
  de administración (`/admin/`) — hoy ninguna vista de la app requiere login.
- El botón "Cargar días administrativos" y el modal de "Descontar días"
  cubren el flujo principal; no hay edición ni eliminación de movimientos
  cargados por error (habría que corregirlos con un movimiento inverso,
  siguiendo el mismo patrón de ledger append-only).

## Notas de diseño

- `DEBUG = True` se deja intencionalmente así: es una app local de un solo
  usuario, no expuesta a la red (el servidor escucha en `127.0.0.1`), por lo
  que priorizamos la simplicidad de instalación (sin `collectstatic` ni
  `STATIC_ROOT`) sobre el hardening típico de un despliegue en producción.
- La paleta institucional JUNJI está centralizada en
  `registro/static/registro/css/palette.css`.
