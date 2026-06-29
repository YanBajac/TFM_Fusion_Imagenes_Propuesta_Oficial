# -*- coding: utf-8 -*-
import os, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from PIL import Image
BK='#000000'
FUSED='experiments/results/fused_images'; OUT='docs/figures/cualitativas/'
CELLS=[('__VIS__','VIS'),('__IR__','IR'),('Promedio','Promedio'),('PiramideLaplace','Laplace'),
 ('Curvelet','Curvelet'),('TopHat_disk_L3','TH disco L3'),('TopHat_square_L3','TH cuadr. L3'),
 ('TopHat_cross_L3','TH cruz L3'),('TopHat_disk_L5','TH disco L5 (anterior)'),
 ('TopHat_disk_L3_BTH','TH disco L3+BTH'),('TopHat_square_L3_BTH','TH cuadr. L3+BTH'),
 ('TopHat_cross_L3_BTH','TH cruz L3+BTH'),('TopHat_disk_L5_BTH','TH disco L5+BTH'),
 ('TopHat_Optimo','TH Optimo (mono)'),('Optimo_Multiescala','Optimo multiescala (propuesta)')]
vis_files=sorted(os.listdir('data/raw/VIS'))
def load(p): return np.asarray(Image.open(p).convert('L'))
plt.rcParams.update({'font.family':'serif'})
for idx,vf in enumerate(vis_files,1):
    stem=os.path.splitext(vf)[0]; outp=f'{OUT}montaje_{idx:02d}.png'
    imgs={'__VIS__':f'data/raw/VIS/{vf}','__IR__':f'data/raw/IR/{vf}'}
    fig,axes=plt.subplots(4,4,figsize=(11,8.6)); fig.patch.set_facecolor('white'); axes=axes.ravel()
    for k,(d,lab) in enumerate(CELLS):
        ax=axes[k]
        p=imgs[d] if d in imgs else (glob.glob(f'{FUSED}/{d}/{stem}.*')+[None])[0]
        if p: ax.imshow(load(p),cmap='gray')
        ax.set_title(lab,color=BK,fontsize=9.5,pad=2)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values(): sp.set_edgecolor('#000000'); sp.set_linewidth(0.6)
    axes[15].axis('off')
    fig.suptitle(f'Escena {idx}: {stem.replace("_"," ")[:46]}',color=BK,fontsize=12,y=0.995)
    fig.tight_layout(rect=[0,0,1,0.975]); fig.savefig(outp,dpi=105,facecolor='white'); plt.close(fig)
print('montajes:',len(glob.glob(OUT+'montaje_*.png')))
