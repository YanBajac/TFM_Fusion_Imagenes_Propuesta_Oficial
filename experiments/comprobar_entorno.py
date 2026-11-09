# -*- coding: utf-8 -*-
"""Compuerta de entorno: comprueba que estan el interprete y los paquetes ANTES de empezar a correr.

POR QUE. La otra compuerta, verificar_corpus.py, mira los datos; no mira el entorno. Sin esta, a un
clon recien bajado al que le falta un paquete el error no le llega en el segundo cero sino cuando el
paso que lo usa llega a importarlo, y algunos llegan tarde: dtcwt se importa al fusionar
(run_all_fusions.py) y PyMuPDF solo en referencia_pso_ortega_espinoza.py. El sintoma es un
ModuleNotFoundError a mitad de una corrida de veinte minutos, con los pasos anteriores ya escritos
a disco y sin decir que mas falta: se arregla uno, se vuelve a correr, y falta el siguiente.

Este script los mira todos de una vez, contra lo DECLARADO en los dos archivos de requisitos, y
cuando falta algo imprime el comando exacto que lo instala. Tarda menos de un segundo y conviene
correrlo primero, antes de la comprobacion del corpus (verificar_corpus.py).

Comprueba tambien las versiones minimas. No alcanza con que el paquete se importe: numpy 1.23
importa igual y las metricas se calculan, pero requirements.txt pide >=1.26 porque por debajo de esa
el comportamiento de algunas rutinas cambia y las tablas no salen iguales. Una version por debajo
del minimo es un aviso, no un fallo: puede que ande, pero si el resultado no se reproduce hay que
mirar aca primero.

Uso:
    python experiments/comprobar_entorno.py                # perfil del benchmark (CPU)
    python experiments/comprobar_entorno.py --deteccion    # ademas torch, torchvision y la GPU

Codigo de salida: 0 si se puede correr, 1 si falta algo imprescindible.
"""
import argparse
import importlib
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

# Nombre de distribucion (el de PyPI, el que va en requirements.txt) -> nombre de import.
# Solo los que no coinciden; para el resto se asume que son iguales.
IMPORT_DE = {
    'opencv-python': 'cv2', 'scikit-image': 'skimage', 'pillow': 'PIL',
    'pymupdf': 'fitz', 'pywavelets': 'pywt',
}

# Paquetes declarados que se comprueban por metadatos y no importandolos. Hoy ninguno.
SOLO_METADATOS = set()

fallos = []
avisos = []


def ok(cond, msg, blando=False):
    if cond:
        print(f'  OK    {msg}')
    elif blando:
        print(f'  AVISO {msg}')
        avisos.append(msg)
    else:
        print(f'  FALLA {msg}')
        fallos.append(msg)
    return bool(cond)


def norm(nombre):
    return re.sub(r'[-_.]+', '-', nombre).strip().lower()


def leer_requisitos(archivo):
    """Devuelve [(nombre, minimo_o_None)] de un archivo de requisitos, ignorando comentarios."""
    ruta = RAIZ / archivo
    if not ruta.exists():
        return None
    fuera = []
    for linea in ruta.read_text(encoding='utf-8').splitlines():
        linea = linea.split('#')[0].strip()
        if not linea or linea.startswith('-'):      # -r, --extra-index-url y demas directivas
            continue
        m = re.match(r'^([A-Za-z0-9_.\-]+)\s*(?:>=\s*([0-9][\w.]*))?', linea)
        if m:
            fuera.append((m.group(1), m.group(2)))
    return fuera


def version_instalada(dist, modulo):
    """La version instalada, por metadatos primero (es la fuente autoritativa) y si no por atributo."""
    from importlib.metadata import version as mv, PackageNotFoundError
    try:
        return mv(dist)
    except PackageNotFoundError:
        pass
    try:
        m = importlib.import_module(modulo)
    except Exception:
        return None
    v = getattr(m, '__version__', None)
    return v if isinstance(v, str) else None


def tupla(v):
    """'1.26.4' -> (1, 26, 4). Corta en el primer trozo no numerico: '2.5.1+cu121' -> (2, 5, 1)."""
    partes = []
    for t in re.split(r'[.\-+]', v or ''):
        if not t.isdigit():
            break
        partes.append(int(t))
    return tuple(partes)


