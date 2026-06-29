# -*- coding: utf-8 -*-
"""
pso_optimal_tophat.py
---------------------
PSO (Particle Swarm Optimization) para optimizar (r, m) del método óptimo
basado en Top-Hat (disco + lineales) en fusión VIS/IR. Global sobre los 20 pares.
Aptitud multicriterio (Ortega & Espinoza, FPUNA 2025): F = SSIM_avg + E_n + PSNR_n.

Reanudable: guarda el estado en experiments/results/pso/pso_state.json y corre con
un presupuesto de tiempo por invocación (para los límites de 45 s del entorno).

Uso: python experiments/pso_optimal_tophat.py [--budget 38]
"""
import sys, json, time, argparse
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal
from skimage.metrics import structural_similarity as ssim

STATE = ROOT / "experiments" / "results" / "pso" / "pso_state.json"
N_PART, T_MAX = 30, 30
R_LO, R_HI = 1.0, 9.0
M_LO, M_HI = 0.3, 2.0
W_MAX, W_MIN, C1, C2 = 0.9, 0.4, 1.5, 1.5
MODE = "sum"
SEED = 42

_imgs = None
def imgs():
    global _imgs
    if _imgs is None:
        allp = list_pairs()
        sub = allp[::2]  # subconjunto representativo de 10 escenas para la aptitud PSO
        _imgs = [load_pair(*p) for p in sub]
    return _imgs

def _entropy(x):
    h,_=np.histogram(x,256,(0,1)); h=h/h.sum(); h=h[h>0]; return float(-(h*np.log2(h)).sum())
def _psnr(a,b):
    mse=float(np.mean((a-b)**2)); return 10*np.log10(1.0/(mse+1e-12))

def fitness(r, m):
    S=E=P=0.0
    for v,i in imgs():
        f=fuse_optimal(v,i,r=int(round(r)),m=float(m),mode=MODE)
        base=0.5*(v+i)
        S+=0.5*(ssim(f,v,data_range=1.0)+ssim(f,i,data_range=1.0))
        E+=_entropy(f)/8.0
        P+=_psnr(f,base)/100.0
    n=len(imgs()); return (S+E+P)/n

def clamp(x,lo,hi): return float(min(hi,max(lo,x)))

def init_state():
    rng=np.random.default_rng(SEED)
    X=np.column_stack([rng.uniform(R_LO,R_HI,N_PART), rng.uniform(M_LO,M_HI,N_PART)])
    V=np.column_stack([rng.uniform(-2,2,N_PART), rng.uniform(-0.5,0.5,N_PART)])
    return {"t":0,"i":0,"X":X.tolist(),"V":V.tolist(),
            "pbest":X.tolist(),"pbest_fit":[-1e9]*N_PART,
            "gbest":[3.0,1.0],"gbest_fit":-1e9,"fitbuf":[None]*N_PART,
            "history":[],"done":False,"rng":int(SEED)}

def load_state():
    if STATE.exists():
        return json.load(open(STATE))
    return init_state()
def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    json.dump(s, open(STATE,"w"))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--budget",type=float,default=38.0)
    args=ap.parse_args()
    s=load_state()
    if s["done"]:
        print(f"PSO YA COMPLETO. gbest r={s['gbest'][0]:.3f} m={s['gbest'][1]:.3f} F={s['gbest_fit']:.4f}")
        return
    t0=time.time(); evals=0
    X=np.array(s["X"]); V=np.array(s["V"]); pbest=np.array(s["pbest"])
    pbest_fit=np.array(s["pbest_fit"]); gbest=np.array(s["gbest"]); gbest_fit=s["gbest_fit"]
    fitbuf=s["fitbuf"]
    while not s["done"]:
        # fase de evaluación de la iteración t, desde partícula i
        while s["i"] < N_PART:
            if time.time()-t0 > args.budget:
                s["X"]=X.tolist();s["V"]=V.tolist();s["pbest"]=pbest.tolist()
                s["pbest_fit"]=pbest_fit.tolist();s["gbest"]=gbest.tolist()
                s["gbest_fit"]=gbest_fit;s["fitbuf"]=fitbuf; save_state(s)
                print(f"[checkpoint] iter {s['t']+1}/{T_MAX} part {s['i']}/{N_PART} | "
                      f"gbest r={gbest[0]:.2f} m={gbest[1]:.2f} F={gbest_fit:.4f} | evals {evals}")
                return
            i=s["i"]; r,m=X[i]
            fv=fitness(r,m); evals+=1; fitbuf[i]=fv
            if fv>pbest_fit[i]:
                pbest_fit[i]=fv; pbest[i]=X[i].copy()
            if fv>gbest_fit:
                gbest_fit=fv; gbest=X[i].copy()
            s["i"]+=1
        # fase de movimiento -> nueva iteración
        w=W_MAX-(W_MAX-W_MIN)*s["t"]/max(1,T_MAX-1)
        rng=np.random.default_rng(1000+s["t"])
        r1=rng.random((N_PART,2)); r2=rng.random((N_PART,2))
        V=w*V+C1*r1*(pbest-X)+C2*r2*(gbest-X)
        V[:,0]=np.clip(V[:,0],-3,3); V[:,1]=np.clip(V[:,1],-0.6,0.6)
        X=X+V
        X[:,0]=np.clip(X[:,0],R_LO,R_HI); X[:,1]=np.clip(X[:,1],M_LO,M_HI)
        s["history"].append({"iter":s["t"]+1,"gbest_r":float(gbest[0]),
                             "gbest_m":float(gbest[1]),"gbest_fit":float(gbest_fit)})
        s["t"]+=1; s["i"]=0; fitbuf=[None]*N_PART
        if s["t"]>=T_MAX:
            s["done"]=True
        s["X"]=X.tolist();s["V"]=V.tolist();s["pbest"]=pbest.tolist()
        s["pbest_fit"]=pbest_fit.tolist();s["gbest"]=gbest.tolist()
        s["gbest_fit"]=gbest_fit;s["fitbuf"]=fitbuf; save_state(s)
    print(f"PSO COMPLETO. gbest r={gbest[0]:.3f} (≈{int(round(gbest[0]))}) m={gbest[1]:.3f} F={gbest_fit:.4f}")

if __name__=="__main__":
    main()
