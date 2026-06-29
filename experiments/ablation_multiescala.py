# -*- coding: utf-8 -*-
"""Ablación del método óptimo multiescala: aporte de líneas, de la cascada y sensibilidad a n."""
import sys, time, json; sys.path.insert(0,'.')
import numpy as np, cv2
from src.datasets import list_pairs, load_pair
from src.fusion.optimal_top_hat import disk_se, linear_se, _open, _close, _ANGLES
from src.metrics.evaluators import _qabf_nabf, scd as _scd, ssim_fusion as _ssimf, std_dev

R=2.89; M=0.10

def wth_bth(f, r, mode):
    f=f.astype(np.float32); d=disk_se(r)
    wth=f-_open(f,d); bth=_close(f,d)-f
    if mode=='full':
        for th in _ANGLES:
            se=linear_se(r,th)
            wth=np.maximum(wth,f-_open(f,se)); bth=np.maximum(bth,_close(f,se)-f)
    return wth,bth

def multiscale(f, n, base_r, mode):
    WTH=[];BTH=[]
    for i in range(1,n+1):
        r=max(1,int(round(base_r*i))); w,b=wth_bth(f,r,mode); WTH.append(w);BTH.append(b)
    WTHS=[];BTHS=[]
    for i in range(2,n+1):
        if i==2: WTHS.append(WTH[1]-WTH[0]); BTHS.append(BTH[1]-BTH[0])
        else: WTHS.append(WTH[i-1]-WTHS[i-3]); BTHS.append(BTH[i-1]-BTHS[i-3])
    wm=np.maximum.reduce(WTH); bm=np.maximum.reduce(BTH)
    wsm=np.maximum.reduce(WTHS) if WTHS else np.zeros_like(f,np.float32)
    bsm=np.maximum.reduce(BTHS) if BTHS else np.zeros_like(f,np.float32)
    return wm,bm,wsm,bsm

def fuse(vis,ir,n,base_r,mode,m=M):
    if vis.shape!=ir.shape: ir=cv2.resize(ir,(vis.shape[1],vis.shape[0]))
    base=0.5*(vis.astype(np.float32)+ir.astype(np.float32))
    wv,bv,wsv,bsv=multiscale(vis,n,base_r,mode); wi,bi,wsi,bsi=multiscale(ir,n,base_r,mode)
    wm=np.maximum(wv,wi);bm=np.maximum(bv,bi);wsm=np.maximum(wsv,wsi);bsm=np.maximum(bsv,bsi)
    return np.clip(base+m*(wm+wsm)-m*(bm+bsm),0,1).astype(np.float32)

def evalp(vis,ir,fused):
    q,nb=_qabf_nabf(fused,vis,ir)
    return q,_ssimf(fused,vis,ir),_scd(fused,vis,ir),nb,std_dev(fused)

CONFIGS=[
 ('Disco solo (n=6)','disk',6),
 ('Disco + 4 lineas — propuesta (n=6)','full',6),
 ('Monoescala (n=1)','full',1),
 ('n=2','full',2),('n=4','full',4),('n=8','full',8),
]
pairs=list_pairs()[::4]  # 5 escenas representativas (igual que el PSO)
import os
OUTF='experiments/results/metrics_reports/ablation_multiescala.json'
rows=json.load(open(OUTF)) if os.path.exists(OUTF) else {}
t0=time.time()
for name,mode,n in CONFIGS:
    if name in rows: continue
    acc=np.zeros(5)
    for p in pairs:
        v,i=load_pair(*p); f=fuse(v,i,n,R,mode); acc+=np.array(evalp(v,i,f))
    rows[name]=(acc/len(pairs)).round(4).tolist()
    json.dump(rows,open(OUTF,'w'),indent=2)
    print(f'{name:38s} Qabf={rows[name][0]:.3f} SSIM={rows[name][1]:.3f} SCD={rows[name][2]:.3f} Nabf={rows[name][3]:.3f} SD={rows[name][4]:.3f}  ({time.time()-t0:.0f}s)')
print('DONE' if len(rows)==len(CONFIGS) else 'PARTIAL')