def comprobar_paquetes(archivo, etiqueta):
    reqs = leer_requisitos(archivo)
    print(f'\n=== paquetes: {etiqueta} ({archivo}) ===')
    if reqs is None:
        ok(False, f'no existe {archivo}: el clon esta incompleto')
        return []
    ausentes = []
    for dist, minimo in reqs:
        clave = norm(dist)
        modulo = IMPORT_DE.get(clave, clave.replace('-', '_'))
        v = version_instalada(dist, modulo)
        importa = True
        if v is not None and clave not in SOLO_METADATOS:
            try:
                importlib.import_module(modulo)
            except Exception as e:
                importa = False
                ok(False, f'{dist}: instalado ({v}) pero no importa — {type(e).__name__}: {e}')
                ausentes.append(dist)
        if v is None:
            ok(False, f'{dist}: NO ESTA INSTALADO')
            ausentes.append(dist)
        elif importa:
            if minimo and tupla(v) and tupla(v) < tupla(minimo):
                ok(False, f'{dist} {v} esta por debajo del minimo declarado ({minimo}): '
                          f'puede andar, pero las tablas pueden no reproducirse', blando=True)
            else:
                ok(True, f'{dist} {v}')
    return ausentes


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--deteccion', action='store_true',
                    help='comprueba tambien el perfil de GPU (torch, torchvision, ultralytics)')
    args = ap.parse_args()

    print('=== interprete ===')
    v = sys.version_info
    ok(v >= (3, 11), f'Python {v.major}.{v.minor}.{v.micro} '
                     f'({"cumple el minimo 3.11" if v >= (3, 11) else "SE PIDE 3.11 o superior"})')
    # Que sea el del entorno virtual no es obligatorio, pero correr con el python del sistema es la
    # causa mas comun de «el paquete esta instalado y no lo encuentra»: estan en entornos distintos.
    en_venv = sys.prefix != getattr(sys, 'base_prefix', sys.prefix)
    ok(en_venv, f'interprete: {sys.executable}'
                + ('' if en_venv else ' — NO es un entorno virtual; si faltan paquetes, '
                                     'probablemente esten instalados en otro interprete'),
       blando=True)

    ausentes = comprobar_paquetes('requirements.txt', 'benchmark de calidad (CPU)')
    ausentes_gpu = []
    if args.deteccion:
        ausentes_gpu = comprobar_paquetes('requirements-deteccion.txt', 'deteccion (GPU)')
        print('\n=== GPU ===')
        try:
            import torch
            hay = torch.cuda.is_available()
            ok(hay, f'torch {torch.__version__}, CUDA disponible: {hay}'
                    + ('' if hay else ' — el entrenamiento en CPU es inviable en la practica. '
                                      'Si la maquina tiene GPU, la rueda instalada es la de CPU: '
                                      'ver reparar_torch_gpu.ps1'),
               blando=True)
            if hay:
                ok(True, f'GPU: {torch.cuda.get_device_name(0)}')
        except ImportError:
            ok(False, 'torch no esta instalado: no se puede comprobar la GPU')

    print('\n=== corpus ===')
    # Comprobacion barata: que este el directorio y tenga algo. La de verdad —los 42 md5, los 20
    # pares, el canal duplicado— la hace verificar_corpus.py, que se corre despues.
    raw = RAIZ / 'data' / 'raw'
    n = len(list((raw / 'VIS').glob('*'))) + len(list((raw / 'IR').glob('*'))) \
        if (raw / 'VIS').exists() and (raw / 'IR').exists() else 0
    ok(n > 0, f'data/raw tiene {n} imagenes'
              + ('' if n else ' — falta armarlo: python experiments/preparar_corpus.py '
                              '--tno "RUTA/AL/TNO_Image_Fusion_Dataset"'))

    print(f'\n=== {len(fallos)} fallos, {len(avisos)} avisos ===')
    for f in fallos:
        print(f'  FALLA {f}')
    if ausentes or ausentes_gpu:
        print('\nPara instalar lo que falta:')
        if ausentes:
            print('    pip install -r requirements.txt')
        if ausentes_gpu:
            print('    pip install torch==2.5.1 torchvision==0.20.1 '
                  '--index-url https://download.pytorch.org/whl/cu121\n'
                  '    pip install -r requirements-deteccion.txt')
    if not fallos:
        print('  el entorno esta listo')
    return 1 if fallos else 0


if __name__ == '__main__':
    sys.exit(main())
