# -*- coding: utf-8 -*-
"""Genera docs/Resultados_Optimos_por_Imagen.pdf — informe breve e independiente con el
optimo (r, m) hallado para CADA imagen fusionada y las metricas en ese punto.

Presenta dos escenarios, porque la eleccion del rango de busqueda determina el resultado:
  A) rango publicado por el trabajo de referencia, m en [0,30; 2,00]
  B) rango ampliado, m en [0,01; 2,00], donde el optimo de F_o queda en el interior

Entrada: metrics_reports/pso_por_imagen.csv y pso_por_imagen_libre.csv
Uso: .venv\Scripts\python.exe -X utf8 experiments/make_reporte_optimos.py
"""
import base64
import io
import os
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.datasets import list_pairs, load_pair          # noqa: E402
from src.fusion.optimal_top_hat import fuse_optimal      # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MR = os.path.join(ROOT, "experiments", "results", "metrics_reports")
OUT_DIR = os.path.join(ROOT, "docs", "_local")
os.makedirs(OUT_DIR, exist_ok=True)
HTML_OUT = os.path.join(OUT_DIR, "Resultados_Optimos_por_Imagen.html")
# Escribe en docs/historial/ y no en docs/: este informe no es un entregable, es un anexo de trabajo
# que el informe de avances ya cubre. Si saliera a docs/ volveria a parecer vigente cada vez que se
# corriera el script. Los cuatro entregables son los unicos habitantes de docs/ raiz.
PDF_OUT = os.path.join(ROOT, "docs", "historial", "Resultados_Optimos_por_Imagen.pdf")

ESCENA = {
    "APC_1_view_1_fk_06_005": "APC 1 · vista 1",
    "APC_1_view_2_fk_ref_01_005": "APC 1 · vista 2",
    "APC_1_view_3_fk_ref_02_005": "APC 1 · vista 3",
    "APC_3_view_1_fk_bar_06_005": "APC 3 · vista 1",
    "APC_3_view_2_fk_NL_01_005": "APC 3 · vista 2",
    "APC_3_view_3_fk_NL_05_005": "APC 3 · vista 3",
    "Athena_2_men_in_front_of_house_meting003": "2 men in front of house",
    "Athena_APC_4_fennek01_005": "APC 4 (fennek)",
    # Athena_heather_IR_hei_vis_g salio del corpus: su canal visible era una copia byte a byte del
    # infrarrojo, asi que toda metrica de fidelidad daba su valor perfecto. Lo sustituye Kaptein_1123.
    "Athena_heather_hei_vis": "heather (hei vis)",
    "Athena_helicopter_helib_011": "helicopter",
    "Athena_lake_lake": "lake",
    "Athena_man_in_doorway_maninhuis": "man in doorway",
    "Athena_soldier_behind_smoke_1_meting012-1200": "soldier behind smoke 1",
    "Athena_soldier_behind_smoke_2_meting012-1500": "soldier behind smoke 2",
    "Athena_soldier_behind_smoke_3_meting012-1700": "soldier behind smoke 3",
    "Athena_soldier_in_trench_1_meting016": "soldier in trench 1",
    "Athena_soldier_in_trench_2_meting055": "soldier in trench 2",
    "Triclobs_Bosnia_R": "Bosnia",
    "Triclobs_Kaptein_1123": "Kaptein 1123",
    "Triclobs_jeep_in_smoke_R": "jeep in smoke",
}
COLS = [("particulas", "Part.", 0), ("iteraciones", "Iter.", 0), ("r", "r", 0),
        ("m", "m", 4), ("SSIM_avg", "SSIM_avg", 6), ("E", "E", 6), ("SF", "SF", 6),
        ("SD", "SD", 6), ("PSNR", "PSNR", 6), ("FO", "FO", 6)]


def num(v, dec):
    return f"{int(v)}" if dec == 0 else f"{float(v):.{dec}f}".replace(".", ",")


def mejores(csv):
    d = pd.read_csv(os.path.join(MR, csv))
    return d.loc[d.groupby("imagen")["FO"].idxmax()].set_index("imagen")


def tabla_optimos(mej, orden):
    filas = []
    for img in orden:
        r = mej.loc[img]
        tds = "".join(f"<td>{num(r[c], d)}</td>" for c, _, d in COLS)
        filas.append(f'<tr><td class="l">{ESCENA.get(img, img)}</td>{tds}</tr>')
    head = "".join(f"<th>{lbl}</th>" for _, lbl, _ in COLS)
    return (f'<table><tr><th class="l">Escena</th>{head}</tr>{"".join(filas)}</table>')


