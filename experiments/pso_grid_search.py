# -*- coding: utf-8 -*-
"""Barrido de configuraciones PSO (replicando el Cuadro 1 de Ortega & Espinoza, FPUNA 2025):
particulas n en {2,4,6,8,10} x iteraciones Tmax en {10,20,30,40,50} = 25 configuraciones.

Cada configuracion optimiza (r, m) de la PROPUESTA (Top-Hat 1 escala, suma de ramas) con la
aptitud orientada a fusion F = SSIM + Qabf + 0.5*SCD - Nabf sobre 3 escenas representativas.
Espacio de busqueda: r en [1, 25] (rango del libro), m en [0.05, 1.20] (ajustado al operador
con suma, que inyecta ~2x mas energia de detalle que el disco unico del libro).

Salida: experiments/results/metrics_reports/pso_grid_search.csv (una fila por configuracion)
        experiments/results/pso/pso_grid_state.json (reanudable)
Uso:    python experiments/pso_grid_search.py --budget 520
"""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
import cv2
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from src.metrics.evaluators import _Q_pair, _corr

STATE = Path('experiments/results/pso/pso_grid_state.json')
OUT_CSV = Path('experiments/results/metrics_reports/pso_grid_search.csv')
LO = np.array([1.0, 0.05]); HI = np.array([25.0, 1.20])
W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5
PARTICULAS = [2, 4, 6, 8, 10]
ITERACIONES = [10, 20, 30, 40, 50]
_cache = None


