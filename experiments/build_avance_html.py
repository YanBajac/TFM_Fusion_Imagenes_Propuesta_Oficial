# -*- coding: utf-8 -*-
"""Genera docs/Avances_Tesis.html (informe de avance, propuesta single-scale).
Fuente reproducible del PDF (imprimir con Chrome/Edge: Ctrl+P -> Guardar como PDF, A4)."""
import json, os
J=json.load(open('/tmp/av_numbers.json',encoding='utf-8')) if os.path.exists('/tmp/av_numbers.json') else {}
M=J.get('means16',{}); FR=J.get('friedman',{}); WC=J.get('wilcoxon_cls',{})
FIG="figures/"
def img(name,cap,w=88):
    return f'<figure><img src="{FIG}{name}" style="width:{w}%"><figcaption>{cap}</figcaption></figure>'
M12=["EN","SD","FE","MG","MI_vis","MI_ir","SF","Qabf","Nabf","SSIM","SCD","VIF"]
def row(name,vals,bold=False):
    tds="".join(f"<td>{v}</td>" for v in vals)
    cls=' class="prop"' if bold else ''
    return f"<tr{cls}><td class='m'>{name}</td>{tds}</tr>"

CSS="""
@page { size: A4; margin: 20mm 18mm; }
* { box-sizing: border-box; }
body { font-family: 'Segoe UI', Arial, sans-serif; color:#1a1a1a; font-size:11.5px; line-height:1.5; }
h1 { font-size:20px; color:#1f3b5c; margin:0 0 4px; }
h2 { font-size:15px; color:#1f3b5c; border-bottom:2px solid #1f3b5c; padding-bottom:3px; margin:0 0 8px; page-break-after:avoid; }
h3 { font-size:12.5px; color:#2f5b7c; margin:14px 0 4px; }
section { page-break-before: always; }
section.cover { page-break-before: avoid; text-align:center; padding-top:60px; }
p { margin:6px 0; text-align:justify; }
.lead { color:#2f5b7c; font-weight:bold; }
table { border-collapse:collapse; width:100%; font-size:9.7px; margin:8px 0; }
th,td { border:1px solid #cfd6df; padding:3px 5px; text-align:center; }
th { background:#1f3b5c; color:#fff; font-weight:600; }
td.m { text-align:left; font-weight:600; background:#f4f7fb; white-space:nowrap; }
tr.prop td { background:#fbeaea; font-weight:bold; }
tr:nth-child(even) td { background:#f7f9fc; }
tr.prop:nth-child(even) td { background:#fbeaea; }
figure { margin:10px 0; text-align:center; page-break-inside:avoid; }
figure img { border:1px solid #dde3ea; border-radius:4px; }
figcaption { font-size:9px; color:#666; font-style:italic; margin-top:3px; }
.eq { background:#f4f7fb; border-left:3px solid #2f5b7c; padding:6px 10px; margin:8px 0; font-family:'Cambria Math',Georgia,serif; font-size:11.5px; }
.eqn { float:right; color:#888; }
.note { background:#fff6e6; border-left:3px solid #b8860b; padding:6px 10px; margin:8px 0; font-size:10.5px; }
.badge { display:inline-block; background:#b8860b; color:#fff; font-size:9px; padding:1px 6px; border-radius:8px; vertical-align:middle; }
ul { margin:6px 0 6px 18px; } li { margin:3px 0; }
.small { font-size:9.5px; color:#555; }
.mejor { color:#137333; font-weight:bold; } .peor { color:#b0261a; } .aeq { color:#888; }
"""

def wcell(v):
    if v=="mejor": return '<td class="mejor">mejor</td>'
    if v=="peor": return '<td class="peor">peor</td>'
    return '<td class="aeq">≈</td>'

# --- tabla 6 datos (5 métodos) ---
T6={
"Promedio":[6.518,0.109,1.029,0.014,1.512,1.064,7.112,0.310,0.000,0.792,1.325,0.331],
"Pirámide de Laplace":[6.835,0.155,1.079,0.025,2.118,1.072,13.040,0.442,0.108,0.721,1.322,0.410],
"Curvelet":[6.665,0.117,1.053,0.026,1.304,0.884,13.151,0.476,0.192,0.731,1.321,0.307],
"Torre Top-Hat disco L5":[6.722,0.125,1.062,0.024,1.363,0.914,11.923,0.458,0.117,0.739,1.430,0.356],
}
prop12=[M.get(k) for k in M12]
T7={"Promedio":[0.215,0.691,0.727,0.341],"Pirámide de Laplace":[0.276,0.744,0.856,0.404],
"Curvelet":[0.197,0.727,0.823,0.369],"Torre Top-Hat disco L5":[0.213,0.743,0.810,0.360]}

