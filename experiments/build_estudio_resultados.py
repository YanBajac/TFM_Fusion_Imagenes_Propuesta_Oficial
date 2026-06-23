# -*- coding: utf-8 -*-
import json, pandas as pd, glob, os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

NAVY='1F3B57'; PROP='Optimo_Multiescala'
def fmt(x,dec=3):
    try: return f'{float(x):.{dec}f}'.replace('.',',')
    except: return str(x)

dm=pd.read_csv('experiments/results/metrics_reports/descriptive_means.csv').set_index('method')
rk=pd.read_csv('experiments/results/metrics_reports/ranking_methods.csv').set_index('Unnamed: 0')
fr=pd.read_csv('experiments/results/metrics_reports/friedman_results.csv')
ds=pd.read_csv('experiments/results/metrics_reports/detection_summary.csv').set_index('method')
abl=json.load(open('experiments/results/metrics_reports/ablation_multiescala.json'))

ORDER=[('Promedio','Promedio'),('PiramideLaplace','Pirámide de Laplace'),('Curvelet','Curvelet'),
('TopHat_disk_L3','Torre TH disco L3'),('TopHat_square_L3','Torre TH cuadrado L3'),
('TopHat_cross_L3','Torre TH cruz L3'),('TopHat_disk_L5','Torre TH disco L5 (anterior)'),
('TopHat_disk_L3_BTH','Torre TH disco L3 +BTH'),('TopHat_square_L3_BTH','Torre TH cuadrado L3 +BTH'),
('TopHat_cross_L3_BTH','Torre TH cruz L3 +BTH'),('TopHat_disk_L5_BTH','Torre TH disco L5 +BTH'),
('TopHat_Optimo','Óptimo monoescala'),('Optimo_Multiescala','Óptimo multiescala (propuesta)')]

doc=Document()
# márgenes
sec=doc.sections[0]
for m in ('top_margin','bottom_margin','left_margin','right_margin'): setattr(sec,m,Inches(0.8))
styles=doc.styles; styles['Normal'].font.name='Calibri'; styles['Normal'].font.size=Pt(10.5)

def H(txt,lvl=1):
    p=doc.add_heading(txt,level=lvl); return p
def P(txt,size=10.5,italic=False,after=6):
    p=doc.add_paragraph(); r=p.add_run(txt); r.font.size=Pt(size); r.italic=italic
    p.paragraph_format.space_after=Pt(after); return p

def table(headers, rows, widths=None, highlight_first_col_val=None, ndecimal=3):
    t=doc.add_table(rows=1+len(rows), cols=len(headers))
    t.alignment=WD_ALIGN_PARAGRAPH.CENTER
    # borders
    tblPr=t._tbl.tblPr; bd=OxmlElement('w:tblBorders')
    for e in ('top','left','bottom','right','insideH','insideV'):
        b=OxmlElement('w:'+e); b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'4'); b.set(qn('w:color'),'B0B8C0'); bd.append(b)
    tblPr.append(bd)
    for ci,htxt in enumerate(headers):
        c=t.rows[0].cells[ci]; c.paragraphs[0].text=''
        r=c.paragraphs[0].add_run(htxt); r.font.bold=True; r.font.size=Pt(9); r.font.color.rgb=RGBColor.from_string('FFFFFF')
        sh=OxmlElement('w:shd'); sh.set(qn('w:val'),'clear'); sh.set(qn('w:fill'),NAVY); c._tc.get_or_add_tcPr().append(sh)
    for ri,row in enumerate(rows,1):
        is_prop = highlight_first_col_val and row[0]==highlight_first_col_val
        for ci,val in enumerate(row):
            c=t.rows[ri].cells[ci]; c.paragraphs[0].text=''
            r=c.paragraphs[0].add_run(str(val)); r.font.size=Pt(9)
            if is_prop: r.font.bold=True
            if ci>0: c.paragraphs[0].alignment=WD_ALIGN_PARAGRAPH.CENTER
    return t

# ===================== PORTADA =====================
ti=doc.add_paragraph(); ti.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=ti.add_run('Estudio de resultados de los experimentos de fusión VIS/IR'); r.font.size=Pt(18); r.font.bold=True; r.font.color.rgb=RGBColor.from_string(NAVY)
st=doc.add_paragraph(); st.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=st.add_run('Tablas cuantitativas (12 métricas) y comparación cualitativa por escena'); r.font.size=Pt(12); r.italic=True
P('TFM — Maestría en Ciencias de Datos · UCOM. Dataset: TNO Image Fusion (20 pares VIS/IR). '
  '13 métodos evaluados: 3 baselines (Promedio, Pirámide de Laplace, Curvelet), 8 configuraciones de la Torre Top-Hat '
  '(método anterior; WTH y WTH+BTH), el óptimo monoescala y el óptimo multiescala (propuesta, PSO: n=6, r≈2,89, m=0,10). '
  'Métricas sin referencia: 6 clásicas (EN, SD, FE, MG, MI_vis, MI_ir) y 6 estándar de calidad (SF, Qabf, Nabf, SSIM, SCD, VIF).', after=4)

# ===================== 1. CUANTITATIVO =====================
H('1. Resultados cuantitativos',1)

