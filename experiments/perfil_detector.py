# -*- coding: utf-8 -*-
"""Perfila el detector usado en las dos pruebas y deja los datos en un JSON.

Motivo: el informe describe la arquitectura, el entorno y el protocolo de entrenamiento de
YOLOv8n. Esas cifras no se citan de la documentacion de la biblioteca —que puede no
corresponder a la version instalada ni a los pesos realmente entrenados— sino que se miden
sobre los checkpoints de este trabajo y se leen de los args.yaml de cada corrida.

Salida: experiments/results/metrics_reports/detector_perfil.json
Uso:    .venv\\Scripts\\python.exe -X utf8 experiments/perfil_detector.py
"""
import glob
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')
RAIZ = Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
sys.path.insert(0, '.')
SALIDA = RAIZ / 'experiments' / 'results' / 'metrics_reports' / 'detector_perfil.json'

PESOS_M3FD = 'runs/**/mixto/weights/best.pt'
PESOS_LLVIP = 'runs/**/llvip/Propuesta_Novedosa/weights/last.pt'
ARGS_M3FD = 'runs/**/m3fd/mixto/args.yaml'
ARGS_LLVIP = 'runs/**/llvip/Propuesta_Novedosa/args.yaml'
# los hiperparametros que el informe publica, con su etiqueta en castellano
HIPER = [
    ('model', 'Pesos iniciales'), ('epochs', 'Épocas'), ('batch', 'Lote'),
    ('imgsz', 'Resolución de entrada'), ('optimizer', 'Optimizador'),
    ('lr0', 'Tasa de aprendizaje inicial'), ('lrf', 'Factor final de la tasa'),
    ('momentum', 'Momento'), ('weight_decay', 'Decaimiento de pesos'),
    ('warmup_epochs', 'Épocas de calentamiento'), ('iou', 'IoU de la supresión no máxima'),
    ('max_det', 'Detecciones máximas por imagen'), ('seed', 'Semilla'),
    ('deterministic', 'Determinista'), ('amp', 'Precisión mixta'),
    ('close_mosaic', 'Épocas finales sin mosaico'),
    ('hsv_h', 'Aumento: tono'), ('hsv_s', 'Aumento: saturación'),
    ('hsv_v', 'Aumento: brillo'), ('translate', 'Aumento: traslación'),
    ('scale', 'Aumento: escala'), ('fliplr', 'Aumento: espejado horizontal'),
    ('mosaic', 'Aumento: mosaico'), ('erasing', 'Aumento: borrado aleatorio'),
]


def ultimo(patron):
    c = sorted(glob.glob(patron, recursive=True), key=os.path.getmtime)
    return c[-1] if c else None


def contar_imagenes(carpeta):
    p = RAIZ / 'datasets' / carpeta / 'images'
    if not p.is_dir():
        return {}
    return {s.name: len(list(s.glob('*'))) for s in sorted(p.iterdir()) if s.is_dir()}


def main():
    import torch
    import ultralytics
    import yaml
    from ultralytics import YOLO
    from ultralytics.utils.torch_utils import get_flops

    d = {'entorno': {
        'ultralytics': ultralytics.__version__,
        'torch': torch.__version__,
        'cuda': bool(torch.cuda.is_available()),
        'gpu': torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
    }, 'modelos': {}, 'hiperparametros': {}, 'datos': {}}

    for nombre, patron in (('m3fd', PESOS_M3FD), ('llvip', PESOS_LLVIP)):
        ruta = ultimo(patron)
        if not ruta:
            print(f'  falta el checkpoint de {nombre} ({patron})')
            continue
        m = YOLO(ruta)
        tipos = {}
        for mod in m.model.modules():
            tipos[type(mod).__name__] = tipos.get(type(mod).__name__, 0) + 1
        d['modelos'][nombre] = {
            'checkpoint': os.path.relpath(ruta, RAIZ).replace('\\', '/'),
            'parametros': int(sum(x.numel() for x in m.model.parameters())),
            'modulos': len(list(m.model.modules())),
            'clases': list(m.model.names.values()),
            'gflops': round(float(get_flops(m.model, 640)), 2),
            'bloques': {k: tipos.get(k, 0) for k in
                        ('Conv', 'C2f', 'Bottleneck', 'SPPF', 'Concat', 'Upsample',
                         'Detect', 'DFL')},
        }
        print(f'  {nombre:6s} {d["modelos"][nombre]["parametros"]:,} parametros · '
              f'{d["modelos"][nombre]["gflops"]} GFLOPs · '
              f'{len(d["modelos"][nombre]["clases"])} clases')

    for nombre, patron in (('m3fd', ARGS_M3FD), ('llvip', ARGS_LLVIP)):
        ruta = ultimo(patron)
        if not ruta:
            continue
        a = yaml.safe_load(open(ruta, encoding='utf-8'))
        d['hiperparametros'][nombre] = {k: a.get(k) for k, _ in HIPER}
        d['hiperparametros'][nombre]['patience'] = a.get('patience')
    d['etiquetas_hiper'] = dict(HIPER)

    for carpeta in ('llvip_Propuesta_Novedosa', 'm3fd_mixto',
                    'm3fd_test_Propuesta_Novedosa', 'm3fd_comp_Propuesta_Novedosa'):
        d['datos'][carpeta] = contar_imagenes(carpeta)

    # cuantas corridas de entrenamiento hay por prueba
    d['entrenamientos'] = {
        'llvip': sorted(p.name for p in Path('runs/detect/runs/llvip').iterdir()
                        if (p / 'weights').is_dir()) if Path('runs/detect/runs/llvip').is_dir() else [],
        'm3fd': sorted(p.name for p in Path('runs/detect/runs/m3fd').iterdir()
                       if (p / 'weights').is_dir()) if Path('runs/detect/runs/m3fd').is_dir() else [],
    }

    # las dos configuraciones tienen que coincidir en todo lo que el informe declara comun
    comunes = ('epochs', 'batch', 'imgsz', 'lr0', 'momentum', 'weight_decay', 'seed',
               'deterministic', 'iou', 'max_det', 'mosaic', 'fliplr')
    if len(d['hiperparametros']) == 2:
        a, b = d['hiperparametros']['m3fd'], d['hiperparametros']['llvip']
        distintos = [k for k in comunes if a.get(k) != b.get(k)]
        assert not distintos, f'las dos pruebas difieren en {distintos}, y el informe las declara iguales'
        print('  las dos configuraciones coinciden en los hiperparametros declarados comunes')

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'-> {SALIDA.relative_to(RAIZ)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
