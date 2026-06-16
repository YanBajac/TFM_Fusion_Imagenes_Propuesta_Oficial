# -*- coding: utf-8 -*-
"""
PSO del MÉTODO ÓPTIMO MULTIESCALA (disco + 4 lineales, cascada). Optimiza:
  n  = número de escalas        ∈ [2, 6]   (entero)
  r  = radio base               ∈ [0.5, 3.0]
  m  = peso de contraste        ∈ [0.1, 1.5]
Aptitud (maximizar): F = SSIM_avg + E_n + PSNR_n  (Ortega & Espinoza, FPUNA).
Global sobre un subconjunto representativo de escenas. Reanudable (checkpoint).
"""
import sys, json, time, argparse
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import fuse_optimal_multiscale
from skimage.metrics import structural_similarity as ssim
from src.metrics.evaluators import _qabf_nabf, scd as _scd, ssim_fusion as _ssimf

STATE=ROOT/"experiments"/"results"/"pso"/"pso_multiscale_state.json"
N_PART,T_MAX=30,30
LO=np.array([2.0,0.5,0.1]); HI=np.array([6.0,3.0,1.5])
W_MAX,W_MIN,C1,C2=0.9,0.4,1.5,1.5
SEED=7
_imgs=None
def imgs():
    global _imgs
    if _imgs is None:
        allp=list_pairs(); _imgs=[load_pair(*p) for p in allp[::4]]  # 5 escenas representativas
    return _imgs
def _entropy(x):
    h,_=np.histogram(x,256,(0,1)); h=h/h.sum(); h=h[h>0]; return float(-(h*np.log2(h)).sum())
def _psnr(a,b):
    mse=float(np.mean((a-b)**2)); return 10*np.log10(1.0/(mse+1e-12))
def fitness(x):
    """Aptitud orientada a fusión: F = SSIM_avg + Qabf + 0.5*SCD - Nabf (maximizar)."""
    n=int(round(x[0])); r=float(x[1]); m=float(x[2])
    acc=0.0
    for v,i in imgs():
        f=fuse_optimal_multiscale(v,i,n=n,base_radius=r,m=m)
        q,nb=_qabf_nabf(f,v,i)
        acc += _ssimf(f,v,i) + q + 0.5*_scd(f,v,i) - nb
    return acc/len(imgs())
def init():
    rng=np.random.default_rng(SEED)
    X=rng.uniform(LO,HI,(N_PART,3)); V=rng.uniform(-0.5,0.5,(N_PART,3))
    return {"t":0,"i":0,"X":X.tolist(),"V":V.tolist(),"pbest":X.tolist(),
            "pbest_fit":[-1e9]*N_PART,"gbest":[4,1,0.5],"gbest_fit":-1e9,
            "history":[],"done":False}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--budget",type=float,default=40.0); a=ap.parse_args()
    s=json.load(open(STATE)) if STATE.exists() else init()
    if s["done"]:
        g=s["gbest"]; print(f"COMPLETO n={int(round(g[0]))} r={g[1]:.2f} m={g[2]:.3f} F={s['gbest_fit']:.4f}"); return
    t0=time.time(); ev=0
    X=np.array(s["X"]);V=np.array(s["V"]);pb=np.array(s["pbest"]);pbf=np.array(s["pbest_fit"])
    gb=np.array(s["gbest"]);gbf=s["gbest_fit"]
    while not s["done"]:
        while s["i"]<N_PART:
            if time.time()-t0>a.budget:
                s.update(X=X.tolist(),V=V.tolist(),pbest=pb.tolist(),pbest_fit=pbf.tolist(),
                         gbest=gb.tolist(),gbest_fit=gbf); STATE.parent.mkdir(parents=True,exist_ok=True)
                json.dump(s,open(STATE,"w"))
                print(f"[ckpt] it {s['t']+1}/{T_MAX} p {s['i']}/{N_PART} | gbest n={int(round(gb[0]))} r={gb[1]:.2f} m={gb[2]:.3f} F={gbf:.4f} | ev {ev}"); return
            i=s["i"]; fv=fitness(X[i]); ev+=1
            if fv>pbf[i]: pbf[i]=fv; pb[i]=X[i].copy()
            if fv>gbf: gbf=fv; gb=X[i].copy()
            s["i"]+=1
        w=W_MAX-(W_MAX-W_MIN)*s["t"]/max(1,T_MAX-1)
        rng=np.random.default_rng(2000+s["t"]); r1=rng.random((N_PART,3)); r2=rng.random((N_PART,3))
        V=w*V+C1*r1*(pb-X)+C2*r2*(gb-X)
        V=np.clip(V,-(HI-LO)*0.3,(HI-LO)*0.3); X=np.clip(X+V,LO,HI)
        s["history"].append({"it":s["t"]+1,"n":int(round(gb[0])),"r":float(gb[1]),"m":float(gb[2]),"F":float(gbf)})
        s["t"]+=1; s["i"]=0
        if s["t"]>=T_MAX: s["done"]=True
        s.update(X=X.tolist(),V=V.tolist(),pbest=pb.tolist(),pbest_fit=pbf.tolist(),gbest=gb.tolist(),gbest_fit=gbf)
        STATE.parent.mkdir(parents=True,exist_ok=True); json.dump(s,open(STATE,"w"))
    print(f"COMPLETO n={int(round(gb[0]))} r={gb[1]:.2f} m={gb[2]:.3f} F={gbf:.4f}")
if __name__=="__main__": main()