H('1.1 Métricas clásicas de actividad e información (medias, n = 20)',2)
hdr=['Método','EN','SD','FE','MG','MI_vis','MI_ir']
rows=[[name]+[fmt(dm.loc[k,m]) for m in ['EN','SD','FE','MG','MI_vis','MI_ir']] for k,name in ORDER]
table(hdr,rows,highlight_first_col_val='Óptimo multiescala (propuesta)')
P('Mayor es mejor en todas. El disco L5 +BTH maximiza EN/SD/MG (contraste/actividad), a costa de la calidad (ver 1.2).',9,True)

H('1.2 Métricas estándar de calidad de fusión (medias, n = 20)',2)
hdr=['Método','SF','Qabf ↑','Nabf ↓','SSIM ↑','SCD ↑','VIF ↑']
rows=[[name]+[fmt(dm.loc[k,m]) for m in ['SF','Qabf','Nabf','SSIM','SCD','VIF']] for k,name in ORDER]
table(hdr,rows,highlight_first_col_val='Óptimo multiescala (propuesta)')
P('El óptimo multiescala lidera Qabf (0,514) y SCD (1,453), registra el menor Nabf entre métodos no triviales (0,065) y es 2º en SSIM (0,775). Nabf: menor es mejor.',9,True)

H('1.3 Ranking por rangos promedio (1 = mejor)',2)
hdr=['Método','Qabf','Nabf','SSIM','SCD','VIF','SF','Rango global']
rows=[]
for k,name in ORDER:
    if k in rk.index:
        rows.append([name]+[fmt(rk.loc[k,m],1) for m in ['Qabf','Nabf','SSIM','SCD','VIF','SF']]+[fmt(rk.loc[k,'avg_rank'],2)])
rows.sort(key=lambda r: float(r[-1].replace(',','.')))
table(hdr,rows,highlight_first_col_val='Óptimo multiescala (propuesta)')
P('Rango promedio sobre las 12 métricas (menor es mejor). Laplace lidera el agregado por su ventaja en contraste; el óptimo multiescala domina las métricas de calidad (Qabf, SCD, Nabf, SSIM).',9,True)

H('1.4 Significancia estadística — prueba de Friedman',2)
hdr=['Métrica','χ² de Friedman','p-valor','Significativo (α=0,05)']
rows=[[r['metric'],fmt(r['chi2'],2),f"{r['p_value']:.2e}".replace('.',','),'Sí' if r['significant_05'] else 'No'] for _,r in fr.iterrows()]
table(hdr,rows)
P('Todas las métricas resultan altamente significativas (p << 0,001): las diferencias entre métodos no se deben al azar.',9,True)

H('1.5 Ablación del método óptimo multiescala (5 escenas representativas)',2)
hdr=['Variante','Qabf ↑','SSIM ↑','SCD ↑','Nabf ↓']
amap=[('Monoescala (n=1)','Monoescala (n = 1)'),('n=2','Cascada n = 2'),('n=4','Cascada n = 4'),
 ('Disco + 4 lineas — propuesta (n=6)','Cascada n = 6 — propuesta'),('n=8','Cascada n = 8'),('Disco solo (n=6)','n = 6, solo disco')]
rows=[[lab]+[fmt(abl[k][i]) for i in (0,1,2,3)] for k,lab in amap]
table(hdr,rows,highlight_first_col_val='Cascada n = 6 — propuesta')
P('La cascada (n) es el factor determinante; los SE lineales aportan poco frente al disco solo en estas métricas.',9,True)

H('1.6 Evaluación orientada a tarea — detección con YOLOv8n (inferencia)',2)
hdr=['Método','Detecciones','Personas','Vehículos','Conf. media','FPS']
disp={k:n for k,n in ORDER}; disp['VIS']='VIS (solo visible)'; disp['IR']='IR (solo infrarrojo)'
rows=[]
for k in ['VIS','IR']+[o[0] for o in ORDER]:
    if k in ds.index:
        rows.append([disp.get(k,k),int(ds.loc[k,'det_total']),int(ds.loc[k,'person_total']),int(ds.loc[k,'vehiculo_total']),fmt(ds.loc[k,'conf_media']),fmt(ds.loc[k,'FPS'],1)])
table(hdr,rows,highlight_first_col_val='Óptimo multiescala (propuesta)')
P('La fusión mejora la detectabilidad de personas frente a VIS. Las diferencias entre métodos no son estadísticamente significativas (n=20 sin etiquetas); mAP concluyente requiere un dataset etiquetado.',9,True)

# ===================== 2. CUALITATIVO =====================
doc.add_page_break()
H('2. Comparación cualitativa por escena',1)
P('Para cada una de las 20 escenas se muestran las imágenes fuente (VIS, IR) y la salida de los 13 métodos de fusión, '
  'permitiendo estudiar el efecto visual de cada uno (el óptimo multiescala se resalta con ★).', after=8)
monts=sorted(glob.glob('docs/figures/cualitativas/montaje_*.png'))
for i,mp in enumerate(monts,1):
    doc.add_picture(mp, width=Inches(6.9))
    doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    if i%2==0 and i<len(monts): doc.add_page_break()

doc.save('/tmp/resultados.docx')
print('DOCX OK ->', len(doc.paragraphs),'parrafos,',len(doc.tables),'tablas,',len(monts),'montajes')
