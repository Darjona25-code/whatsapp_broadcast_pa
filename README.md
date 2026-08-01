# WhatsApp Business PA — Listas de Difusión

Aplicación de escritorio en Python para usuarios de **WhatsApp Business en Panamá**.
Permite pegar texto copiado desde páginas web con datos de contactos
(nombres, números de celular y correos), procesarlo automáticamente y generar
una lista limpia lista para copiar y pegar en las **listas de difusión
(Broadcast)** de WhatsApp Business.

## Características

- Interfaz gráfica moderna con **CustomTkinter**.
- Detección automática de **nombre, teléfono y correo** sin importar el orden
  o el separador usado (`|`, `-`, `;`, líneas separadas, etc.).
- Normalización de teléfonos panameños al formato internacional:
  - `6673-2629` → `+50766732629`
  - `+507 6673-2629` / `00507 6673-2629` → `+50766732629`
- Estados por contacto: **Válido**, **Revisar teléfono** e **Información incompleta**.
- Tabla de resultados con colores por estado.
- **Lista para Broadcast**: solo teléfonos `+507...`, uno por línea, con botón de copiado.
- **Reporte completo**: `Nombre | +507... | correo`, con botón de copiado.
- Exportación a **CSV** (compatible con Excel) y **Excel (.xlsx)** con colores.
- Guardado automático de la última sesión y restauración al abrir.

## Requisitos

- **Windows** (objetivo de empaquetado: ejecutable .exe).
- **Python 3.11 o superior**.

## Instalación

```bat
cd whatsapp_broadcast_pa
python -m pip install -r requirements.txt
```

## Ejecución

```bat
python main.py
```

## Cómo se usa

1. Copia el texto desde la página web (nombre, teléfono y correo de cada persona).
2. Pégalo en el área superior de la aplicación.
3. Presiona **Procesar**.
4. Usa los botones de copiado para la **Lista para Broadcast** o el **Reporte completo**,
   o exporta a CSV/Excel.

### Formatos de entrada soportados

```
Patricia Guevara
pangelica_27@hotmail.com
6673-2629
```

```
María López | 6222-3344 | maria@gmail.com
```

```
Carlos Ruiz - carlos@hotmail.com - 6777-8888
```

Los tres se procesan igual y producen el mismo tipo de resultado.

### Estados posibles

| Estado | Significado |
| --- | --- |
| Válido | Nombre, teléfono y correo correctos. |
| Revisar teléfono | El teléfono no parece un número móvil panameño válido. |
| Información incompleta | Falta el nombre, el teléfono o el correo. |

## Ejecutar las pruebas

```bat
python -m unittest discover tests
```

## Empaquetado con PyInstaller

Ejecuta el script incluido:

```bat
build.bat
```

O manualmente:

```bat
python -m pip install pyinstaller
python -m PyInstaller --noconfirm --onefile --windowed --name WhatsAppBroadcastPA main.py
```

El ejecutable se genera en `dist\WhatsAppBroadcastPA.exe`.

> El estado guardado se almacena en `%APPDATA%\WhatsAppBroadcastPA`, fuera del
> ejecutable, para que la persistencia funcione también en versiones
> empaquetadas con PyInstaller.

## Estructura del proyecto

```
whatsapp_broadcast_pa/
├── main.py               # Punto de entrada
├── requirements.txt      # Dependencias
├── build.bat             # Script de compilación PyInstaller
├── core/                 # Lógica de negocio
│   ├── models.py         # Contacto y estados
│   ├── normalizer.py     # Normalización de teléfonos y nombres
│   ├── parser.py         # Extracción de datos desde texto libre
│   ├── report.py         # Generación de los reportes de salida
│   ├── exporter.py       # Exportación a CSV y Excel
│   └── persistence.py    # Guardado/restauración de la sesión
├── ui/                   # Interfaz gráfica
│   ├── app.py            # Ventana principal
│   └── widgets.py        # Tabla de resultados
└── tests/                # Pruebas automáticas
```
