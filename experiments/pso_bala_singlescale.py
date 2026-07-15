# -*- coding: utf-8 -*-
"""PSO de la propuesta single-scale con SUMA de ramas (Eqs 1-8 de Bala, fusion Eq 12).
Operador por fuente (una escala, radio r; sin complemento): THm=(1/4)sum_theta[s-(s o linea)],
BHm=(1/4)sum_theta[(s . linea)-s], TH_bright=s-(s o disco), BH_dark=(s . disco)-s,
I_opt_top=THm+TH_bright (ec7, SUMA), I_opt_bot=BHm+BH_dark (ec8, SUMA).
Fusion (ec12): I_FUS=(VIS+IR)/2 + m*max(top_IR,top_VIS) - m*max(bot_IR,bot_VIS).
Equivale a fuse_optimal(mode='sum'). PSO optimiza (r,m); aptitud F=SSIM+Qabf+0.5*SCD-Nabf
sobre escenas representativas (eval final = 20 pares con evaluadores originales). Reanudable.
"""
import sys, json, time, argparse
from pathlib import Path
sys.path.insert(0, '.')
import numpy as np
import cv2
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from src.metrics.evaluators import _Q_pair, _corr

STATE = Path('experiments/results/pso/pso_propuesta_sum_state.json')
LO = np.array([1.0, 0.05]); HI = np.array([12.0, 1.20])
N_PART, T_MAX = 30, 50
W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5
_cache = None

def _grad_so(p):
    sx = cv2.Sobel(p, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(p, cv2.CV_32F, 0, 1, ksize=3)
    g = np.sqrt(sx*sx + sy*sy)
    a = np.where(sx != 0, np.arctan(sy/(sx+1e-12)), np.pi/2.0)
    return g, a

def _gb(x):
    return cv2.GaussianBlur(x, (11, 11), 1.5)

def _ssim_fast(f, x, mu_x, var_x):
    C1s, C2s = 0.01**2, 0.03**2
    mu_f = _gb(f); var_f = _gb(f*f) - mu_f*mu_f; cov = _gb(f*x) - mu_f*mu_x
    s = ((2*mu_f*mu_x + C1s)*(2*cov + C2s)) / ((mu_f*mu_f + mu_x*mu_x + C1s)*(var_f + var_x + C2s) + 1e-12)
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
            var_v = _gb(v*v) - mu_v*mu_v; var_i = _gb(i*i) - mu_i*mu_i
            _cache.append(dict(v=v, i=i, gA=gA, aA=aA, gB=gB, aB=aB,
                               mu_v=mu_v, var_v=var_v, mu_i=mu_i, var_i=var_i,
                               wsum=float(np.sum(gA+gB))+1e-12))
    return _cache

def fitness(x):
    r = int(round(np.clip(x[0], 1, 12))); m = float(np.clip(x[1], 0.05, 1.20))
    acc = 0.0; C = cache()
    for c in C:
        f = fuse_optimal(c['v'], c['i'], r, m, mode="sum")
        gF, aF = _grad_so(f)
        QAF = _Q_pair(c['gA'], c['aA'], gF, aF); QBF = _Q_pair(c['gB'], c['aB'], gF, aF)
        qabf = float(np.sum(QAF*c['gA'] + QBF*c['gB']) / c['wsum'])
        art = ((gF > c['gA']) & (gF > c['gB'])).astype(np.float64)
        nabf = float(np.sum(art*((1-QAF)*c['gA'] + (1-QBF)*c['gB'])) / c['wsum'])
        ssim = 0.5*(_ssim_fast(f, c['v'], c['mu_v'], c['var_v']) + _ssim_fast(f, c['i'], c['mu_i'], c['var_i']))
        sc = _corr(f - c['i'], c['v']) + _corr(f - c['v'], c['i'])
        acc += ssim + qabf + 0.5*sc - nabf
    return acc / len(C)

def init():
    rng = np.random.default_rng(123)
    X = rng.uniform(LO, HI, (N_PART, 2)); V = rng.uniform(-0.3, 0.3, (N_PART, 2))
    return {"t": 0, "i": 0, "X": X.tolist(), "V": V.tolist(), "pbest": X.tolist(),
            "pbest_fit": [-1e9]*N_PART, "gbest": [3, 0.5], "gbest_fit": -1e9,
            "history": [], "done": False}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--budget", type=float, default=40.0); a = ap.parse_args()
    s = json.load(open(STATE)) if STATE.exists() else init()
    if s["done"]:
        g = s["gbest"]; print("COMPLETO r=%d m=%.3f F=%.4f" % (int(round(g[0])), g[1], s["gbest_fit"]), flush=True); return
    X = np.array(s["X"]); V = np.array(s["V"]); pb = np.array(s["pbest"]); pbf = np.array(s["pbest_fit"])
    gb = np.array(s["gbest"]); gbf = s["gbest_fit"]; t0 = time.time(); ev = 0
    while s["t"] < T_MAX:
        while s["i"] < N_PART:
            if time.time()-t0 > a.budget:
                s.update(X=X.tolist(), V=V.tolist(), pbest=pb.tolist(), pbest_fit=pbf.tolist(),
                         gbest=gb.tolist(), gbest_fit=gbf)
                STATE.parent.mkdir(parents=True, exist_ok=True)
                json.dump(s, open(STATE, "w"))
                print("[ckpt] it %d/%d p %d/%d | gbest r=%d m=%.3f F=%.4f | ev %d" % (
                    s["t"]+1, T_MAX, s["i"], N_PART, int(round(gb[0])), gb[1], gbf, ev), flush=True)
                return
            i = s["i"]; fv = fitness(X[i]); ev += 1
            if fv > pbf[i]: pbf[i] = fv; pb[i] = X[i].copy()
            if fv > gbf: gbf = fv; gb = X[i].copy()
            s["i"] += 1
        r1 = np.random.default_rng(s["t"]+1).uniform(0, 1, (N_PART, 2))
        r2 = np.random.default_rng(1000+s["t"]).uniform(0, 1, (N_PART, 2))
        w = W_MAX - (W_MAX-W_MIN)*s["t"]/max(1, T_MAX-1)
        V = w*V + C1*r1*(pb-X) + C2*r2*(gb-X)
        X = np.clip(X + V, LO, HI)
        s["t"] += 1; s["i"] = 0
        s["history"].append({"it": s["t"], "gbest_fit": gbf, "r": float(gb[0]), "m": float(gb[1])})
    s.update(gbest=gb.tolist(), gbest_fit=gbf, done=True)
    STATE.parent.mkdir(parents=True, exist_ok=True); json.dump(s, open(STATE, "w"))
    print("COMPLETO r=%d m=%.3f F=%.4f" % (int(round(gb[0])), gb[1], gbf), flush=True)

if __name__ == "__main__":
    main()