def tabla_comparativa(a, b, orden):
    filas = []
    for img in orden:
        ra, rb = a.loc[img], b.loc[img]
        d = float(rb["FO"]) - float(ra["FO"])
        filas.append(
            f'<tr><td class="l">{ESCENA.get(img, img)}</td>'
            f'<td>{int(ra["r"])}</td><td>{num(ra["m"], 4)}</td><td>{num(ra["FO"], 6)}</td>'
            f'<td>{int(rb["r"])}</td><td>{num(rb["m"], 4)}</td><td>{num(rb["FO"], 6)}</td>'
            f'<td>{("+" if d >= 0 else "−")}{abs(d):.6f}</td></tr>'.replace(".", ",", 0))
    return ('<table><tr><th class="l" rowspan="2">Escena</th>'
            '<th colspan="3">A) rango publicado [0,30; 2,00]</th>'
            '<th colspan="3">B) rango ampliado [0,01; 2,00]</th>'
            '<th rowspan="2">Δ FO</th></tr>'
            '<tr><th>r</th><th>m</th><th>FO</th><th>r</th><th>m</th><th>FO</th></tr>'
            f'{"".join(filas)}</table>')


plt.rcParams.update({"font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"]})
ROJO = "#8b1a1a"


def _b64(fig, dpi=135):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def _sat(f):
    """Fraccion de pixeles saturados (indicador de realce excesivo)."""
    return float(np.mean((f >= 0.999) | (f <= 0.001))) * 100


def figura_cualitativa(A, B, escenas):
    """Por escena: VIS, IR y la fusion en cada uno de los dos optimos."""
    pares = {Path(v).stem: (v, i) for v, i in list_pairs()}
    fig, axes = plt.subplots(len(escenas), 4, figsize=(9.4, 2.28 * len(escenas)))
    if len(escenas) == 1:
        axes = np.array([axes])
    for fila, img in enumerate(escenas):
        v, i = load_pair(*pares[img])
        ra, ma = int(A.loc[img, "r"]), float(A.loc[img, "m"])
        rb, mb = int(B.loc[img, "r"]), float(B.loc[img, "m"])
        fa = fuse_optimal(v, i, ra, ma, mode="sum")
        fb = fuse_optimal(v, i, rb, mb, mode="sum")
        paneles = [
            ("VIS", v, "black"),
            ("IR", i, "black"),
            (f"A)  r={ra}, m={ma:.2f}".replace(".", ","), fa, "black"),
            (f"B)  r={rb}, m={mb:.4f}".replace(".", ","), fb, ROJO),
        ]
        for col, (tit, im, color) in enumerate(paneles):
            ax = axes[fila, col]
            ax.imshow(np.clip(im, 0, 1), cmap="gray", vmin=0, vmax=1)
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_color(ROJO if col == 3 else "#bfbfbf")
                s.set_linewidth(1.3 if col == 3 else 0.6)
            if fila == 0:
                ax.set_title(tit, fontsize=9.5, color=color,
                             fontweight=("bold" if col == 3 else "normal"))
            else:
                ax.set_title(tit, fontsize=8.8, color=color,
                             fontweight=("bold" if col == 3 else "normal"), pad=2.5)
            if col >= 2:
                ax.set_xlabel(f"saturado {_sat(im):.1f} %".replace(".", ","),
                              fontsize=7.2, color="#666666", labelpad=1.5)
        axes[fila, 0].set_ylabel(ESCENA.get(img, img), fontsize=8.5, rotation=90,
                                 labelpad=4, va="center")
    fig.tight_layout(h_pad=1.0, w_pad=0.35)
    return _b64(fig)


CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Times New Roman', Times, serif; color: #000; font-size: 11pt; line-height: 1.45; }
.page { width: 210mm; min-height: 297mm; padding: 20mm 18mm 18mm 18mm; page-break-after: always;
        position: relative; background: #fff; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 3mm; }
h2 { font-size: 13pt; margin: 0 0 3mm 0; border-bottom: 1px solid #000; padding-bottom: 1mm; }
p { text-align: justify; margin-bottom: 2.5mm; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0; font-size: 7.8pt; }
th, td { border: 1px solid #000; padding: 0.8mm 0.7mm; text-align: center; }
th { background: #e8e8e8; font-weight: bold; }
th.l, td.l { text-align: left; padding-left: 1.5mm; }
.lectura { font-size: 9.5pt; font-style: italic; margin: 2mm 0 3mm 0; text-align: justify; }
.pie { position: absolute; bottom: 8mm; left: 18mm; right: 18mm; text-align: center; font-size: 9pt; }
.figc { text-align: center; margin: 3mm 0 2mm 0; }
.figc img { width: 100%; }
.sub { font-size: 10.5pt; text-align: center; color: #444; margin-bottom: 6mm; }
"""


def main():
    A = mejores("pso_por_imagen.csv")
    B = mejores("pso_por_imagen_libre.csv")
    orden = [i for i in ESCENA if i in A.index] or list(A.index)

    n_borde = int((A["m"] == 0.30).sum())
    m_min, m_max = float(B["m"].min()), float(B["m"].max())
    r_a = sorted(A["r"].unique().tolist())
    r_b = sorted(B["r"].unique().tolist())
    m_med = float(B["m"].mean())
    n_r25 = int((B["r"] == 25).sum())
    n_r1_a = int((A["r"] == 1).sum())
    fo_a, fo_b = float(A["FO"].mean()), float(B["FO"].mean())
    _c = lambda v, d=4: f"{v:.{d}f}".replace(".", ",")
    mmin_c, mmax_c, mmed_c = _c(m_min), _c(m_max), _c(m_med)
    foa_c, fob_c = _c(fo_a), _c(fo_b)

    H = [f"""
<div class="page">
  <h1>Resultados óptimos por imagen fusionada</h1>
  <div class="sub">Fusión VIS/IR mediante morfología matemática · Propuesta Novedosa (banco de disco
  y líneas, suma de ramas)<br>Optimización por enjambre de partículas con la aptitud
  F<sub>o</sub> = SSIM<sub>avg</sub> + E<sub>n</sub> + PSNR<sub>n</sub> (Ortega y Espinoza, 2025)</div>

  <h2>A) Óptimo con el rango publicado: m &isin; [0,30; 2,00]</h2>
  <p>Para cada uno de los 20 pares del TNO se ejecutaron las 25 configuraciones del Cuadro 1
  (partículas 2–10 × iteraciones 10–50) y se reporta <b>la de mayor aptitud</b>, con las métricas de la
  imagen fusionada en ese punto. El espacio de búsqueda es el del trabajo de referencia, sin
  modificaciones.</p>
  {tabla_optimos(A, orden)}
  <p class="lectura">Lectura: el peso óptimo es <b>m = 0,30</b> en {n_borde} de las 20 escenas, es decir
  el <b>límite inferior</b> del intervalo. No es un artefacto de la búsqueda: F<sub>o</sub> decrece de
  forma estrictamente monótona al aumentar m en todo el rango publicado —verificado con un barrido de
  paso 0,05: cero tramos crecientes en 34, con r = 1 y con r = 25—, de modo que el máximo se ubica
  necesariamente en el borde. El radio, en cambio, sí varía entre escenas
  (valores hallados: {", ".join(str(int(x)) for x in r_a)}).</p>
  <div class="pie">1</div>
</div>

<div class="page">
  <h2>B) Óptimo con el rango ampliado: m &isin; [0,01; 2,00]</h2>
  <p>El mismo barrido, ampliando el límite inferior del peso para que el óptimo de F<sub>o</sub> quede
  <b>dentro</b> del intervalo y no sobre su borde. Es el escenario que revela el óptimo real de la
  aptitud para este operador.</p>
  {tabla_optimos(B, orden)}
  <p class="lectura">Lectura: al liberar el límite inferior, el peso óptimo <b>ya varía entre escenas</b>
  (de {mmin_c} a {mmax_c}; media {mmed_c}) y se ubica muy por debajo del rango publicado. Y
  aparece el hallazgo decisivo: <b>el radio óptimo pasa a ser r = 25 en {n_r25} de las 20 escenas</b>,
  frente a r = 1 en {n_r1_a} de 20 con el rango publicado. Es decir, F<sub>o</sub> <b>sí favorece el
  banco completo de cinco elementos estructurantes</b>, siempre que se le permita un peso
  suficientemente bajo: la preferencia por r = 1 del escenario A es un <b>artefacto</b> de forzar
  m &ge; 0,30. La aptitud media también mejora ({fob_c} frente a {foa_c}).</p>
  <div class="pie">2</div>
</div>

<div class="page">
  <h2>C) Comparación de ambos escenarios</h2>
  <p>Óptimo por escena en cada rango de búsqueda y diferencia de aptitud alcanzada.</p>
  {tabla_comparativa(A, B, orden)}
  <p class="lectura">Síntesis. El óptimo de F<sub>o</sub> para el operador propuesto se encuentra
  <b>por debajo del rango publicado</b>: la aptitud premia la fidelidad a las fuentes y por lo tanto un
  realce moderado, de modo que con el intervalo original el resultado queda sistemáticamente sobre su
  borde inferior. Tres consecuencias para la interpretación. <b>(i)</b> El peso constante m = 0,30 del
  escenario A es el resultado correcto de aplicar la metodología de referencia a este operador, no una
  falla de convergencia. <b>(ii)</b> Cuando el peso puede tomar valores bajos, F<sub>o</sub> elige
  <b>r = 25 en {n_r25} de las 20 escenas</b>, de modo que la aptitud publicada <b>sí respalda el banco
  completo de cinco elementos estructurantes</b>; la preferencia por r = 1 que se observa con el rango
  original es un artefacto de la restricción sobre m, no una propiedad del operador. <b>(iii)</b> Los
  óptimos libres se concentran en r = 25 con m entre {mmin_c} y {mmax_c} (media {mmed_c}), es
  decir el entorno inmediato de la configuración r = 25, m = 0,0703 que arrojó el barrido agregado
  sobre las escenas representativas.</p>
  <div class="pie">3</div>
</div>
"""]
    # ---------- D) diferencias cualitativas ----------
    tipicas = [k for k in orden if int(B.loc[k, "r"]) == 25]
    atipicas = [k for k in orden if int(B.loc[k, "r"]) != 25]
    sel1 = tipicas[:3]
    sel2 = (tipicas[3:5] + atipicas)[:3]
    H.append(f"""
<div class="page">
  <h2>D) Diferencias cualitativas entre ambos óptimos</h2>
  <p>Para las mismas escenas se muestra la fusión obtenida en cada óptimo: <b>A)</b> el del rango
  publicado (radio pequeño con m = 0,30) y <b>B)</b> el del rango ampliado (radio grande con un peso
  bajo, recuadro rojo). Las dos alcanzan una aptitud F<sub>o</sub> parecida, pero producen imágenes
  claramente distintas.</p>
  <div class="figc"><img src="{figura_cualitativa(A, B, sel1)}"></div>
  <p class="lectura">Las diferencias son sutiles a simple vista, pero sistemáticas y medibles. El óptimo
  A, con radio de uno o dos píxeles y peso alto, transfiere detalle de <b>grano fino</b>: mayor
  frecuencia espacial (SF media 12,55 frente a 8,86 de B) a costa de la fidelidad. El óptimo B, con
  r = 25 y un peso unas seis veces menor, transfiere <b>estructura de gran escala</b> con un realce
  suave: mayor similitud estructural en <b>19 de las 20 escenas</b> (SSIM media 0,787 frente a 0,759) y
  mayor PSNR en 15 de 20, con saturación prácticamente nula. La cantidad total de realce es comparable
  —el producto del peso por la energía del operador—; lo que cambia es la <b>escala</b> de las
  estructuras transferidas y, con ella, el balance entre fidelidad y actividad.</p>
  <div class="pie">4</div>
