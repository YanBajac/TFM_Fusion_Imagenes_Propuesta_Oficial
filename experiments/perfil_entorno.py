# -*- coding: utf-8 -*-
"""Captura el entorno de ejecucion completo y lo deja en un CSV, para que las versiones se citen del dato.

POR QUE. Sin las versiones de los programas el experimento no se puede repetir: la morfologia, las
wavelets y las metricas dependen de la implementacion, y un cambio de version puede mover la tercera
cifra decimal de cualquier tabla. El CSV deja el equipo, el interprete y las versiones, y separa donde
corrio cada cosa: las fusiones y las metricas en CPU; el entrenamiento del detector, en GPU.

Uso:  .venv\\Scripts\\python.exe -X utf8 experiments/perfil_entorno.py
"""
import importlib
import json
import os
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SALIDA = ROOT / 'experiments' / 'results' / 'metrics_reports' / 'entorno.csv'

# Los paquetes que el pipeline usa de verdad, con el nombre de import y el de distribucion. Se listan a
# mano y no se leen de requirements.txt a proposito: lo que interesa es la version INSTALADA que produjo
# estos resultados, no la declarada.
PAQUETES = [
    ('numpy', 'numpy'), ('cv2', 'opencv-python'), ('scipy', 'scipy'),
    ('skimage', 'scikit-image'), ('pywt', 'PyWavelets'), ('dtcwt', 'dtcwt'), ('pandas', 'pandas'),
    ('matplotlib', 'matplotlib'),
    # scikit-learn no va: no esta en requirements.txt y ningun script lo importa.
    ('torch', 'torch'), ('ultralytics', 'ultralytics'),
    ('fitz', 'PyMuPDF'),
]


# PyWavelets 1.9.0 informa mal su version: pywt.__version__ devuelve 1.8.0. Para ese paquete se lee
# primero la del dist-info instalado, que coincide con requirements-lock.txt.
METADATA_PRIMERO = {'PyWavelets'}


def version(mod, dist=None):
    try:
        m = importlib.import_module(mod)
    except Exception as e:
        return f'NO IMPORTA ({type(e).__name__})'
    if dist in METADATA_PRIMERO:
        try:
            from importlib.metadata import version as mv
            return mv(dist)
        except Exception:
            pass
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
    """El modelo de CPU. platform.processor() en Windows devuelve una cadena poco informativa, asi que ahi
    el nombre se lee del registro. No se usa wmic, que las versiones recientes de Windows 11 ya no traen."""
    n = platform.processor() or ''
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r'HARDWARE\DESCRIPTION\System\CentralProcessor\0') as k:
                return winreg.QueryValueEx(k, 'ProcessorNameString')[0].strip()
        except Exception:
            pass
    return n or 'desconocido'


def ram_gb():
    """La memoria fisica total. En Windows, con GlobalMemoryStatusEx (campo ullTotalPhys)."""
    try:
        if os.name == 'nt':
            import ctypes

            class Memoria(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                            ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                            ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                            ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                            ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]

            m = Memoria()
            m.dwLength = ctypes.sizeof(Memoria)
            if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return None
            return round(m.ullTotalPhys / 1024 ** 3, 1)
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
    devuelve la ruta absoluta, que arrastra el arbol de carpetas del equipo y no debe publicarse.
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
        filas.append(('paquete', dist, version(mod, dist)))

    # Donde corrio cada cosa.
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
