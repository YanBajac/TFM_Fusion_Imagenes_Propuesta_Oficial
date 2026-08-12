# -*- coding: utf-8 -*-
"""Repite el entrenamiento de LLVIP con varias semillas, para poder decir algo del ORDEN entre fusiones.

POR QUE EXISTE. Los dos experimentos de deteccion del trabajo usan UNA SOLA SEMILLA por entrada. El
informe lo declara dos veces y con razon: las siete fusiones se apilan en centesimas y la menor
distancia entre dos consecutivas es 0,0001, de modo que sin repeticiones no se puede separar el orden
entre ellas del ruido de inicializacion. Declararlo es honesto, pero no vuelve defendible el orden. La
unica brecha que hoy sobrevive a cualquier semilla es la que hay contra el visible solo, de 0,092
puntos de mAP. Este script produce las repeticiones que faltan.

POR QUE NO SIRVE train_eval_llvip.py CON --seed. Dos cosas lo impiden, y las dos silenciosamente:
  1. entrena con project='runs/llvip', name=<metodo>, exist_ok=True, asi que una segunda semilla
     SOBREESCRIBE los pesos de la primera;
  2. escribe en detection_llvip_map.csv, que esta indexado por metodo y reemplaza la fila anterior,
     de modo que el resultado de la semilla previa se PIERDE.
Aca cada corrida va a runs/**/llvip_semillas/<metodo>_s<semilla> y cada resultado es una fila
(metodo, semilla) en su propio CSV.

UNA CORRIDA POR SUBPROCESO, y esto no es un detalle. La primera version entrenaba todas las corridas
dentro de un mismo proceso de Python y murio en la corrida 11 con «CUDA error: out of memory» sobre una
placa de 6 GB que estaba vacia: PyTorch no devuelve al sistema la memoria de su asignador entre
entrenamientos sucesivos, y la fragmentacion se acumula. Con un subproceso por corrida el sistema
operativo reclama toda la VRAM al terminar cada una. El padre solo reparte trabajo; el hijo entrena una
sola y sale. Ademas, si una corrida falla, el padre lo anota y sigue con la siguiente en lugar de
llevarse el lote entero.

LA SEMILLA 0 NO SE REENTRENA. Sus pesos ya estan en disco de la corrida publicada, con la misma
configuracion y el mismo protocolo de checkpoint (last.pt, sin seleccion sobre el val). Se los evalua
con este mismo codigo para que la medicion de las cinco semillas salga del mismo camino. Se comprobo
que reproducen los mAP publicados exactamente, de modo que reusarlos es legitimo.

ES REANUDABLE. Antes de cada corrida se mira si el par (metodo, semilla) ya esta en el CSV y se lo
saltea; y antes de entrenar se mira si los pesos ya estan en disco y se los reusa. El CSV se reescribe
DESPUES DE CADA CORRIDA: si esto se corta en la corrida 30, se conservan 29 y se retoma donde quedo.

Salida: experiments/results/metrics_reports/detection_llvip_semillas.csv
Uso:
  .venv\\Scripts\\python.exe -X utf8 experiments/detection_llvip/run_semillas_llvip.py
  ... --semillas 0,1,2,3,4      (por defecto; 0 solo se evalua, 1 a 4 se entrenan)
  ... --max-corridas 1          (piloto)
  ... --un-proceso              (uso interno: hace UNA corrida sin lanzar subprocesos)
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

SALIDA = RAIZ / 'experiments' / 'results' / 'metrics_reports' / 'detection_llvip_semillas.csv'
METODOS = ['VIS', 'IR', 'PiramideLaplace', 'RatioPiramide', 'DWT', 'DTCWT', 'Curvelet',
           'TopHat_Clasico', 'Propuesta_Novedosa']


def pesos_semilla_cero(metodo):
    """Los pesos de la corrida publicada, que es la semilla 0."""
    c = sorted(RAIZ.glob(f'runs/**/llvip/{metodo}/weights/last.pt'), key=lambda p: p.stat().st_mtime)
    return c[-1] if c else None


def pesos_existentes(metodo, semilla, epocas):
    """Pesos de este par SOLO SI el entrenamiento se completo. Si no, None.

    Se busca con glob y no con una ruta armada: ultralytics resuelve «project» bajo su
    settings.runs_dir y el nivel intermedio depende de esa configuracion. Armar la ruta a mano hizo
    que una version anterior descartara un entrenamiento completo con un «no aparecio; salto».

    Y SE EXIGE QUE ESTE COMPLETO, que es lo que faltaba. Ultralytics escribe last.pt en cada epoca,
    de modo que un entrenamiento interrumpido deja pesos que parecen validos: reusarlos registraria
    como corrida un modelo entrenado a medias. Paso de verdad —una corrida quedo en 18 epocas de 40
    al matarla un timeout— y el lote la habria tomado por buena. results.csv lleva una fila por epoca
    terminada, asi que contar sus filas dice si la corrida llego al final.
    """
    for w in sorted(RAIZ.glob(f'runs/**/llvip_semillas/{metodo}_s{semilla}/weights/last.pt'),
                    key=lambda p: p.stat().st_mtime, reverse=True):
        res = w.parent.parent / 'results.csv'
        if not res.exists():
            continue
        hechas = sum(1 for _ in res.open(encoding='utf-8', errors='replace')) - 1
        if hechas >= epocas:
            return w
        print(f'  [PARCIAL] {w.parent.parent.name} tiene {hechas} de {epocas} epocas: '
              f'no se reusa, se reentrena')
    return None


def leer_hechas():
    import pandas as pd
    if not SALIDA.exists():
        return set(), []
    prev = pd.read_csv(SALIDA)
    return ({(r.method, int(r.semilla)) for r in prev.itertuples()}, prev.to_dict('records'))


def una_corrida(m, s, a):
    """Entrena (o evalua) UN par (metodo, semilla) y agrega su fila al CSV. Corre en su propio proceso."""
    import pandas as pd
    import torch
    from ultralytics import YOLO

    data = RAIZ / 'datasets' / f'llvip_{m}' / 'data.yaml'
    if not data.exists():
        print(f'[AVISO] falta {data}; no se puede correr {m}')
        return 1
    t1 = time.time()
    if s == 0:
        w = pesos_semilla_cero(m)
        if w is None:
            print(f'[AVISO] no estan los pesos de la corrida publicada de {m}')
            return 1
        entrenada = False
    else:
        w = pesos_existentes(m, s, a.epochs)
        if w is not None:
            print(f'  ya hay pesos entrenados: se reusan sin reentrenar')
        else:
            torch.cuda.empty_cache()
            model = YOLO(a.model)
            model.train(data=str(data), epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
                        seed=s, deterministic=True, project='runs/llvip_semillas',
                        name=f'{m}_s{s}', exist_ok=True, verbose=False, plots=False,
                        device=a.device)
            sd = Path(getattr(model.trainer, 'save_dir', '')) if model.trainer else None
            w = (sd / 'weights' / 'last.pt') if sd else None
            if w is None or not w.exists():
                w = pesos_existentes(m, s, a.epochs)
            if w is None:
                print(f'[AVISO] no se encontraron los pesos de {m} s{s} tras entrenar')
                return 1
            del model
            torch.cuda.empty_cache()
        entrenada = True

    met = YOLO(str(w)).val(data=str(data), split='val', verbose=False, device=a.device)
    fila = {'method': m, 'semilla': s,
            'mAP50': round(float(met.box.map50), 4),
            'mAP50_95': round(float(met.box.map), 4),
            'precision': round(float(met.box.mp), 4),
            'recall': round(float(met.box.mr), 4),
            'checkpoint': 'last', 'entrenada_aqui': entrenada,
            'segundos': round(time.time() - t1, 1)}
    _hechas, filas = leer_hechas()
    filas = [f for f in filas if not (f['method'] == m and int(f['semilla']) == s)] + [fila]
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(filas).sort_values(['method', 'semilla']).to_csv(SALIDA, index=False)
    print(f'  mAP50={fila["mAP50"]:.4f}  mAP50-95={fila["mAP50_95"]:.4f}  '
          f'[{fila["segundos"] / 60:.1f} min]', flush=True)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--semillas', default='0,1,2,3,4')
    ap.add_argument('--metodos', default=','.join(METODOS))
    ap.add_argument('--model', default='yolov8n.pt')
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--imgsz', type=int, default=640)
    ap.add_argument('--batch', type=int, default=16)
    ap.add_argument('--device', default='0')
    ap.add_argument('--max-corridas', type=int, default=0, help='0 = sin limite')
    ap.add_argument('--un-proceso', action='store_true',
                    help='uso interno: hace UNA corrida en este mismo proceso')
    a = ap.parse_args()

    semillas = [int(x) for x in a.semillas.split(',') if x.strip() != '']
    metodos = [x.strip() for x in a.metodos.split(',') if x.strip()]

    if a.un_proceso:
        if len(semillas) != 1 or len(metodos) != 1:
            print('--un-proceso necesita exactamente un metodo y una semilla')
            return 2
        return una_corrida(metodos[0], semillas[0], a)

    import pandas as pd
    hechas, _filas = leer_hechas()
    if hechas:
        print(f'--- retomando: {len(hechas)} corridas ya en {SALIDA.name}')
    pendientes = [(m, s) for s in semillas for m in metodos if (m, s) not in hechas]
    if a.max_corridas:
        pendientes = pendientes[:a.max_corridas]
    n_entrena = sum(1 for m, s in pendientes
                    if s != 0 and pesos_existentes(m, s, a.epochs) is None)
    print(f'--- {len(pendientes)} corridas pendientes ({n_entrena} entrenan de cero)')
    print(f'--- una corrida por subproceso, para que la VRAM se libere entre una y otra')

    t0, fallidas = time.time(), []
    for i, (m, s) in enumerate(pendientes, 1):
        print(f'\n===== [{i}/{len(pendientes)}] {m}  semilla {s} =====', flush=True)
        cmd = [sys.executable, '-X', 'utf8', str(Path(__file__).resolve()),
               '--un-proceso', '--metodos', m, '--semillas', str(s),
               '--model', a.model, '--epochs', str(a.epochs), '--imgsz', str(a.imgsz),
               '--batch', str(a.batch), '--device', a.device]
        r = subprocess.run(cmd, cwd=str(RAIZ))
        if r.returncode != 0:
            print(f'  [FALLO] {m} s{s} termino con codigo {r.returncode}; se sigue con la siguiente')
            fallidas.append((m, s, r.returncode))
        transcurrido = time.time() - t0
        resta = (transcurrido / i) * (len(pendientes) - i)
        print(f'  ({i} de {len(pendientes)} · faltan {len(pendientes) - i} · '
              f'~{resta / 3600:.1f} h)', flush=True)

    hechas, filas = leer_hechas()
    d = pd.DataFrame(filas)
    if not len(d):
        print('\n===== ninguna corrida completada =====')
        return 1
    print(f'\n===== {len(d)} corridas en el CSV, {d.semilla.nunique()} semillas =====')
    if fallidas:
        print(f'  {len(fallidas)} fallidas: {fallidas}')
    if d.semilla.nunique() > 1:
        r = d.groupby('method').agg(
            n=('mAP50', 'size'), mAP50_media=('mAP50', 'mean'), mAP50_desv=('mAP50', 'std'),
            mAP50_min=('mAP50', 'min'), mAP50_max=('mAP50', 'max')).round(4)
        print(r.sort_values('mAP50_media', ascending=False).to_string())
    print(f'\nGuardado: {SALIDA}')
    return 1 if fallidas else 0


if __name__ == '__main__':
    sys.exit(main())
