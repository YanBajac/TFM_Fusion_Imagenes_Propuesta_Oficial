# -*- coding: utf-8 -*-
"""Barrido PSO paralelo con la funcion objetivo F_o de Ortega & Espinoza (FPUNA 2025):
    F_o = SSIM_avg + E_n + PSNR_n         (ecs. 15-17 y 19 del libro)
con SSIM_avg = 1/2[SSIM(F,IR)+SSIM(F,VIS)], E_n = E/8 (entropia de 8 bits) y
PSNR_n = PSNR/100 (PSNR estandar con MAX=1 sobre el MSE promedio contra ambas
fuentes; la ec. 29 del libro contiene una errata en el numerador, se usa la
definicion estandar 10*log10(MAX^2/MSE)).

Mismo Cuadro 1 (n en {2,4,6,8,10} x Tmax en {10,20,30,40,50}) y mismo espacio de
busqueda del libro: r en [1, 25], m en [0.3, 2.0] (rango que contiene el 0.5-2
sugerido por el director). Dos operadores:
  --operator propuesta : Top-Hat 1 escala con suma de ramas (ablacion de aptitud)
  --operator clasico   : disco unico + maximo (replica fiel del libro FPUNA)

Salida: experiments/results/metrics_reports/pso_grid_search_fo_<operador>.csv
        experiments/results/pso/pso_grid_fo_<operador>_state.json (reanudable)
Uso:    python experiments/pso_grid_search_fo.py --operator propuesta --budget 5400
"""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
import cv2
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from src.fusion.comparatives import tophat_classic_fusion

W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5
PARTICULAS = [2, 4, 6, 8, 10]
ITERACIONES = [10, 20, 30, 40, 50]
LO = np.array([1.0, 0.30]); HI = np.array([25.0, 2.00])   # rango del libro FPUNA
_cache = None


def _gb(x):
    return cv2.GaussianBlur(x, (11, 11), 1.5)


def _ssim_fast(f, x, mu_x, var_x):
    C1s, C2s = 0.01 ** 2, 0.03 ** 2
    mu_f = _gb(f); var_f = _gb(f * f) - mu_f * mu_f
    cov = _gb(f * x) - mu_f * mu_x
    s = ((2 * mu_f * mu_x + C1s) * (2 * cov + C2s)) / (
        (mu_f * mu_f + mu_x * mu_x + C1s) * (var_f + var_x + C2s) + 1e-12)
    return float(s.mean())


def _entropia8(f):
    """Entropia de Shannon sobre 256 niveles, normalizada por 8 bits (ec. 15)."""
    h, _ = np.histogram(np.clip(f, 0, 1), bins=256, range=(0.0, 1.0))
    p = h.astype(np.float64) / max(1, h.sum())
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum()) / 8.0


def _psnr_n(f, v, i):
    """PSNR estandar (MAX=1) sobre el MSE promedio contra ambas fuentes, /100 (ec. 16)."""
    mse = 0.5 * (float(np.mean((f - v) ** 2)) + float(np.mean((f - i) ** 2)))
    psnr = 10.0 * np.log10(1.0 / max(mse, 1e-12))
    return float(psnr) / 100.0


def cache():
    global _cache
    if _cache is None:
        allp = list_pairs()
        _cache = []
        for p in allp[::7]:      # mismas 3 escenas del barrido con F_apt
            v, i = load_pair(*p)
            mu_v = _gb(v); mu_i = _gb(i)
            _cache.append(dict(v=v, i=i, mu_v=mu_v, mu_i=mu_i,
                               var_v=_gb(v * v) - mu_v * mu_v,
                               var_i=_gb(i * i) - mu_i * mu_i))
    return _cache


def hacer_fitness(operador):
    def fitness(x):
        r = int(round(np.clip(x[0], LO[0], HI[0])))
        m = float(np.clip(x[1], LO[1], HI[1]))
        acc = 0.0
        C = cache()
        for c in C:
            if operador == "propuesta":
                f = fuse_optimal(c['v'], c['i'], r, m, mode="sum")
            else:
                f = tophat_classic_fusion(c['v'], c['i'], r=r, m=m)
            ssim = 0.5 * (_ssim_fast(f, c['v'], c['mu_v'], c['var_v'])
                          + _ssim_fast(f, c['i'], c['mu_i'], c['var_i']))
            acc += ssim + _entropia8(f) + _psnr_n(f, c['v'], c['i'])
        return acc / len(C)
    return fitness


def init_swarm(n, seed):
    rng = np.random.default_rng(seed)
    X = rng.uniform(LO, HI, (n, 2))
    V = rng.uniform(-0.3, 0.3, (n, 2))
    return X, V


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--operator", choices=["propuesta", "clasico"], required=True)
    ap.add_argument("--budget", type=float, default=5400.0)
    a = ap.parse_args()
    STATE = Path(f'experiments/results/pso/pso_grid_fo_{a.operator}_state.json')
    OUT_CSV = Path(f'experiments/results/metrics_reports/pso_grid_search_fo_{a.operator}.csv')
    fitness = hacer_fitness(a.operator)
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
                       "gbest": [3.0, 1.0], "gbest_fit": -1e9,
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
                    print(f"[ckpt] {key} it {cfg['t']}/{T} | gbest r={gb[0]:.1f} "
                          f"m={gb[1]:.3f} Fo={gbf:.4f}", flush=True)
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
                  f"Fo*={gbf:.4f} | evals={cfg['evals']} seg={cfg['seg']:.0f}", flush=True)

    rows = ["n,Tmax,evaluaciones,r_opt,m_opt,Fo_opt,segundos"]
    for n in PARTICULAS:
        for T in ITERACIONES:
            c = s["configs"][f"n{n}_T{T}"]
            rows.append(f"{n},{T},{c['evals']},{int(round(c['gbest'][0]))},"
                        f"{c['gbest'][1]:.4f},{c['gbest_fit']:.4f},{c['seg']:.0f}")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_CSV.write_text("\n".join(rows), encoding="utf-8")
    best = max(s["configs"].items(), key=lambda kv: kv[1]["gbest_fit"])
    print(f"\nBARRIDO Fo ({a.operator}) COMPLETO ->", OUT_CSV)
    print(f"Mejor configuracion: {best[0]} | r*={int(round(best[1]['gbest'][0]))} "
          f"m*={best[1]['gbest'][1]:.4f} Fo*={best[1]['gbest_fit']:.4f}")


if __name__ == "__main__":
    main()
