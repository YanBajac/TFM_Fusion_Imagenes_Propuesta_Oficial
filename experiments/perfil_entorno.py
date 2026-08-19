# -*- coding: utf-8 -*-
"""Captura el entorno de ejecucion completo y lo deja en un CSV, para que el reporte lo cite del dato.

POR QUE. El informe no menciona ni una version de software: cero apariciones de «Python 3» y cero de
OpenCV en sus 92 paginas. Para un reporte tecnico eso es el hueco que mas pesa, porque sin las versiones
el experimento no se puede repetir: la morfologia, las wavelets y las metricas dependen de la
implementacion, y un cambio de version puede mover la tercera cifra decimal de cualquier tabla.

Lo que ya existia es detector_perfil.json, que trae ultralytics, torch, CUDA y la GPU —lo del detector— y
nada del resto del pipeline ni de la maquina.

Y HAY UN DATO QUE HAY QUE CORREGIR CON ESTO. El apendice F del libro afirma que todo se ejecuto «en una
notebook estandar (Intel i7, 16 GB de RAM, sin GPU dedicada)». Hay GPU y se uso: detector_perfil.json
registra cuda = True con una RTX 4050. Las fusiones si corren en CPU; el entrenamiento del detector, no.
El CSV separa las dos cosas para que el texto pueda decirlo bien.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/perfil_entorno.py
"""
import importlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / 'experiments' / 'results' / 'metrics_reports' / 'entorno.csv'

# Los paquetes que el pipeline usa de verdad, con el nombre de import y el de distribucion. Se listan a
# mano y no se leen de requirements.txt a proposito: lo que interesa es la version INSTALADA que produjo
# estos resultados, no la declarada.
PAQUETES = [
    ('numpy', 'numpy'), ('cv2', 'opencv-python'), ('scipy', 'scipy'),
    ('skimage', 'scikit-image'), ('pywt', 'PyWavelets'), ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib'),
    # scikit-learn NO va: no esta en requirements.txt y ningun script del pipeline lo importa.
    # Lo habia puesto por costumbre y metia una fila «NO IMPORTA» en el CSV que el reporte iba a citar.
    ('torch', 'torch'), ('ultralytics', 'ultralytics'),
    ('fitz', 'PyMuPDF'), ('docx', 'python-docx'), ('pptx', 'python-pptx'),
    ('openpyxl', 'openpyxl'), ('yaml', 'PyYAML'),
]


def version(mod):
    try:
        m = importlib.import_module(mod)
    except Exception as e:
        return f'NO IMPORTA ({type(e).__name__})'
    for attr in ('__version__', 'version', 'VERSION'):
        v = getattr(m, attr, None)
        if isinstance(v, str):
            return v
        if v is not None and not callable(v):
            return str(v)
    try:
        from importlib.metadata import version as mv
        return mv(mod)
    except Exception:
        return 'sin atributo de version'


def cpu():
    """El modelo de CPU. platform.processor() en Windows devuelve una cadena poco informativa."""
    n = platform.processor() or ''
    if os.name == 'nt':
        try:
            out = subprocess.run(['wmic', 'cpu', 'get', 'name'], capture_output=True, text=True,
                                 timeout=20).stdout
            lineas = [x.strip() for x in out.splitlines() if x.strip() and 'Name' not in x]
            if lineas:
                return lineas[0]
        except Exception:
            pass
    return n or 'desconocido'


def ram_gb():
    try:
        if os.name == 'nt':
            out = subprocess.run(['wmic', 'computersystem', 'get', 'TotalPhysicalMemory'],
                                 capture_output=True, text=True, timeout=20).stdout
            for x in out.split():
                if x.isdigit():
                    return round(int(x) / 1024 ** 3, 1)
        return round(os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES') / 1024 ** 3, 1)
    except Exception:
        return None


def gpu():
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0), True, torch.version.cuda
        return 'no disponible', False, None
    except Exception:
        return 'torch no importa', False, None


def ruta_interprete():
    """La ruta del interprete RELATIVA a la raiz del repositorio.

    Lo que esta fila tiene que decir es que se corrio con el interprete del entorno virtual del proyecto
    y no con el Python del sistema, y para eso alcanza `.venv\\Scripts\\python.exe`. `sys.executable`
    devuelve la ruta absoluta, que arrastra el arbol de carpetas del equipo —y esa ruta se publicaba en
    la tabla del entorno de la pagina 65 del informe de avances, que se manda al director—.
    """
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        rel = os.path.relpath(sys.executable, raiz)
    except ValueError:                          # otra unidad de disco: no hay relativa posible
        return os.path.basename(sys.executable)
    return rel if not rel.startswith('..') else os.path.basename(sys.executable)


def main():
    g, cuda_ok, cuda_ver = gpu()
    filas = [
        ('interprete', 'Python', platform.python_version()),
        ('interprete', 'implementacion', platform.python_implementation()),
        ('interprete', 'ruta', ruta_interprete()),
        ('sistema', 'sistema operativo', f'{platform.system()} {platform.release()}'),
        ('sistema', 'version detallada', platform.version()),
        ('sistema', 'arquitectura', platform.machine()),
        ('maquina', 'CPU', cpu()),
        ('maquina', 'nucleos logicos', str(os.cpu_count())),
        ('maquina', 'RAM (GB)', str(ram_gb())),
        ('maquina', 'GPU', g),
        ('maquina', 'CUDA disponible', 'si' if cuda_ok else 'no'),
        ('maquina', 'CUDA', cuda_ver or '—'),
    ]
    for mod, dist in PAQUETES:
        filas.append(('paquete', dist, version(mod)))

    # Donde corrio cada cosa. Es el dato que el apendice F del libro tiene mal.
    filas += [
        ('ejecucion', 'fusion y metricas', 'CPU (NumPy y OpenCV; sin GPU)'),
        ('ejecucion', 'entrenamiento e inferencia del detector',
         f'GPU ({g})' if cuda_ok else 'CPU'),
    ]

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with SALIDA.open('w', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['bloque', 'clave', 'valor'])
        w.writerows(filas)

    ancho = max(len(c) for _b, c, _v in filas)
    bl = None
    for b, c, v in filas:
        if b != bl:
            print(f'\n  [{b}]')
            bl = b
        print(f'    {c:<{ancho}}  {v}')
    print(f'\n  -> {SALIDA.relative_to(ROOT)} ({len(filas)} filas)')
    faltan = [c for _b, c, v in filas if 'NO IMPORTA' in str(v)]
    if faltan:
        print(f'  AVISO: no se pudo importar {faltan}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