def _grad_so(p):
    gx = cv2.Sobel(p, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(p, cv2.CV_32F, 0, 1, ksize=3)
    g = np.sqrt(gx * gx + gy * gy)
    a = np.arctan2(gy, gx + 1e-12)
    return g, a


def _gb(x):
    return cv2.GaussianBlur(x, (11, 11), 1.5)


def _ssim_fast(f, x, mu_x, var_x):
    C1s, C2s = 0.01 ** 2, 0.03 ** 2
    mu_f = _gb(f); var_f = _gb(f * f) - mu_f * mu_f
    cov = _gb(f * x) - mu_f * mu_x
    s = ((2 * mu_f * mu_x + C1s) * (2 * cov + C2s)) / (
        (mu_f * mu_f + mu_x * mu_x + C1s) * (var_f + var_x + C2s) + 1e-12)
    return float(s.mean())


def cache():
    global _cache
    if _cache is None:
        allp = list_pairs()
        _cache = []
        for p in allp[::7]:
            v, i = load_pair(*p)
            gA, aA = _grad_so(v); gB, aB = _grad_so(i)
            mu_v = _gb(v); mu_i = _gb(i)
            var_v = _gb(v * v) - mu_v * mu_v; var_i = _gb(i * i) - mu_i * mu_i
            _cache.append(dict(v=v, i=i, gA=gA, aA=aA, gB=gB, aB=aB,
                               mu_v=mu_v, var_v=var_v, mu_i=mu_i, var_i=var_i,
                               wsum=float(np.sum(gA + gB)) + 1e-12))
    return _cache


def fitness(x):
    r = int(round(np.clip(x[0], LO[0], HI[0])))
    m = float(np.clip(x[1], LO[1], HI[1]))
    acc = 0.0
    C = cache()
    for c in C:
        f = fuse_optimal(c['v'], c['i'], r, m, mode="sum")
        gF, aF = _grad_so(f)
        QAF = _Q_pair(c['gA'], c['aA'], gF, aF); QBF = _Q_pair(c['gB'], c['aB'], gF, aF)
        qabf = float(np.sum(QAF * c['gA'] + QBF * c['gB']) / c['wsum'])
        art = ((gF > c['gA']) & (gF > c['gB'])).astype(np.float64)
        nabf = float(np.sum(art * ((1 - QAF) * c['gA'] + (1 - QBF) * c['gB'])) / c['wsum'])
        ssim = 0.5 * (_ssim_fast(f, c['v'], c['mu_v'], c['var_v'])
                      + _ssim_fast(f, c['i'], c['mu_i'], c['var_i']))
        sc = _corr(f - c['i'], c['v']) + _corr(f - c['v'], c['i'])
        acc += ssim + qabf + 0.5 * sc - nabf
    return acc / len(C)


def init_swarm(n, seed):
    rng = np.random.default_rng(seed)
    X = rng.uniform(LO, HI, (n, 2))
    V = rng.uniform(-0.3, 0.3, (n, 2))
    return X, V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=520.0)
    a = ap.parse_args()
    s = json.load(open(STATE)) if STATE.exists() else {"configs": {}}
    t0 = time.time()

    for n in PARTICULAS:
        for T in ITERACIONES:
            key = f"n{n}_T{T}"
            cfg = s["configs"].get(key)
            if cfg and cfg.get("done"):
                continue
            if cfg is None:
                X, V = init_swarm(n, seed=1000 * n + T)
                cfg = {"t": 0, "X": X.tolist(), "V": V.tolist(),
                       "pbest": X.tolist(), "pbest_fit": [-1e9] * n,
                       "gbest": [3.0, 0.5], "gbest_fit": -1e9,
                       "history": [], "evals": 0, "seg": 0.0, "done": False}
                s["configs"][key] = cfg
            X = np.array(cfg["X"]); V = np.array(cfg["V"])
            pb = np.array(cfg["pbest"]); pbf = np.array(cfg["pbest_fit"])
            gb = np.array(cfg["gbest"]); gbf = cfg["gbest_fit"]
            tc0 = time.time() - cfg["seg"]
            while cfg["t"] < T:
                if time.time() - t0 > a.budget:
                    cfg.update(X=X.tolist(), V=V.tolist(), pbest=pb.tolist(),
                               pbest_fit=pbf.tolist(), gbest=gb.tolist(), gbest_fit=gbf,
                               seg=time.time() - tc0)
                    STATE.parent.mkdir(parents=True, exist_ok=True)
                    json.dump(s, open(STATE, "w"))
                    print(f"[ckpt] {key} it {cfg['t']}/{T} | gbest r={gb[0]:.1f} m={gb[1]:.3f} "
                          f"F={gbf:.4f}", flush=True)
                    return
                for i in range(n):
                    fv = fitness(X[i]); cfg["evals"] += 1
                    if fv > pbf[i]:
                        pbf[i] = fv; pb[i] = X[i].copy()
                    if fv > gbf:
                        gbf = fv; gb = X[i].copy()
                rng1 = np.random.default_rng(7000 + cfg["t"])
                rng2 = np.random.default_rng(9000 + cfg["t"])
                w = W_MAX - (W_MAX - W_MIN) * cfg["t"] / max(1, T - 1)
                V = w * V + C1 * rng1.uniform(0, 1, (n, 2)) * (pb - X) \
                    + C2 * rng2.uniform(0, 1, (n, 2)) * (gb - X)
                X = np.clip(X + V, LO, HI)
                cfg["t"] += 1
                cfg["history"].append({"it": cfg["t"], "gbest_fit": gbf,
                                       "r": float(gb[0]), "m": float(gb[1])})
            cfg.update(X=X.tolist(), V=V.tolist(), pbest=pb.tolist(), pbest_fit=pbf.tolist(),
                       gbest=gb.tolist(), gbest_fit=gbf, seg=time.time() - tc0, done=True)
            STATE.parent.mkdir(parents=True, exist_ok=True)
            json.dump(s, open(STATE, "w"))
            print(f"[OK] {key:8s} | r*={int(round(gb[0])):2d} m*={gb[1]:.4f} "
                  f"F*={gbf:.4f} | evals={cfg['evals']} seg={cfg['seg']:.0f}", flush=True)

    # ------- todas completas: exportar CSV -------
    rows = ["n,Tmax,evaluaciones,r_opt,m_opt,F_opt,segundos"]
    for n in PARTICULAS:
        for T in ITERACIONES:
            c = s["configs"][f"n{n}_T{T}"]
            rows.append(f"{n},{T},{c['evals']},{int(round(c['gbest'][0]))},"
                        f"{c['gbest'][1]:.4f},{c['gbest_fit']:.4f},{c['seg']:.0f}")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.write_text("\n".join(rows), encoding="utf-8")
    best = max(s["configs"].items(), key=lambda kv: kv[1]["gbest_fit"])
    print("\nBARRIDO COMPLETO ->", OUT_CSV)
    print(f"Mejor configuracion: {best[0]} | r*={int(round(best[1]['gbest'][0]))} "
          f"m*={best[1]['gbest'][1]:.4f} F*={best[1]['gbest_fit']:.4f}")


if __name__ == "__main__":
    main()
