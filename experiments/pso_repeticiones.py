# -*- coding: utf-8 -*-
"""Estabilidad del barrido PSO: 20 repeticiones independientes de cada configuracion.

Pedido del orientador: llevar el barrido de 25 a 500 corridas repitiendo veinte veces cada
una de las 25 configuraciones de enjambre, y analizar la dispersion de los resultados.

Por que hace falta un script aparte, y no basta con volver a correr el barrido: la aptitud
es DETERMINISTA y en pso_grid_search_fo.py las semillas estan fijadas por la configuracion
—init_swarm(n, seed=1000n+T)— y por el numero de iteracion —default_rng(7000+t) y
default_rng(9000+t) para los coeficientes r1 y r2—. Con eso, repetir una configuracion
devuelve el mismo resultado bit a bit y el estudio no mediria nada. Aca la semilla es
funcion de (n, T, repeticion), de modo que cada repeticion es una corrida genuinamente
distinta. La repeticion 0 reproduce EXACTAMENTE el barrido publicado, y el script lo
comprueba contra su CSV: es la garantia de que no se cambio nada mas que la semilla.

La otra diferencia es de costo. La parte morfologica de la fusion depende solo del radio y
no del peso, de modo que se cachea por r: cada evaluacion queda en aritmetica mas metricas.
Verificado bit a bit contra fuse_optimal (diferencia 0,000e+00 en los doce puntos de
prueba), rinde 9,2x y baja las 90.000 evaluaciones de ~20 h a ~2 h.

Uso:
  .venv\\Scripts\\python.exe -X utf8 experiments/pso_repeticiones.py --operator propuesta
  ... --repeticiones 20 --rep-desde 0 --rep-hasta 0     (solo valida contra lo publicado)
  ... --budget 3600                                      (reanudable por presupuesto)

Salida: experiments/results/metrics_reports/pso_repeticiones_<operador>.csv
        experiments/results/pso/pso_repeticiones_<operador>_state.json
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, '.')
import numpy as np
import pandas as pd

from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import combined_top_hat
from src.fusion.comparatives import tophat_classic_fusion
import experiments.pso_grid_search_fo as G

RAIZ = Path(__file__).resolve().parent.parent
MR = RAIZ / 'experiments' / 'results' / 'metrics_reports'
PSO = RAIZ / 'experiments' / 'results' / 'pso'
PARTICULAS, ITERACIONES = G.PARTICULAS, G.ITERACIONES
W_MAX, W_MIN, C1, C2 = G.W_MAX, G.W_MIN, G.C1, G.C2
DESPLAZAMIENTO = 100_000        # separa los flujos de semillas de cada repeticion


# --------------------------------------------------------------- escenas y cache por radio
def escenas():
    """Las mismas tres escenas del barrido publicado: list_pairs()[::7]."""
    fuera = []
    for p in list_pairs()[::7]:
        v, i = load_pair(*p)
        mu_v, mu_i = G._gb(v), G._gb(i)
        fuera.append(dict(
            nombre=p[0].stem, v=v, i=i, mu_v=mu_v, mu_i=mu_i,
            var_v=G._gb(v * v) - mu_v * mu_v, var_i=G._gb(i * i) - mu_i * mu_i,
            base=0.5 * (v.astype(np.float32) + i.astype(np.float32))))
    return fuera


def hacer_fitness(operador, ESC):
    """F_o promediada sobre las escenas, con la morfologia cacheada por radio.

    El cache es perezoso: el enjambre visita pocos radios, de modo que precalcular los 25
    costaria mas que calcular los que se usan.
    """
    porr = {}

    def piezas(r):
        if r not in porr:
            fuera = []
            for c in ESC:
                if operador == 'propuesta':
                    wv, bv = combined_top_hat(c['v'], r, 'sum')
                    wi, bi = combined_top_hat(c['i'], r, 'sum')
                else:
                    # el clasico usa disco unico; se obtiene su respuesta por diferencia
                    # contra la fusion completa para no duplicar su implementacion
                    f1 = tophat_classic_fusion(c['v'], c['i'], r=r, m=1.0)
                    f0 = tophat_classic_fusion(c['v'], c['i'], r=r, m=0.0)
                    fuera.append((f0, (f1 - f0).astype(np.float32), None))
                    continue
                fuera.append((c['base'], np.maximum(wv, wi), np.maximum(bv, bi)))
            porr[r] = fuera
        return porr[r]

    def fitness(x):
        r = int(round(np.clip(x[0], G.LO[0], G.HI[0])))
        m = float(np.clip(x[1], G.LO[1], G.HI[1]))
        acc = 0.0
        for c, pz in zip(ESC, piezas(r)):
            if pz[2] is None:                       # camino del clasico
                f = np.clip(pz[0] + m * pz[1], 0.0, 1.0).astype(np.float32)
            else:
                base, wmax, bmax = pz
                f = np.clip(base + m * wmax - m * bmax, 0.0, 1.0).astype(np.float32)
            # mu_f y var_f no dependen de la fuente: se calculan una vez por escena
            mu_f = G._gb(f)
            var_f = G._gb(f * f) - mu_f * mu_f
            ssim = 0.5 * (_ssim(f, c['v'], c['mu_v'], c['var_v'], mu_f, var_f)
                          + _ssim(f, c['i'], c['mu_i'], c['var_i'], mu_f, var_f))
            acc += ssim + G._entropia8(f) + G._psnr_n(f, c['v'], c['i'])
        return acc / len(ESC)

    return fitness, porr


def _ssim(f, x, mu_x, var_x, mu_f, var_f):
    C1s, C2s = 0.01 ** 2, 0.03 ** 2
    cov = G._gb(f * x) - mu_f * mu_x
    s = ((2 * mu_f * mu_x + C1s) * (2 * cov + C2s)) / (
        (mu_f * mu_f + mu_x * mu_x + C1s) * (var_f + var_x + C2s) + 1e-12)
    return float(s.mean())


# ------------------------------------------------------------------------ una corrida PSO
def corrida(fitness, n, T, rep):
    """Replica exactamente el PSO del barrido publicado, con la semilla desplazada."""
    d = DESPLAZAMIENTO * rep
    rng = np.random.default_rng(1000 * n + T + d)
    X = rng.uniform(G.LO, G.HI, (n, 2))
    V = rng.uniform(-0.3, 0.3, (n, 2))
    pb, pbf = X.copy(), np.full(n, -1e9)
    gb, gbf, evals = np.array([3.0, 1.0]), -1e9, 0
    for t in range(T):
        for i in range(n):
            fv = fitness(X[i]); evals += 1
            if fv > pbf[i]:
                pbf[i], pb[i] = fv, X[i].copy()
            if fv > gbf:
                gbf, gb = fv, X[i].copy()
        rng1 = np.random.default_rng(7000 + t + d)
        rng2 = np.random.default_rng(9000 + t + d)
        w = W_MAX - (W_MAX - W_MIN) * t / max(1, T - 1)
        V = w * V + C1 * rng1.uniform(0, 1, (n, 2)) * (pb - X) \
            + C2 * rng2.uniform(0, 1, (n, 2)) * (gb - X)
        X = np.clip(X + V, G.LO, G.HI)
    return int(round(gb[0])), float(gb[1]), float(gbf), evals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--operator', choices=['propuesta', 'clasico'], default='propuesta')
    ap.add_argument('--repeticiones', type=int, default=20)
    ap.add_argument('--rep-desde', type=int, default=0)
    ap.add_argument('--rep-hasta', type=int, default=None)
    ap.add_argument('--budget', type=float, default=1e9, help='segundos antes de guardar y salir')
    # El rango de m se puede abrir para contestar una pregunta distinta: si el intervalo
    # heredado no fuera la restriccion, adonde iria la busqueda. El maximo de Fo sin
    # restringir esta en m ~ 0,07, fuera del rango publicado, de modo que con el piso en 0,01
    # el optimo pasa a ser INTERIOR y la dispersion mide otra cosa.
    ap.add_argument('--m-lo', type=float, default=None, help='piso de m (por omision, 0,30)')
    ap.add_argument('--m-hi', type=float, default=None, help='techo de m (por omision, 2,00)')
    ap.add_argument('--tag', default='', help='sufijo de la salida, para no pisar el barrido oficial')
    a = ap.parse_args()
    hasta = a.repeticiones - 1 if a.rep_hasta is None else a.rep_hasta
    if a.m_lo is not None or a.m_hi is not None:
        G.LO = np.array([1.0, a.m_lo if a.m_lo is not None else float(G.LO[1])])
        G.HI = np.array([25.0, a.m_hi if a.m_hi is not None else float(G.HI[1])])
    print(f'rango de busqueda: r en [{G.LO[0]:.0f}, {G.HI[0]:.0f}] · '
          f'm en [{G.LO[1]:.2f}, {G.HI[1]:.2f}]')

    ESC = escenas()
    fitness, porr = hacer_fitness(a.operator, ESC)
    huella = hashlib.sha256(json.dumps(
        {'escenas': [c['nombre'] for c in ESC], 'operador': a.operator,
         'lo': list(map(float, G.LO)), 'hi': list(map(float, G.HI))},
        sort_keys=True).encode()).hexdigest()[:16]
    print(f'escenas: {", ".join(c["nombre"] for c in ESC)}')
    print(f'huella:  {huella}')
    print(f'plan:    {len(PARTICULAS) * len(ITERACIONES)} configuraciones x '
          f'{a.repeticiones} repeticiones = {len(PARTICULAS) * len(ITERACIONES) * a.repeticiones} corridas')

    # el sufijo separa las salidas: sin el, correr con otro rango descartaria el estado
    # del barrido oficial, porque la huella incluye los limites de m
    suf = a.operator + (f'_{a.tag}' if a.tag else '')
    EST = PSO / f'pso_repeticiones_{suf}_state.json'
    s = json.loads(EST.read_text()) if EST.exists() else {}
    if s.get('huella') != huella:
        if s.get('filas'):
            print('AVISO: las condiciones cambiaron; se descarta el estado y se recalcula.')
        s = {'huella': huella, 'filas': {}}

    t0 = time.time()
    for rep in range(a.rep_desde, hasta + 1):
        for n in PARTICULAS:
            for T in ITERACIONES:
                clave = f'r{rep}_n{n}_T{T}'
                if clave in s['filas']:
                    continue
                if time.time() - t0 > a.budget:
                    EST.parent.mkdir(parents=True, exist_ok=True)
                    EST.write_text(json.dumps(s))
                    print(f'[ckpt] {len(s["filas"])} corridas hechas; falta seguir')
                    return 0
                tc = time.time()
                r_opt, m_opt, fo, ev = corrida(fitness, n, T, rep)
                s['filas'][clave] = {'repeticion': rep, 'n': n, 'Tmax': T, 'evaluaciones': ev,
                                     'r_opt': r_opt, 'm_opt': round(m_opt, 6),
                                     'Fo_opt': round(fo, 6), 'segundos': round(time.time() - tc, 1)}
                print(f'[OK] rep {rep:2d} n{n:2d} T{T:2d} | r*={r_opt:2d} m*={m_opt:.4f} '
                      f'Fo*={fo:.4f} | {len(s["filas"])}/'
                      f'{len(PARTICULAS) * len(ITERACIONES) * a.repeticiones} '
                      f'({time.time() - tc:.0f} s, radios en cache: {len(porr)})', flush=True)
        EST.parent.mkdir(parents=True, exist_ok=True)
        EST.write_text(json.dumps(s))

    tabla = pd.DataFrame(sorted(s['filas'].values(),
                                key=lambda d: (d['repeticion'], d['n'], d['Tmax'])))
    tabla.insert(0, 'operador', a.operator)
    salida = MR / f'pso_repeticiones_{suf}.csv'
    tabla.to_csv(salida, index=False)

    # --- la repeticion 0 tiene que reproducir el barrido publicado, o algo cambio
    pub = MR / f'pso_grid_search_fo_{a.operator}.csv'
    rango_oficial = (abs(float(G.LO[1]) - 0.30) < 1e-9 and abs(float(G.HI[1]) - 2.00) < 1e-9)
    if pub.exists() and 0 in set(tabla.repeticion) and rango_oficial:
        p = pd.read_csv(pub).rename(columns={'Fo_opt': 'Fo_pub', 'r_opt': 'r_pub',
                                             'm_opt': 'm_pub'})
        z = tabla[tabla.repeticion == 0].merge(p[['n', 'Tmax', 'r_pub', 'm_pub', 'Fo_pub']],
                                              on=['n', 'Tmax'])
        mal = z[(z.r_opt != z.r_pub) | ((z.m_opt - z.m_pub).abs() > 5e-4)
                | ((z.Fo_opt - z.Fo_pub).abs() > 5e-4)]
        if len(mal):
            print('\nFALLA: la repeticion 0 no reproduce el barrido publicado:')
            print(mal[['n', 'Tmax', 'r_opt', 'r_pub', 'm_opt', 'm_pub', 'Fo_opt', 'Fo_pub']]
                  .to_string(index=False))
            return 1
        print(f'\nla repeticion 0 reproduce las {len(z)} celdas del barrido publicado')

    print(f'{len(tabla)} corridas -> {salida.relative_to(RAIZ)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