</div>

<div class="page">
  <h2>D) Diferencias cualitativas (continuación)</h2>
  <div class="figc"><img src="{figura_cualitativa(A, B, sel2)}"></div>
  <p class="lectura">Las últimas escenas incluyen los casos atípicos del escenario B, donde el óptimo
  libre no fue r = 25 sino un radio intermedio o mínimo. En conjunto, la comparación respalda la lectura
  cuantitativa y aclara <b>por qué</b> F<sub>o</sub> elige el radio grande en 17 de 20 escenas: no
  porque agregue más detalle, sino porque un elemento estructurante amplio con un peso bajo transfiere
  la estructura de la escena de forma <b>más suave y más fiel a las fuentes</b> —y F<sub>o</sub>, al
  estar dominada por SSIM y PSNR, premia precisamente eso (la prefiere en las 20 escenas). La
  restricción m &ge; 0,30 fuerza el efecto contrario: obliga a un realce intenso, que solo resulta
  tolerable para la aptitud si el radio se reduce al mínimo. Es decir, el rango de búsqueda no solo
  desplaza el óptimo numérico: <b>determina el carácter de la fusión resultante</b>.</p>
  <div class="pie">5</div>
</div>
""")

    html = (f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">'
            f'<title>Resultados óptimos por imagen</title><style>{CSS}</style></head>'
            f'<body>{"".join(H)}</body></html>')
    with open(HTML_OUT, "w", encoding="utf-8") as fh:
        fh.write(html)
    print("HTML:", HTML_OUT)

    edge = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge):
        edge = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    if os.path.exists(edge):
        subprocess.run([edge, "--headless", "--disable-gpu", f"--print-to-pdf={PDF_OUT}",
                        "--no-pdf-header-footer", HTML_OUT], capture_output=True, timeout=300)
        if os.path.exists(PDF_OUT):
            print("PDF:", PDF_OUT, f"{os.path.getsize(PDF_OUT)/1e6:.2f} MB")
        else:
            print("AVISO: Edge no genero el PDF.")
    else:
        print("AVISO: Edge no encontrado; imprimir el HTML manualmente.")


if __name__ == "__main__":
    main()
