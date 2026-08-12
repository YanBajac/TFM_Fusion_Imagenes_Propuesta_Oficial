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
Aca cada corrida va a runs/llvip_semillas/<metodo>_s<semilla> y cada resultado es una fila (metodo,
semilla) en su propio CSV.

LA SEMILLA 0 NO SE REENTRENA. Sus pesos ya estan en disco de la corrida publicada, con la misma
configuracion y el mismo protocolo de checkpoint (last.pt, sin seleccion sobre el val). Se los evalua
con este mismo codigo para que la medicion de las cinco semillas salga del mismo camino, pero
entrenarla de nuevo seria gastar una hora de GPU en reproducir un numero que ya esta.

ES REANUDABLE. Antes de cada corrida se mira si el par (metodo, semilla) ya esta en el CSV y se lo
saltea. El CSV se reescribe DESPUES DE CADA CORRIDA, no al final: si esto se corta a la corrida 30, se
conservan 29 y se retoma donde quedo.

Salida: experiments/results/metrics_reports/detection_llvip_semillas.csv
Uso:
  .venv\\Scripts\\python.exe -X utf8 experiments/detection_llvip/run_semillas_llvip.py --semillas 1
  ... --semillas 0,1,2,3,4            (0 solo se evalua; 1 a 4 se entrenan)
  ... --max-corridas 1                (piloto: una sola, para medir cuanto tarda)
"""
import argparse
import os
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
    a = ap.parse_args()

    import pandas as pd
    from ultralytics import YOLO

    semillas = [int(x) for x in a.semillas.split(',') if x.strip() != '']
    metodos = [x.strip() for x in a.metodos.split(',') if x.strip()]

    hechas = set()
    if SALIDA.exists():
        prev = pd.read_csv(SALIDA)
        hechas = {(r.method, int(r.semilla)) for r in prev.itertuples()}
        filas = prev.to_dict('records')
        print(f'--- retomando: {len(hechas)} corridas ya en {SALIDA.name}')
    else:
        filas = []

    pendientes = [(m, s) for s in semillas for m in metodos if (m, s) not in hechas]
    if a.max_corridas:
        pendientes = pendientes[:a.max_corridas]
    n_entrena = sum(1 for _m, s in pendientes if s != 0)
    print(f'--- {len(pendientes)} corridas pendientes ({n_entrena} entrenan, '
          f'{len(pendientes) - n_entrena} solo evaluan)')

    t0 = time.time()
    for i, (m, s) in enumerate(pendientes, 1):
        data = RAIZ / 'datasets' / f'llvip_{m}' / 'data.yaml'
        if not data.exists():
            print(f'[AVISO] falta {data}; salto {m}')
            continue
        t1 = time.time()
        print(f'\n===== [{i}/{len(pendientes)}] {m}  semilla {s} '
              f'{"(solo evaluacion)" if s == 0 else ""} =====', flush=True)
        if s == 0:
            w = pesos_semilla_cero(m)
            if w is None:
                print(f'[AVISO] no estan los pesos de la corrida publicada de {m}; salto')
                continue
            model = YOLO(str(w))
            entrenada = False
        else:
            model = YOLO(a.model)
            model.train(data=str(data), epochs=a.epochs, imgsz=a.imgsz, batch=a.batch,
                        seed=s, deterministic=True, project='runs/llvip_semillas',
                        name=f'{m}_s{s}', exist_ok=True, verbose=False, plots=False,
                        device=a.device)
            w = RAIZ / 'runs' / 'llvip_semillas' / f'{m}_s{s}' / 'weights' / 'last.pt'
            if not w.exists():
                print(f'[AVISO] no aparecio {w}; salto')
                continue
            model = YOLO(str(w))
            entrenada = True

        met = model.val(data=str(data), split='val', verbose=False, device=a.device)
        seg = time.time() - t1
        filas.append({
            'method': m, 'semilla': s,
            'mAP50': round(float(met.box.map50), 4),
            'mAP50_95': round(float(met.box.map), 4),
            'precision': round(float(met.box.mp), 4),
            'recall': round(float(met.box.mr), 4),
            'checkpoint': 'last', 'entrenada_aqui': entrenada,
            'segundos': round(seg, 1),
        })
        # se escribe DESPUES DE CADA CORRIDA: una caida cuesta una, no las treinta y seis
        SALIDA.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(filas).sort_values(['method', 'semilla']).to_csv(SALIDA, index=False)
        transcurrido = time.time() - t0
        resta = (transcurrido / i) * (len(pendientes) - i)
        print(f'  mAP50={filas[-1]["mAP50"]:.4f}  mAP50-95={filas[-1]["mAP50_95"]:.4f}  '
              f'[{seg / 60:.1f} min]  ·  faltan {len(pendientes) - i}, '
              f'~{resta / 3600:.1f} h', flush=True)

    d = pd.DataFrame(filas)
    print(f'\n===== {len(d)} corridas en total, {d.semilla.nunique()} semillas =====')
    if len(d) and d.semilla.nunique() > 1:
        r = d.groupby('method').agg(
            n=('mAP50', 'size'), mAP50_media=('mAP50', 'mean'), mAP50_desv=('mAP50', 'std'),
            mAP50_min=('mAP50', 'min'), mAP50_max=('mAP50', 'max')).round(4)
        print(r.sort_values('mAP50_media', ascending=False).to_string())
    print(f'\nGuardado: {SALIDA}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
