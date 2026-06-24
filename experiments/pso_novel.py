# -*- coding: utf-8 -*-
"""PSO de la propuesta novedosa: optimiza (n escalas, peso m) maximizando
aptitud orientada a fusión F = SSIM + Qabf + 0.5*SCD - Nabf, sobre un subconjunto
representativo. Reanudable por checkpoint. Uso: timeout 44 python3 experiments/pso_novel.py --budget 40
"""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
from src.datasets import list_pairs, load_pair
from src.fusion.novel_fusion import fuse_novel
from src.metrics.evaluators import _qabf_nabf, scd as _scd, ssim_fusion as _ssimf

STATE = Path('experiments/results/pso/pso_novel_state.json')
LO = np.array([1.0, 0.05]); HI = np.array([8.0, 1.20])   # (n, m)
N_PART, T_MAX = 20, 20
W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5
_imgs = None

def imgs():
    global _imgs
    if _imgs is None:
        allp = list_pairs()
        _imgs = [load_pair(*p) for p in allp[::4]]   # 5 escenas representativas
    return _imgs

def fitness(x):
    n = int(round(np.clip(x[0], 1, 8))); m = float(np.clip(x[1], 0.05, 1.20))
    acc = 0.0
    for v, i in imgs():
        f = fuse_novel(v, i, n, m)
        q, nb = _qabf_nabf(f, v, i)
        acc += _ssimf(f, v, i) + q + 0.5 * _scd(f, v, i) - nb
    return acc / len(imgs())

def init():
    rng = np.random.default_rng(123)
    X = rng.uniform(LO, HI, (N_PART, 2)); V = rng.uniform(-0.3, 0.3, (N_PART, 2))
    return {"t": 0, "i": 0, "X": X.tolist(), "V": V.tolist(), "pbest": X.tolist(),
            "pbest_fit": [-1e9]*N_PART, "gbest": [6, 0.5], "gbest_fit": -1e9,
            "history": [], "done": False}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--budget", type=float, default=40.0); a = ap.parse_args()
    s = json.load(open(STATE)) if STATE.exists() else init()
    if s["done"]:
        g = s["gbest"]; print(f"COMPLETO n={int(round(g[0]))} m={g[1]:.3f} F={s['gbest_fit']:.4f}"); return
    X = np.array(s["X"]); V = np.array(s["V"]); pb = np.array(s["pbest"]); pbf = np.array(s["pbest_fit"])
    gb = np.array(s["gbest"]); gbf = s["gbest_fit"]; t0 = time.time(); ev = 0
    while s["t"] < T_MAX:
        while s["i"] < N_PART:
            if time.time()-t0 > a.budget:
                s.update(X=X.tolist(), V=V.tolist(), pbest=pb.tolist(), pbest_fit=pbf.tolist(),
                         gbest=gb.tolist(), gbest_fit=gbf); STATE.parent.mkdir(parents=True, exist_ok=True)
                json.dump(s, open(STATE, "w"))
                print(f"[ckpt] it {s['t']+1}/{T_MAX} p {s['i']}/{N_PART} | gbest n={int(round(gb[0]))} m={gb[1]:.3f} F={gbf:.4f} | ev {ev}"); return
            i = s["i"]; fv = fitness(X[i]); ev += 1
            if fv > pbf[i]: pbf[i] = fv; pb[i] = X[i].copy()
            if fv > gbf: gbf = fv; gb = X[i].copy()
            s["i"] += 1
        w = W_MAX - (W_MAX-W_MIN)*s["t"]/max(1, T_MAX-1)
        rng = np.random.default_rng(7000+s["t"]); r1 = rng.random((N_PART, 2)); r2 = rng.random((N_PART, 2))
        V = w*V + C1*r1*(pb-X) + C2*r2*(gb-X)
        X = np.clip(X+V, LO, HI)
        s["history"].append({"it": s["t"]+1, "n": int(round(gb[0])), "m": float(gb[1]), "F": float(gbf)})
        s["t"] += 1; s["i"] = 0
    s["done"] = True
    s.update(X=X.tolist(), V=V.tolist(), pbest=pb.tolist(), pbest_fit=pbf.tolist(), gbest=gb.tolist(), gbest_fit=gbf)
    json.dump(s, open(STATE, "w"))
    print(f"COMPLETO n={int(round(gb[0]))} m={gb[1]:.3f} F={gbf:.4f}")

if __name__ == "__main__":
    main()
