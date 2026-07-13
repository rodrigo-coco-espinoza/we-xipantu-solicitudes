# Manual de uso - Sistema We Xipantu

Sistema para registrar y consultar las horas de descanso complementario y los
días administrativos del equipo del jardín. Funciona directamente en este
computador, sin necesidad de internet.

## 1. Instalación

Estos pasos los realiza quien instala el sistema en el computador (no son
necesarios para el uso diario).

1. Copiar la carpeta completa del proyecto al computador (por ejemplo, en
   `Documentos\we-xipantu-solicitudes`).
2. Tener Python 3 instalado.
3. Abrir una terminal (símbolo del sistema) dentro de la carpeta del proyecto
   y ejecutar:

   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py importar_funcionarias "data\base-funcionarias.csv"
   ```

4. Una vez terminado, el sistema queda listo para usarse con el acceso
   directo `Iniciar We Xipantu.bat` (ver siguiente sección).

Si en algún momento cambia la planilla oficial de funcionarias, basta con
volver a ejecutar el paso de `importar_funcionarias` con el archivo
actualizado: el sistema identifica a cada funcionaria por su código y
actualiza sus datos sin duplicar a nadie.

## 2. Cómo iniciar el sistema

1. Ir a la carpeta del proyecto y hacer **doble clic** en
   `Iniciar We Xipantu.bat`.
2. Se abrirá una ventana negra (no cerrarla) y, a los pocos segundos, el
   navegador se abrirá solo mostrando el sistema.
3. Si el navegador no se abre automáticamente, ingresar manualmente esta
   dirección en cualquier navegador: `http://127.0.0.1:8000/`

## 3. Cómo cerrar el sistema

Simplemente cerrar la ventana negra que se abrió al iniciar. Mientras esa
ventana esté abierta, el sistema sigue funcionando; al cerrarla, se apaga.

## 4. Pantallas del sistema

### Inicio

Página de bienvenida con el nombre e imagen del jardín. Desde el menú
superior se accede a las dos secciones principales.

### Descanso complementario

Muestra tres tablas (Educadoras, Técnicos, Personal auxiliar) con, por cada
funcionaria: horas disponibles, horas utilizadas en el mes actual, y dos
botones de acción.

- **Cargar horas**: registra horas nuevas para una funcionaria (por ejemplo,
  cuando trabajó fuera de su jornada habitual). Pide la cantidad de horas, la
  fecha y un motivo opcional.
- **Descontar horas**: registra el uso de horas ya disponibles. Pide el día,
  el horario (desde/hasta, en formato de 24 horas, entre 08:00 y 17:00) y la
  fecha en que se solicitó. El sistema calcula automáticamente cuántas horas
  corresponden y avisa si la funcionaria no tiene saldo suficiente.
- **Ver historial**: al hacer clic en cualquier parte de la fila de una
  funcionaria (fuera de los botones), se despliega su historial completo de
  cargas y usos. Un segundo clic en la misma fila lo vuelve a ocultar. Solo
  se puede tener el historial de una funcionaria abierto a la vez.

### Días administrativos

Misma lógica que la sección anterior, pero para días administrativos (que se
cargan y usan dentro del mismo año calendario):

- **Cargar días administrativos** (botón arriba a la derecha de la página):
  carga 6 días administrativos nuevos a **todas** las funcionarias de una
  sola vez. Pide confirmación antes de aplicarse, porque además elimina los
  días administrativos que le quedaran a cada una del ciclo anterior (los
  días administrativos vencen a fin de año). Se recomienda usar este botón
  una vez al año, al iniciar el nuevo ciclo.
- **Descontar días**: registra el uso de días administrativos por una
  funcionaria específica. Pide el día solicitado y si corresponde a día
  completo o medio día. El sistema avisa si no hay saldo suficiente.
- **Ver historial**: igual que en Descanso complementario, clic en la fila
  para ver las cargas y usos de días de esa funcionaria.

## 5. Preguntas frecuentes

**El navegador no se abrió solo.**
Ingresar manualmente `http://127.0.0.1:8000/` en cualquier navegador mientras
la ventana negra siga abierta.

**Aparece un mensaje de error al iniciar, algo sobre "puerto en uso".**
Puede que el sistema ya esté abierto en otra ventana. Buscar si hay otra
ventana negra abierta antes de iniciar una nueva.

**Cerré el navegador por error.**
No es problema: el sistema sigue funcionando mientras la ventana negra esté
abierta. Basta con abrir un navegador nuevo e ingresar
`http://127.0.0.1:8000/`.

**¿Se pueden editar o borrar cargas/descuentos hechos por error?**
No desde la pantalla actual: por diseño, el sistema no borra ni modifica
registros ya guardados (queda todo como historial). Para corregir un error,
contactar a soporte técnico.
