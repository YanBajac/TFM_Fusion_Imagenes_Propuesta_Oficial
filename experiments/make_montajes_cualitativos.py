# -*- coding: utf-8 -*-
import os, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
NAVY='#1f3b57'; ACC='#c0392b'
FUSED='experiments/results/fused_images'
OUT='docs/figures/cualitativas/'
# (dir, etiqueta, color)
CELLS=[('__VIS__','VIS',NAVY),('__IR__','IR',NAVY),
 ('Promedio','Promedio',NAVY),('PiramideLaplace','Laplace',NAVY),
 ('Curvelet','Curvelet',NAVY),
 ('TopHat_disk_L3','TH disco L3',NAVY),('TopHat_square_L3','TH cuadr. L3',NAVY),
 ('TopHat_cross_L3','TH cruz L3',NAVY),('TopHat_disk_L5','TH disco L5 (anterior)',NAVY),
 ('TopHat_disk_L3_BTH','TH disco L3+BTH',NAVY),('TopHat_square_L3_BTH','TH cuadr. L3+BTH',NAVY),
 ('TopHat_cross_L3_BTH','TH cruz L3+BTH',NAVY),('TopHat_disk_L5_BTH','TH disco L5+BTH',NAVY),
 ('TopHat_Optimo','TH Óptimo (mono)',NAVY),('Optimo_Multiescala','Óptimo Multiescala ★',ACC)]
vis_files=sorted(os.listdir('data/raw/VIS'))
def load(path): return np.asarray(Image.open(path).convert('L'))
def scene_label(stem):
    s=stem.replace('_',' ')
    return s[:46]
for idx,vf in enumerate(vis_files,1):
    stem=os.path.splitext(vf)[0]
    outp=f'{OUT}montaje_{idx:02d}.png'
    if os.path.exists(outp): continue
    imgs={'__VIS__':f'data/raw/VIS/{vf}','__IR__':f'data/raw/IR/{vf}'}
    fig,axes=plt.subplots(4,4,figsize=(11,8.6)); fig.patch.set_facecolor('white')
    axes=axes.ravel()
    for k,(d,lab,col) in enumerate(CELLS):
        ax=axes[k]
        if d in imgs: p=imgs[d]
        else:
            cand=glob.glob(f'{FUSED}/{d}/{stem}.*'); p=cand[0] if cand else None
        if p:
            ax.imshow(load(p),cmap='gray')
        ax.set_title(lab,color=col,fontsize=10,fontweight='bold',pad=2)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_edgecolor('#d0d0d0')
    axes[15].axis('off')
    fig.suptitle(f'Escena {idx}: {scene_label(stem)}',color=NAVY,fontsize=13,fontweight='bold',y=0.995)
    fig.tight_layout(rect=[0,0,1,0.975]); fig.savefig(outp,dpi=105,facecolor='white'); plt.close(fig)
    print('montaje',idx,'OK')
print('DONE', len(glob.glob(OUT+'montaje_*.png')),'montajes')