html=[f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>Presentación de avances — Fusión IR/VIS</title><style>{CSS}</style></head><body>"]

# Cover
html.append("""<section class="cover">
<p class="small">Universidad Comunera (UCOM) — Maestría en Ciencias de Datos</p>
<h1 style="font-size:26px;margin-top:40px">Fusión de imágenes infrarrojas y visibles mediante morfología matemática</h1>
<p style="font-size:15px;color:#2f5b7c;font-weight:bold">Presentación de avances</p>
<p>Procesos realizados, fórmulas y métricas por etapa</p>
<p style="margin-top:50px">Autores: Lic. Juan Pablo Bazán — Ing. Yan Bajac</p>
<p>Director: D.Sc. Julio César Mello</p>
<p class="small" style="margin-top:30px">Actualizado — propuesta de una sola escala (r=12, m=0,127)</p>
</section>""")

# 1 Intro
html.append("""<section><h2>1. Introducción y esquema general</h2>
<p>Este informe documenta, paso por paso, el trabajo realizado en el proyecto de tesis. En cada etapa se presentan las fórmulas utilizadas y la tabla de métricas que esa etapa dejó resuelta, de modo que pueda seguirse cómo cada decisión fue tomada en base a los resultados numéricos.</p>
<p>El orden del documento es el siguiente:</p>
<ul>
<li>Datos de entrada: 20 pares VIS/IR del dataset TNO (sección 2).</li>
<li>Fundamentos: operadores morfológicos y transformada Top-Hat (sección 3).</li>
<li>Primeras fusiones Top-Hat de una escala, con su tabla de métricas (sección 4).</li>
<li>Torre Top-Hat y el ensayo de la rama Black Top-Hat, con sus tablas (sección 5).</li>
<li>Métodos clásicos de comparación, con su tabla (sección 6).</li>
<li>Optimización de hiperparámetros por PSO (sección 7).</li>
<li><b>Propuesta novedosa de una sola escala</b>, con su tabla (sección 8).</li>
<li>Comparación final con las 16 métricas y análisis estadístico (secciones 9 y 10).</li>
<li>Resultados cualitativos de las 20 escenas (sección 11).</li>
<li>Evaluación de detección de objetos (sección 12) y conclusiones (sección 13).</li>
</ul>"""+img("fig_morfologia_tophat.png","Figura 1. Esquema general del proceso, desde las fuentes VIS/IR hasta las métricas y la detección.",70)+"</section>")

# 2 Datos
html.append("""<section><h2>2. Datos de entrada: 20 pares VIS/IR (TNO)</h2>
<p>Se trabaja con los 20 pares registrados del <b>TNO Image Fusion Dataset</b> (escenas de vigilancia nocturna: vehículos, personas, humo). Cada escena tiene una imagen visible (VIS), que aporta textura y contexto, y una infrarroja (IR), que registra la radiación térmica. Ambas comparten nombre de archivo para el emparejado automático. Sobre estos 20 pares se calculan todas las métricas del informe.</p>"""+img("ejemplo_modalidades.png","Figura 2. Aporte de cada modalidad: la VIS brinda textura y contexto; la IR revela los objetivos térmicos.",70)+"</section>")

# 3 Fundamentos
html.append("""<section><h2>3. Fundamentos: morfología matemática y Top-Hat</h2>
<p>Dado un elemento estructurante (SE) <i>b</i>, la dilatación toma el máximo local y la erosión el mínimo. Su composición define la <b>apertura</b> γ (elimina objetos claros menores que el SE) y el <b>cierre</b> φ (rellena huecos oscuros menores que el SE). La transformada Top-Hat conserva lo que la apertura o el cierre eliminan: la <b>White Top-Hat</b> (WTH) extrae el detalle brillante fino y la <b>Black Top-Hat</b> (BTH) el detalle oscuro fino:</p>
<div class="eq">WTH(f) = f − γ(f, b) &nbsp;;&nbsp; BTH(f) = φ(f, b) − f <span class="eqn">(1)</span></div>
"""+img("fig_cinco_se.png","Figura 3. Los cinco elementos estructurantes empleados: un disco y cuatro líneas (0°, 45°, 90°, 135°).",60)+"</section>")
open('docs/Avances_Tesis.html','w',encoding='utf-8').write("".join(html))
print("Parte 1 escrita:", len("".join(html)), "chars")
