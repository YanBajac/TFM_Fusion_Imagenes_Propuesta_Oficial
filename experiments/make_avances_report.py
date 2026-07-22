# -*- coding: utf-8 -*-
"""Genera docs/Avances_Tesis.pdf — informe de avances (diseno simple tipo Word).
Propuesta con SUMA de ramas (r=25, m=0.0703) vs 6 comparativos (LP, RP, DWT, DTCWT,
CVT, Top-Hat clasico) + deteccion LLVIP. Requiere Microsoft Edge para el paso HTML->PDF.
Uso: python experiments/make_avances_report.py"""
import base64, io, json, os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
warnings.filterwarnings("ignore")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FIG  = os.path.join(ROOT, "docs", "figures")
CUAL = os.path.join(FIG, "cualitativas")
MR   = os.path.join(ROOT, "experiments", "results", "metrics_reports")
OUT  = os.path.join(ROOT, "docs", "_local")
os.makedirs(OUT, exist_ok=True)
HTML_OUT = os.path.join(OUT, "Avances_Tesis.html")
PDF_OUT  = os.path.join(ROOT, "docs", "Avances_Tesis.pdf")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 10, "axes.grid": True, "grid.alpha": 0.3, "grid.linewidth": 0.5,
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
})

def b64(data, mime="image/png"):
    return f"data:{mime};base64," + base64.b64encode(data).decode()

def fig_to_b64(fig, dpi=150):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return b64(buf.getvalue())

def file_img_b64(path, max_w=1400, jpeg_q=85):
    im = Image.open(path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > max_w:
        im = im.resize((max_w, int(im.height * max_w / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=jpeg_q)
    return b64(buf.getvalue(), "image/jpeg")

def formula_b64(tex, fs=14):
    fig = plt.figure(figsize=(0.1, 0.1))
    t = fig.text(0, 0, f"${tex}$", fontsize=fs, color="black")
    fig.canvas.draw()
    bb = t.get_window_extent()
    fig.set_size_inches(bb.width / fig.dpi + 0.15, bb.height / fig.dpi + 0.12)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=220, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return b64(buf.getvalue())

# ------------------------------------------------------------------ datos
means = pd.read_csv(os.path.join(MR, "descriptive_means.csv")).set_index("method")
fried = pd.read_csv(os.path.join(MR, "friedman_results.csv"))
wilc  = pd.read_csv(os.path.join(MR, "wilcoxon_results.csv"))
rankm = pd.read_csv(os.path.join(MR, "ranking_methods.csv"), index_col=0)
grid  = pd.read_csv(os.path.join(MR, "pso_grid_search.csv"))
det   = pd.read_csv(os.path.join(MR, "detection_llvip_map.csv")).set_index("method")
pso_grid = json.load(open(os.path.join(ROOT, "experiments", "results", "pso",
                                       "pso_grid_state.json")))

PROP = "Propuesta_Novedosa"
ORDEN = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", PROP]
LBL = {"PiramideLaplace": "Pirámide de Laplace (LP)",
       "RatioPiramide": "Ratio of low-pass Pyramid (RP)",
       "DWT": "Wavelet discreta (DWT)",
       "DTCWT": "Dual-Tree Complex Wavelet (DTCWT)",
       "Curvelet": "Curvelet (CVT)",
       "TopHat_Clasico": "Top-Hat clásico",
       PROP: "Propuesta novedosa (r=25, m=0,070)"}
SHORT = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT",
         "Curvelet": "CVT", "TopHat_Clasico": "TH clás.", PROP: "Propuesta"}
DIRECTION = {"EN": 1, "SD": 1, "FE": 1, "MG": 1, "MI_vis": 1, "MI_ir": 1, "SF": 1,
             "Qabf": 1, "Nabf": -1, "SSIM": 1, "SCD": 1, "VIF": 1}
METS = list(DIRECTION.keys())

def tabla_metodos(methods, resaltar=None):
    best = {}
    for mk in METS:
        vals = {m: means.loc[m, mk] for m in methods}
        best[mk] = (max if DIRECTION[mk] > 0 else min)(vals, key=vals.get)
    head = "".join(f'<th>{mk}&nbsp;{"↑" if DIRECTION[mk] > 0 else "↓"}</th>' for mk in METS)
    rows = []
    for m in methods:
        tds = []
        for mk in METS:
            v = means.loc[m, mk]
            b = "<b>" if best.get(mk) == m else ""
            tds.append(f'<td>{b}{v:.3f}{"</b>" if b else ""}</td>')
        name = LBL.get(m, m)
        if m == resaltar:
            name = f"<b>{name}</b>"
        rows.append(f'<tr><td class="l">{name}</td>{"".join(tds)}</tr>')
    return (f'<table><tr><th class="l">Método</th>{head}</tr>{"".join(rows)}</table>')

n_best_prop = sum(1 for mk in METS
                  if (max if DIRECTION[mk] > 0 else min)(
                      {m: means.loc[m, mk] for m in ORDEN},
                      key=lambda k: {m: means.loc[m, mk] for m in ORDEN}[k]) == PROP)

# ------------------------------------------------------------------ graficas
charts = {}
AZUL = "#4472c4"; GRIS = "#a6a6a6"

# convergencia comparada: una curva por numero de particulas (T=50)
fig, ax = plt.subplots(figsize=(7.2, 3.2))
tonos = {2: "#c9c9c9", 4: "#9db4c0", 6: "#7a97ab", 8: "#5b7f99", 10: "#4472c4"}
for n in [2, 4, 6, 8, 10]:
    h = pso_grid["configs"][f"n{n}_T50"]["history"]
    ax.plot([x["it"] for x in h], [x["gbest_fit"] for x in h], "-",
            color=tonos[n], lw=2 if n == 10 else 1.2, label=f"n = {n}")
ax.set_xlabel("Iteración"); ax.set_ylabel("Mejor aptitud F")
ax.set_title("Convergencia del PSO según el número de partículas (Tmax = 50)", fontsize=11)
ax.legend(frameon=False, fontsize=8, ncol=5, loc="lower right")
charts["pso"] = fig_to_b64(fig)

# tabla 5x5 del barrido (F* por configuracion)
gbest_F = grid["F_opt"].max()
piv = grid.pivot(index="n", columns="Tmax", values="F_opt")
filas_grid = []
for n in [2, 4, 6, 8, 10]:
    tds = []
    for T in [10, 20, 30, 40, 50]:
        v = piv.loc[n, T]
        b = "<b>" if abs(v - gbest_F) < 5e-4 else ""
        tds.append(f"<td>{b}{v:.4f}{'</b>' if b else ''}</td>")
    filas_grid.append(f'<tr><td class="l"><b>n = {n}</b></td>{"".join(tds)}</tr>')
tabla_grid = ('<table class="chica"><tr><th class="l">Partículas \\ Iteraciones</th>'
              + "".join(f"<th>T = {T}</th>" for T in [10, 20, 30, 40, 50])
              + f'</tr>{"".join(filas_grid)}</table>')

key = ["Qabf", "Nabf", "SSIM", "SCD"]
fig, axes = plt.subplots(1, 4, figsize=(12.0, 2.9))
for ax, mk in zip(axes, key):
    vals = [means.loc[m, mk] for m in ORDEN]
    cols = [AZUL if m == PROP else GRIS for m in ORDEN]
    ax.bar(range(len(ORDEN)), vals, color=cols, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=6.3)
    ax.set_title(f'{mk} ({"menor mejor" if mk == "Nabf" else "mayor mejor"})', fontsize=9)
    ax.set_xticks(range(len(ORDEN)))
    ax.set_xticklabels([SHORT[m] for m in ORDEN], fontsize=6.5, rotation=30, ha="right")
    ax.margins(y=0.18)
fig.tight_layout()
charts["quality"] = fig_to_b64(fig)

rk = rankm["avg_rank"].sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.6, 2.9))
cols = [AZUL if n == PROP else GRIS for n in rk.index]
ax.barh(range(len(rk)), rk.values, color=cols, height=0.62)
ax.set_yticks(range(len(rk)))
ax.set_yticklabels([LBL.get(n, n) for n in rk.index], fontsize=8)
for i, v in enumerate(rk.values):
    ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=7.5)
ax.set_xlabel("Ranking promedio en 12 métricas (menor = mejor)", fontsize=9)
ax.margins(x=0.12)
charts["ranking"] = fig_to_b64(fig)

# --- detección LLVIP: barras mAP por método ---
_dord = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", "Propuesta_Novedosa"]
_dshort = {"VIS": "VIS", "IR": "IR", "PiramideLaplace": "LP", "RatioPiramide": "RP",
           "DWT": "DWT", "DTCWT": "DTCWT", "Curvelet": "CVT", "TopHat_Clasico": "TH clás.",
           "Propuesta_Novedosa": "Propuesta"}
dd = det.loc[_dord]
fig, ax = plt.subplots(figsize=(7.4, 3.0))
x = np.arange(len(_dord)); w = 0.4
ax.bar(x - w/2, dd["mAP50"], w, label="mAP@0,5", color=AZUL)
ax.bar(x + w/2, dd["mAP50_95"], w, label="mAP@0,5:0,95", color=GRIS)
for xi, (a, b) in enumerate(zip(dd["mAP50"], dd["mAP50_95"])):
    ax.text(xi - w/2, a, f"{a:.2f}".replace(".", ","), ha="center", va="bottom", fontsize=6)
ax.set_xticks(x); ax.set_xticklabels([_dshort[m] for m in _dord], fontsize=7.5, rotation=25, ha="right")
ax.set_ylim(0, 1.05); ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_ylabel("mAP", fontsize=9)
charts["det"] = fig_to_b64(fig)

# wilcoxon: propuesta vs cada rival (tabla resumen)
wp = wilc[wilc["tophat"] == PROP].copy()
rivales_w = [m for m in ORDEN if m != PROP and m in set(wp["baseline"])]
wtab = {}
for _, r in wp.iterrows():
    d = DIRECTION[r["metric"]]
    sig = r["p_holm"] < 0.05
    mejor = (r["mean_tophat"] - r["mean_baseline"]) * d > 0
    wtab[(r["metric"], r["baseline"])] = "≈" if not sig else ("mejor" if mejor else "peor")
rows = []
for mk in METS:
    tds = "".join(f'<td>{wtab.get((mk, rv), "—")}</td>' for rv in rivales_w)
    rows.append(f'<tr><td class="l">{mk}</td>{tds}</tr>')
tabla_wilcoxon = ('<table class="chica"><tr><th class="l">Métrica</th>'
                  + "".join(f"<th>vs. {SHORT[r]}</th>" for r in rivales_w)
                  + f'</tr>{"".join(rows)}</table>')
w_mejor = sum(1 for v in wtab.values() if v == "mejor")
w_peor = sum(1 for v in wtab.values() if v == "peor")
w_emp = sum(1 for v in wtab.values() if v == "≈")
print("charts ok | propuesta mejor columnas:", n_best_prop,
      f"| wilcoxon {w_mejor}m/{w_peor}p/{w_emp}e")

# ------------------------------------------------------------------ formulas
F = {
 "dil_ero": r"\delta(f,b)(x,y)=\max_{(s,t)\in b} f(x+s,\,y+t) \qquad \varepsilon(f,b)(x,y)=\min_{(s,t)\in b} f(x+s,\,y+t)",
 "open_close": r"\gamma(f,b)=\delta(\varepsilon(f,b),\,b) \qquad \varphi(f,b)=\varepsilon(\delta(f,b),\,b)",
 "tophat": r"WTH(f,b)=f-\gamma(f,b) \qquad BTH(f,b)=\varphi(f,b)-f",
 "se_disco": r"B_r=\left\{(x,y)\in\mathbb{Z}^2 \,:\, x^2+y^2\leq r^2\right\}",
 "se_lineas": r"L_{r,\theta}\subset\mathbb{Z}^2,\quad \left|L_{r,\theta}\right|=2r+1,\qquad \theta\in\left\{0^\circ,\,45^\circ,\,90^\circ,\,135^\circ\right\}",
 "wth_theta": r"WTH_{\theta}(f)=f-\gamma\!\left(f,\,L_{r,\theta}\right),\qquad \theta\in\left\{0^\circ,45^\circ,90^\circ,135^\circ\right\}",
 "wth_lin4": r"WTH_{lin}(f)=\frac{1}{4}\left[\,WTH_{0^\circ}(f)+WTH_{45^\circ}(f)+WTH_{90^\circ}(f)+WTH_{135^\circ}(f)\,\right]",
 "bth_theta": r"BTH_{\theta}(f)=\varphi\!\left(f,\,L_{r,\theta}\right)-f,\qquad \theta\in\left\{0^\circ,45^\circ,90^\circ,135^\circ\right\}",
 "bth_lin4": r"BTH_{lin}(f)=\frac{1}{4}\left[\,BTH_{0^\circ}(f)+BTH_{45^\circ}(f)+BTH_{90^\circ}(f)+BTH_{135^\circ}(f)\,\right]",
 "wth_disc": r"WTH_{disco}(f)=f-\gamma\!\left(f,\,B_r\right) \qquad BTH_{disco}(f)=\varphi\!\left(f,\,B_r\right)-f",
 "wth_sum": r"WTH(f)=WTH_{lin}(f)+WTH_{disco}(f)",
 "bth_sum": r"BTH(f)=BTH_{lin}(f)+BTH_{disco}(f)",
 "fuse_src": r"WTH^{F}(x,y)=\max\!\left(WTH^{VIS}(x,y),\;WTH^{IR}(x,y)\right) \qquad BTH^{F}(x,y)=\max\!\left(BTH^{VIS}(x,y),\;BTH^{IR}(x,y)\right)",
 "recon": r"F = I_{base} + m\cdot WTH^{F} - m\cdot BTH^{F}\,,\qquad I_{base}=\frac{VIS+IR}{2}\,,\qquad m>0",
 "pso_v": r"v_k^{t+1}=\omega\, v_k^{t}+c_1 r_1\left(p_k-x_k^{t}\right)+c_2 r_2\left(g-x_k^{t}\right) \qquad x_k^{t+1}=x_k^{t}+v_k^{t+1}",
 "pso_fit": r"F_{apt}(r,m)= SSIM + Q^{AB/F} + 0.5\cdot SCD - N^{AB/F} \;\longrightarrow\; \max",
 "th_clasico": r"F_{TH}=\frac{VIS+IR}{2}+\max\!\left(WTH^{VIS}_{B_5},WTH^{IR}_{B_5}\right)-\max\!\left(BTH^{VIS}_{B_5},BTH^{IR}_{B_5}\right)",
 "en": r"EN=-\sum_{l=0}^{255} p_l\,\log_2 p_l \qquad SD=\sqrt{\frac{1}{MN}\sum_{i,j}\left(F(i,j)-\mu\right)^2}",
 "mg_sf": r"MG=\frac{1}{MN}\sum_{i,j}\sqrt{\frac{(\nabla_x F)^2+(\nabla_y F)^2}{2}} \qquad SF=\sqrt{RF^2+CF^2}",
 "mi": r"MI_{X}=\sum_{f,x} p_{F,X}(f,x)\,\log_2\frac{p_{F,X}(f,x)}{p_F(f)\,p_X(x)}\,,\quad X\in\{VIS, IR\}",
 "qabf": r"Q^{AB/F}=\frac{\sum_{i,j}\left(Q^{AF}w^{A}+Q^{BF}w^{B}\right)}{\sum_{i,j}\left(w^{A}+w^{B}\right)}",
 "ssim": r"SSIM(x,y)=\frac{\left(2\mu_x\mu_y+C_1\right)\left(2\sigma_{xy}+C_2\right)}{\left(\mu_x^2+\mu_y^2+C_1\right)\left(\sigma_x^2+\sigma_y^2+C_2\right)}",
 "scd": r"SCD=r\!\left(F-IR,\;VIS\right)+r\!\left(F-VIS,\;IR\right)",
 "friedman": r"\chi^2_F=\frac{12N}{k(k+1)}\left[\sum_{j=1}^{k}R_j^2-\frac{k(k+1)^2}{4}\right]",
 "rb": r"r_{rb}=1-\frac{2W}{n(n+1)/2}",
}
FORM = {k: formula_b64(v) for k, v in F.items()}
print("formulas ok")

# ------------------------------------------------------------------ imagenes
VIS_D = os.path.join(ROOT, "data", "raw", "VIS"); IR_D = os.path.join(ROOT, "data", "raw", "IR")
pairs_html = []
for idx, nm in enumerate(sorted(os.listdir(VIS_D)), 1):
    v = Image.open(os.path.join(VIS_D, nm)).convert("L")
    r = Image.open(os.path.join(IR_D, nm)).convert("L")
    Hh = 220
    v = v.resize((int(v.width * Hh / v.height), Hh), Image.LANCZOS)
    r = r.resize((int(r.width * Hh / r.height), Hh), Image.LANCZOS)
    canvas = Image.new("RGB", (v.width + r.width + 8, Hh), (255, 255, 255))
    canvas.paste(v.convert("RGB"), (0, 0)); canvas.paste(r.convert("RGB"), (v.width + 8, 0))
    buf = io.BytesIO(); canvas.save(buf, "JPEG", quality=84)
    pairs_html.append(
        f'<div class="par"><img src="{b64(buf.getvalue(), "image/jpeg")}">'
        f'<div class="cap">Par {idx:02d}: {nm.rsplit(".", 1)[0]} (izq. VIS, der. IR)</div></div>')
mont_html = []
for i in range(1, 21):
    mont_html.append(f'<div class="mont"><img src="{file_img_b64(os.path.join(CUAL, f"montaje_{i:02d}.png"), 1350, 84)}"></div>')
def fig_file(name, max_w=1350):
    p = os.path.join(FIG, name)
    return file_img_b64(p, max_w=max_w) if os.path.exists(p) else None
EXIST = {n: fig_file(n) for n in [
    "fig_morfologia_tophat.png", "fig_cinco_se.png", "fig_pso_diagrama.png",
    "ejemplo_modalidades.png", "fig_aptitud_vs_m.png"]}
print("imagenes ok")

def tabla_friedman():
    rows = "".join(f'<tr><td class="l">{r.metric}</td><td>{r.chi2:.1f}</td>'
                   f'<td>{r.p_value:.1e}</td><td>{"Sí" if r.significant_05 else "No"}</td></tr>'
                   for r in fried.itertuples())
    return ('<table class="chica"><tr><th class="l">Métrica</th><th>χ² de Friedman</th>'
            f'<th>p-valor</th><th>Significativa (α = 0,05)</th></tr>{rows}</table>')

DET_ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
             "Curvelet", "TopHat_Clasico", PROP]
DET_LBL = {"VIS": "VIS (solo)", "IR": "IR (solo)", **LBL}
def tabla_det():
    best50 = det["mAP50"].idxmax(); best5095 = det["mAP50_95"].idxmax()
    bestp = det["precision"].idxmax(); bestr = det["recall"].idxmax()
    rows = []
    for m in DET_ORDEN:
        r = det.loc[m]
        nm = DET_LBL.get(m, m)
        if m == PROP:
            nm = f"<b>{nm}</b>"
        def c(v, isbest):
            s = f"{v:.3f}".replace(".", ",")
            return f"<b>{s}</b>" if isbest else s
        rows.append(f'<tr><td class="l">{nm}</td><td>{c(r.mAP50, m==best50)}</td>'
                    f'<td>{c(r.mAP50_95, m==best5095)}</td><td>{c(r.precision, m==bestp)}</td>'
                    f'<td>{c(r.recall, m==bestr)}</td></tr>')
    return ('<table class="chica"><tr><th class="l">Entrada</th><th>mAP@0,5 ↑</th>'
            '<th>mAP@0,5:0,95 ↑</th><th>Precisión ↑</th><th>Recall ↑</th></tr>'
            f'{"".join(rows)}</table>')

# ------------------------------------------------------------------ HTML
def formula(key, num):
    return (f'<div class="formula"><img src="{FORM[key]}"><span class="eq">({num})</span></div>')

def figura(src, cap, w=88, n=[0]):
    if src is None:
        return ""
    n[0] += 1
    return (f'<div class="figc" style="width:{w}%"><img src="{src}">'
            f'<div class="cap">Figura {n[0]}. {cap}</div></div>')

css = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Times New Roman', Times, serif; color: #000; font-size: 11pt; line-height: 1.45; }
.page { width: 210mm; min-height: 297mm; padding: 20mm 20mm 18mm 20mm; page-break-after: always;
        position: relative; background: #fff; }
h1 { font-size: 16pt; text-align: center; margin-bottom: 4mm; }
h2 { font-size: 13pt; margin: 0 0 3mm 0; border-bottom: 1px solid #000; padding-bottom: 1mm; }
h3 { font-size: 11.5pt; margin: 4mm 0 1.5mm 0; }
p { text-align: justify; margin-bottom: 2.5mm; }
.formula { text-align: center; margin: 3mm 0; position: relative; }
.formula img { max-height: 12mm; max-width: 90%; vertical-align: middle; }
.eq { position: absolute; right: 0; top: 50%; transform: translateY(-50%); font-size: 10pt; }
.figc { margin: 3mm auto; text-align: center; }
.figc img { max-width: 100%; }
.cap { font-size: 9pt; margin-top: 1mm; text-align: center; }
table { border-collapse: collapse; width: 100%; margin: 2.5mm 0; font-size: 8pt; }
table.chica { width: 78%; margin-left: auto; margin-right: auto; font-size: 9pt; }
th, td { border: 1px solid #000; padding: 1.2mm 1mm; text-align: center; }
th { background: #e8e8e8; font-weight: bold; }
th.l, td.l { text-align: left; padding-left: 2mm; }
.lectura { font-size: 9.5pt; font-style: italic; margin: 1.5mm 0 3mm 0; text-align: justify; }
.grid2 { display: flex; flex-wrap: wrap; gap: 3mm 4mm; justify-content: space-between; }
.par { width: calc(50% - 2.5mm); margin-bottom: 2mm; }
.par img { width: 100%; border: 1px solid #999; }
.mont { margin-bottom: 4mm; text-align: center; }
.mont img { width: 88%; border: 1px solid #999; }
.pie { position: absolute; bottom: 8mm; left: 20mm; right: 20mm; text-align: center; font-size: 9pt; }
ul, ol { margin: 1.5mm 0 2.5mm 7mm; }
li { margin-bottom: 1mm; text-align: justify; }
.portada { display: flex; flex-direction: column; justify-content: center; text-align: center; }
.portada .t1 { font-size: 12pt; margin-bottom: 18mm; }
.portada h1 { font-size: 18pt; margin-bottom: 8mm; }
.portada .t2 { font-size: 12pt; margin-bottom: 22mm; }
.portada .datos { font-size: 11.5pt; line-height: 2.1; }
"""

def pie(n):
    return f'<div class="pie">{n}</div>'

H = []
H.append("""
<div class="page portada">
  <div class="t1">Universidad Comunera (UCOM)<br>Maestría en Ciencias de Datos</div>
  <h1>Fusión de imágenes infrarrojas y visibles<br>mediante morfología matemática</h1>
  <div class="t2">Presentación de avances<br>Propuesta Top-Hat de una escala (suma de ramas) frente al estado del arte</div>
  <div class="datos">
    Autores: Lic. Juan Pablo Bazán — Ing. Yan Bajac<br>
    Director: D.Sc. Julio César Mello<br>
    13 de julio de 2026
  </div>
</div>
""")

H.append(f"""
<div class="page">
  <h2>1. Introducción y esquema general</h2>
  <p>Este informe documenta el planteamiento vigente del proyecto. La propuesta central es un método de
  fusión VIS+IR basado en la transformada Top-Hat que, sobre una única escala definida por el radio r,
  combina por <b>suma</b> la respuesta promediada de cuatro elementos estructurantes lineales con la de
  un disco, y reconstruye con el esquema aditivo-sustractivo con peso de contraste m. Los
  hiperparámetros (r, m) se optimizan por enjambre de partículas (PSO).</p>
  <p>La evaluación compara la propuesta contra <b>seis métodos</b>: cinco representativos del estado del
  arte en fusión multiescala —Pirámide de Laplace (LP), Ratio of low-pass Pyramid (RP), Wavelet discreta
  (DWT), Dual-Tree Complex Wavelet (DTCWT) y Curvelet (CVT)— más la <b>metodología clásica de la
  transformada Top-Hat</b>, sobre los 20 pares del TNO Image Fusion Dataset con 12 métricas sin
  referencia y análisis estadístico no paramétrico.</p>
  <p>El orden del documento:</p>
  <ol>
    <li>Datos de entrada: 20 pares VIS/IR del dataset TNO (sección 2).</li>
    <li>Fundamentos: operadores morfológicos y transformada Top-Hat (sección 3).</li>
    <li>Propuesta novedosa: formulación completa, ecuaciones 4–15 (sección 4).</li>
    <li>Optimización de (r, m) por PSO (sección 5).</li>
    <li>Métodos comparativos del benchmark (sección 6).</li>
    <li>Métricas de evaluación con sus fórmulas (sección 7).</li>
    <li>Resultados cuantitativos: tabla general y gráficas (sección 8).</li>
    <li>Análisis estadístico: Friedman, Wilcoxon-Holm y ranking (sección 9).</li>
    <li>Resultados cualitativos de las 20 escenas (sección 10).</li>
    <li>Evaluación orientada a tarea (sección 11), ablación de la función de aptitud (sección 12),
        clases complementarias en M3FD (sección 13) y conclusiones (sección 14).</li>
  </ol>
  {pie(2)}
</div>
""")

chunks = [pairs_html[0:8], pairs_html[8:16], pairs_html[16:20]]
H.append(f"""
<div class="page">
  <h2>2. Datos de entrada: 20 pares VIS/IR (TNO)</h2>
  <p>Se trabaja con los 20 pares registrados del TNO Image Fusion Dataset (escenas de vigilancia
  nocturna: vehículos, personas, humo). Cada escena tiene una imagen visible (VIS), que aporta textura y
  contexto, y una infrarroja (IR), que registra la radiación térmica. Ambas comparten nombre de archivo
  para el emparejado automático. Sobre estos 20 pares se calculan todas las métricas del informe.</p>
  <div class="grid2">{"".join(chunks[0])}</div>
  {pie(3)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[1])}</div>
  {pie(4)}
</div>
<div class="page">
  <h2>2. Datos de entrada (continuación)</h2>
  <div class="grid2">{"".join(chunks[2])}</div>
  {pie(5)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>3. Fundamentos: morfología matemática y Top-Hat</h2>
  <p>Dado un elemento estructurante (SE) <i>b</i>, la dilatación toma el máximo local y la erosión el mínimo:</p>
  {formula("dil_ero", 1)}
  <p>Su composición define la apertura γ, que elimina objetos claros menores que el SE, y el cierre φ, que
  rellena huecos oscuros menores que el SE:</p>
  {formula("open_close", 2)}
  <p>La transformada Top-Hat conserva exactamente lo que la apertura o el cierre eliminan: la White Top-Hat
  (WTH) extrae el detalle brillante fino y la Black Top-Hat (BTH) el detalle oscuro fino:</p>
  {formula("tophat", 3)}
  {figura(EXIST.get("fig_morfologia_tophat.png"), "Efecto de las operaciones morfológicas y de las transformadas WTH/BTH sobre una señal del dataset.", 80)}
  {pie(6)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>4. Propuesta novedosa: una escala, disco + líneas, suma de ramas</h2>
  <h3>4.1 Elementos estructurantes</h3>
  <p>En la escala de radio r se emplean cinco elementos estructurantes: un <b>disco</b> B<sub>r</sub>,
  isótropo (ecuación 4), y cuatro <b>segmentos lineales</b> L<sub>r,θ</sub> de longitud 2r+1 píxeles,
  orientados a 0°, 45°, 90° y 135° (ecuación 5):</p>
  {formula("se_disco", 4)}
  {formula("se_lineas", 5)}
  {figura(EXIST.get("fig_cinco_se.png"), "Banco de cinco elementos estructurantes (un disco y cuatro líneas) de la escala de radio r.", 62)}
  <h3>4.2 Respuestas White Top-Hat direccionales y su promedio</h3>
  <p>Para cada orientación θ, la White Top-Hat con el segmento L<sub>r,θ</sub> extrae las estructuras
  <b>brillantes</b> finas alineadas con esa dirección:</p>
  {formula("wth_theta", 6)}
  <p>Las cuatro respuestas direccionales se <b>promedian</b>, de modo que ninguna orientación queda
  privilegiada y el ruido direccional se atenúa:</p>
  {formula("wth_lin4", 7)}
  {pie(7)}
</div>
<div class="page">
  <h2>4. Propuesta novedosa (continuación)</h2>
  <h3>4.3 Respuestas Black Top-Hat direccionales y su promedio</h3>
  <p>El mismo desglose se aplica al detalle <b>oscuro</b> con el cierre φ:</p>
  {formula("bth_theta", 8)}
  {formula("bth_lin4", 9)}
  <h3>4.4 Respuesta del disco</h3>
  <p>En paralelo, el disco B<sub>r</sub> captura las estructuras brillantes y oscuras sin orientación
  predominante (manchas, objetivos térmicos compactos):</p>
  {formula("wth_disc", 10)}
  <h3>4.5 Operador combinado por suma</h3>
  <p>El operador de la propuesta <b>suma</b> la respuesta lineal promediada y la del disco, de modo que el
  realce acumula la evidencia de ambas ramas: donde una estructura es a la vez direccional e isótropa,
  ambas contribuyen (esquema de Bala et al., 2024):</p>
  {formula("wth_sum", 11)}
  {formula("bth_sum", 12)}
  <h3>4.6 Combinación entre fuentes y reconstrucción</h3>
  <p>Entre fuentes se conserva, píxel a píxel, el detalle <b>dominante</b>, y la imagen fusionada suma el
  detalle brillante y resta el oscuro sobre la base, ponderados por el peso de contraste m:</p>
  {formula("fuse_src", 13)}
  {formula("recon", 14)}
  {pie(8)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>5. Optimización de (r, m) por PSO: barrido de configuraciones</h2>
  <p>Cada partícula k es un candidato (r, m) que se mueve atraído por su mejor posición personal
  p<sub>k</sub> y por la mejor global g, con inercia ω decreciente linealmente de 0,9 a 0,4 y
  c1 = c2 = 1,5:</p>
  {formula("pso_v", 15)}
  <p>La función de aptitud está orientada a la calidad de fusión: premia estructura (SSIM), bordes
  transferidos (Q<sup>AB/F</sup>) y correlación de diferencias (SCD), y penaliza los artefactos
  (N<sup>AB/F</sup>):</p>
  {formula("pso_fit", 16)}
  <p>Para elegir la configuración del enjambre se replicó el diseño experimental de Ortega y
  Espinoza (2025): se evaluaron sistemáticamente combinaciones con número de partículas variando de
  2 a 10 en incrementos de 2 y número de iteraciones de 10 a 50 en incrementos de 10, es decir,
  <b>25 configuraciones</b>. El espacio de búsqueda adopta el rango del mismo trabajo para el radio,
  r ∈ [1, 25]; para el peso se usa m ∈ [0,05; 1,20], porque el operador con suma de cinco respuestas
  inyecta más energía de detalle que el disco único de aquel trabajo y requiere pesos menores. Cada
  configuración se ejecutó con semilla propia sobre las escenas representativas del TNO.</p>
  <p><b>Tabla 1.</b> Resultado del barrido: mejor aptitud F alcanzada por cada configuración
  (en negrita las que alcanzan el óptimo global).</p>
  {tabla_grid}
  <p class="lectura">Lectura: los enjambres de 2 partículas quedan atrapados en el óptimo local
  r = 1 (F ≈ 1,909) en tres de cinco corridas; desde n = 4 el óptimo global aparece de forma
  esporádica, y con <b>n = 10 y T ≥ 30</b> se alcanza consistentemente. El óptimo global del barrido
  es <b>r = 25, m = 0,070</b> con F = 1,9843.</p>
  {pie(9)}
</div>
<div class="page">
  <h2>5. Optimización por PSO (continuación): convergencia y óptimo</h2>
  {figura(charts["pso"], "Convergencia del mejor global según el número de partículas (Tmax = 50): los enjambres grandes escapan del óptimo local r = 1 y alcanzan F = 1,9843.", 84)}
  <p>El radio óptimo se ubica en el extremo superior del rango del barrido (r = 25, elementos
  estructurantes de 51 píxeles): el operador aprovecha un vecindario amplio para capturar los
  objetivos térmicos completos (personas, vehículos), mientras el peso m = 0,070 mantiene el realce
  conservador que la aptitud exige al penalizar artefactos. Estos hiperparámetros definen la
  configuración final de la propuesta usada en todo el benchmark.</p>
  <p>La comparación con el trabajo de referencia es directa: con el mismo diseño experimental
  y el mismo rango de radio, aquel operador (disco único, aptitud de fidelidad) convergía a un
  realce conservador; el operador propuesto (disco + líneas por suma, aptitud orientada a
  fusión) aprovecha el radio máximo disponible con un peso un orden de magnitud menor, reflejo
  de que la suma de cinco respuestas concentra más energía de detalle por unidad de peso.</p>
  {pie(10)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>6. Métodos comparativos del benchmark</h2>
  <p>La propuesta se contrasta con cinco métodos representativos del estado del arte en fusión de
  imágenes visibles e infrarrojas, más la metodología clásica de la transformada Top-Hat:</p>
  <ul>
    <li><b>Pirámide de Laplace (LP)</b> — Burt y Adelson: separa frecuencias mediante filtros gaussianos
        y laplacianos (4 niveles); el detalle se combina por máxima actividad local.</li>
    <li><b>Ratio of low-pass Pyramid (RP)</b> — Toet (1989): utiliza razones entre niveles gaussianos
        consecutivos, R = G<sub>l</sub>/expand(G<sub>l+1</sub>); se conserva en cada píxel la razón que
        más se aparta de 1 (mayor contraste local) y se reconstruye multiplicativamente.</li>
    <li><b>Wavelet discreta (DWT)</b>: descompone en subbandas de detalle y aproximación (Haar, 3
        niveles); detalle por máxima magnitud de coeficiente, aproximación por promedio.</li>
    <li><b>Dual-Tree Complex Wavelet (DTCWT)</b> — Kingsbury: mejora la DWT con invariancia al
        desplazamiento y seis subbandas direccionales complejas por nivel (4 niveles); fusión por máxima
        magnitud compleja.</li>
    <li><b>Curvelet (CVT)</b> — Candès et al.: captura estructuras anisótropas y curvas mediante
        elementos base direccionales (aproximación vía wavelet db4, 3 niveles).</li>
    <li><b>Top-Hat clásico</b>: la fusión morfológica básica con un único disco B<sub>5</sub>, detalle
        entre fuentes por máximo y reconstrucción sin ponderación (m = 1):</li>
  </ul>
  {formula("th_clasico", 17)}
  <p>Todos los métodos se ejecutan sobre los mismos 20 pares, con la misma implementación de métricas
  (<i>src/metrics/evaluators.py</i>), de modo que la comparación es directa.</p>
  {pie(11)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>7. Métricas de evaluación</h2>
  <p>Las 12 métricas, todas sin referencia (no existe imagen fusionada ideal):</p>
  <p>Entropía y desviación estándar (información y contraste):</p>
  {formula("en", 18)}
  <p>Gradiente medio y frecuencia espacial (nitidez y actividad):</p>
  {formula("mg_sf", 19)}
  <p>Información mutua con cada fuente:</p>
  {formula("mi", 20)}
  <p>Preservación de bordes de Xydeas-Petrović (su complemento N<sup>AB/F</sup> mide los artefactos):</p>
  {formula("qabf", 21)}
  <p>Similitud estructural y correlación de las diferencias:</p>
  {formula("ssim", 22)}
  {formula("scd", 23)}
  <p>Se agregan la eficiencia de fusión (FE) y la fidelidad de información visual (VIF). Todas se
  maximizan salvo Nabf, que se minimiza.</p>
  {pie(12)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>8. Resultados cuantitativos</h2>
  <p><b>Tabla 2.</b> Benchmark completo: los 7 métodos con las 12 métricas (promedio de los 20 pares
  TNO; en negrita el mejor valor de cada columna).</p>
  {tabla_metodos(ORDEN, resaltar=PROP)}
  <p class="lectura">Lectura: la propuesta obtiene la <b>menor tasa de artefactos por amplio margen</b>
  (Nabf {means.loc[PROP, "Nabf"]:.3f}, {means.loc["PiramideLaplace", "Nabf"]/means.loc[PROP, "Nabf"]:.1f} veces menos que el mejor rival) y la <b>mayor similitud
  estructural</b> (SSIM {means.loc[PROP, "SSIM"]:.3f}); en Qabf ({means.loc[PROP, "Qabf"]:.3f}), SCD
  ({means.loc[PROP, "SCD"]:.3f}) y VIF ({means.loc[PROP, "VIF"]:.3f}) queda segunda, a milésimas del
  líder de cada columna. El Top-Hat clásico —la referencia morfológica directa— gana solo en las
  métricas de actividad bruta (EN, MG, SF) a costa del mayor Nabf del estudio
  ({means.loc["TopHat_Clasico", "Nabf"]:.3f}) y la peor SSIM ({means.loc["TopHat_Clasico", "SSIM"]:.3f}):
  la diferencia con la propuesta aísla el aporte del banco disco + líneas y del ajuste (r, m) por
  PSO.</p>
  {figura(charts["quality"], "Las cuatro métricas de calidad de fusión; la barra azul es la propuesta.", 96)}
  {pie(13)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>9. Análisis estadístico</h2>
  <p>Primero, el test de Friedman (7 métodos × 20 imágenes, por rangos) para cada métrica:</p>
  {formula("friedman", 24)}
  <p><b>Tabla 3.</b> Resultados del test de Friedman.</p>
  {tabla_friedman()}
  {pie(14)}
</div>
<div class="page">
  <h2>9. Análisis estadístico (continuación): Wilcoxon y ranking</h2>
  <p>Wilcoxon pareado de la propuesta contra cada rival (20 imágenes), con corrección de Holm y tamaño
  de efecto rank-biserial:</p>
  {formula("rb", 25)}
  <p><b>Tabla 4.</b> Resumen de los {len(wtab)} contrastes de la propuesta: mejor / peor / sin
  diferencia significativa (≈), α = 0,05.</p>
  {tabla_wilcoxon}
  <p class="lectura">Lectura: la propuesta resulta significativamente mejor en {w_mejor} contrastes,
  peor en {w_peor} y sin diferencia en {w_emp}.</p>
  {figura(charts["ranking"], "Ranking promedio global de los 7 métodos (12 métricas, dirección respetada); la barra azul es la propuesta.", 78)}
  {pie(15)}
</div>
""")

pg = 16
H.append(f"""
<div class="page">
  <h2>10. Resultados cualitativos: las 20 escenas</h2>
  <p>Para cada escena se muestran las fuentes VIS e IR, los seis comparativos y la propuesta (recuadro
  rojo). Se sugiere observar: la visibilidad del objetivo térmico, la conservación de la textura del
  fondo visible y la ausencia de halos en los bordes.</p>
  {mont_html[0]}
  {mont_html[1]}
  {pie(pg)}
</div>
""")
pg += 1
for i in range(2, 20, 2):
    blk = mont_html[i] + (mont_html[i + 1] if i + 1 < 20 else "")
    H.append(f'<div class="page"><h2>10. Resultados cualitativos (escenas {i+1} y {min(i+2,20)} de 20)</h2>'
             f'{blk}{pie(pg)}</div>')
    pg += 1

H.append(f"""
<div class="page">
  <h2>11. Evaluación orientada a tarea: detección en LLVIP</h2>
  <p>Para medir el efecto práctico de la fusión se reentrenó el mismo detector <b>YOLOv8n</b> (40 épocas,
  misma configuración y semilla) sobre cada versión fusionada del dataset etiquetado <b>LLVIP</b>
  (peatones nocturnos; subconjunto de 2.000 imágenes de entrenamiento y 500 de validación). Como los
  pares VIS/IR están registrados, las anotaciones valen para toda versión fusionada: la diferencia de
  mAP aísla el efecto del método de fusión.</p>
  <p><b>Tabla 8.</b> Detección de peatones en LLVIP — mAP por entrada del detector.</p>
  {tabla_det()}
  <p class="lectura">Lectura: toda fusión supera con claridad al visible solo (mAP@0,5 de 0,808 a la banda
  0,926–0,949, +0,12 a +0,14 puntos); el infrarrojo solo es la modalidad más fuerte (0,957) y ninguna
  fusión lo supera, coherente con que el peatón nocturno es esencialmente térmico; y entre las fusiones,
  en una banda estrecha, la propuesta es competitiva (0,936) —prácticamente empatada con el Top-Hat
  clásico (0,938)— sin ser la líder. Conclusión honesta: la superioridad de la propuesta en calidad de
  imagen (Nabf, SSIM) no se traslada automáticamente a la detección; la elección del método depende del
  criterio operativo prioritario.</p>
  {figura(charts["det"], "mAP por entrada del detector (YOLOv8n reentrenado por método sobre LLVIP).", 88)}
  {pie(pg)}
</div>
""")
pg += 1

TAB_ABLA = """<table><thead><tr><th>Variante</th><th>Qabf &uarr;</th><th>Nabf &darr;</th>
<th>SSIM &uarr;</th><th>SCD &uarr;</th><th>VIF &uarr;</th></tr></thead><tbody>
<tr><td><b>Propuesta + F_apt (r=25; m=0,070)</b></td><td>0,500</td><td><b>0,041</b></td><td><b>0,782</b></td><td>1,450</td><td>0,368</td></tr>
<tr><td>Top-Hat clásico + Fo (r=25; m=0,30)</td><td><b>0,534</b></td><td>0,184</td><td>0,745</td><td><b>1,504</b></td><td><b>0,395</b></td></tr>
<tr><td>Propuesta + Fo (r=1; m=0,30)</td><td>0,448</td><td>0,121</td><td>0,761</td><td>1,353</td><td>0,322</td></tr>
<tr><td>Top-Hat clásico manual (r=5; m=1)</td><td>0,305</td><td>0,585</td><td>0,578</td><td>1,360</td><td>0,334</td></tr>
</tbody></table>"""

H.append(f"""
<div class="page">
  <h2>12. Ablación de la función de aptitud (pedido de la revisión)</h2>
  <p>El barrido de 25 configuraciones se repitió con la función objetivo del trabajo de referencia,
  <b>Fo = SSIM<sub>avg</sub> + E<sub>n</sub> + PSNR<sub>n</sub></b> (Ortega y Espinoza, 2025), con su
  rango original m &isin; [0,3; 2,0], sobre la propuesta y sobre el operador clásico. En las
  <b>50 corridas</b> el peso óptimo se ubicó en el límite inferior del rango (<b>m* = 0,30</b>): los dos
  términos de fidelidad de Fo dominan a la entropía y empujan el realce al mínimo permitido. Sobre la
  propuesta, Fo seleccionó además <b>r* = 1</b>, un óptimo trivial que desactiva el banco de SE.</p>
  {figura(EXIST.get("fig_aptitud_vs_m.png"), "Aptitud en función de m (r = 25), sin restricciones de rango: las tres curvas decrecen monótonamente en [0,5-2], y el máximo real de Fo sobre la propuesta coincide con nuestro óptimo (m ≈ 0,07).", 78)}
  <p><b>Tabla 9.</b> Óptimos de cada aptitud evaluados sobre los 20 pares (medias).</p>
  {TAB_ABLA}
  <p class="lectura">Lectura: ninguna configuración del enjambre puede converger dentro de [0,5; 2,0]
  porque la aptitud decrece monótonamente allí; ambas formulaciones acuerdan el peso adecuado del
  operador con suma (m ≈ 0,07). La propuesta con F_apt conserva el mejor perfil de limpieza y estructura;
  el óptimo de Fo sobre el clásico es competitivo en bordes y correlación al costo de 4,5&times; más
  artefactos. La función de aptitud define el perfil del resultado (refuerza H2).</p>
  {pie(pg)}
</div>
""")
pg += 1

TAB_M3FD = """<table><thead><tr><th>Entrada del detector</th><th>AP People &uarr;</th>
<th>AP Lamp &uarr;</th><th>Promedio del par &uarr;</th><th>mAP@0,5 &uarr;</th></tr></thead><tbody>
<tr><td>VIS (solo)</td><td>0,178</td><td><b>0,135</b></td><td>0,157</td><td><b>0,245</b></td></tr>
<tr><td>IR (solo)</td><td><b>0,220</b></td><td>0,018</td><td>0,119</td><td>0,191</td></tr>
<tr><td>Pirámide de Laplace (LP)</td><td>0,147</td><td>0,096</td><td>0,122</td><td>0,215</td></tr>
<tr><td>Ratio Pyramid (RP)</td><td>0,198</td><td>0,133</td><td><b>0,165</b></td><td>0,231</td></tr>
<tr><td>Wavelet discreta (DWT)</td><td>0,165</td><td>0,110</td><td>0,137</td><td>0,228</td></tr>
<tr><td>DTCWT</td><td>0,159</td><td>0,114</td><td>0,137</td><td>0,229</td></tr>
<tr><td>Curvelet (CVT)</td><td>0,167</td><td>0,100</td><td>0,133</td><td>0,228</td></tr>
<tr><td>Top-Hat clásico (r=5; m=1)</td><td>0,125</td><td>0,054</td><td>0,090</td><td>0,198</td></tr>
<tr><td>PSO FPUNA (clásico + Fo; r=25; m=0,30)</td><td>0,174</td><td>0,118</td><td>0,146</td><td>0,229</td></tr>
<tr><td>Propuesta + Fo (r=1; m=0,30)</td><td>0,200</td><td>0,110</td><td>0,155</td><td>0,238</td></tr>
<tr><td><b>Propuesta + F_apt (r=25; m=0,070)</b></td><td>0,207</td><td>0,117</td><td>0,162</td><td>0,239</td></tr>
</tbody></table>"""

H.append(f"""
<div class="page">
  <h2>13. Detección con clases complementarias (M3FD)</h2>
  <p>Experimento diseñado para aislar el escenario donde la fusión es insustituible: el dataset
  <b>M3FD</b> (Liu et al., 2022; 2.000 pares de entrenamiento y 500 de validación) anota seis clases,
  dos de ellas de <b>visibilidad opuesta</b>: las personas dominan en el infrarrojo (firma térmica) y
  las luces (Lamp) son esencialmente visibles solo en el canal visible. Un <b>único detector YOLOv8n</b>
  se entrenó con las imágenes de ambas modalidades mezcladas (4.000 imágenes, 40 épocas, etiquetas
  compartidas) y se evaluó <b>por inferencia</b> sobre la validación de cada modalidad y de cada método
  de fusión — incluidos los dos óptimos del PSO (F_apt y Fo).</p>
  <p><b>Tabla 10.</b> AP@0,5 por clase y mAP global (medias sobre 500 imágenes de validación).</p>
  {TAB_M3FD}
  <p class="lectura">Lectura: la complementariedad es extrema — el IR domina en personas (0,220) pero es
  prácticamente ciego a las luces (0,018); el VIS presenta el patrón espejo. Las mejores fusiones superan
  en el promedio del par a <b>ambas</b> modalidades individuales (RP 0,165 y propuesta 0,162 vs VIS 0,157
  e IR 0,119): detectan ambas clases en una sola imagen, algo que ninguna modalidad logra por separado.
  La propuesta es la <b>mejor fusión del estudio</b> en mAP global (0,239) y en personas (0,207, cerca del
  IR puro), y su óptimo F_apt supera al de Fo en las dos clases clave. El VIS conserva el mejor mAP global
  de seis clases (0,245) por la abundancia de vehículos diurnos; los valores absolutos son moderados
  (subconjunto de 500, modelo nano).</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>14. Conclusiones</h2>
  <h3>Resumen del planteamiento</h3>
  <ol>
    <li><b>Propuesta:</b> Top-Hat de una sola escala (radio r) con banco de cinco SE; respuestas lineales
        promediadas (ecs. 6–9) <b>sumadas</b> a la respuesta del disco (ecs. 11–12); detalle dominante
        entre fuentes y reconstrucción aditivo-sustractiva con peso m (ecs. 13–14).</li>
    <li><b>Optimización:</b> barrido de 25 configuraciones PSO (partículas 2–10 × iteraciones 10–50,
        replicando el diseño de Ortega y Espinoza 2025) con aptitud orientada a fusión →
        <b>r = 25, m = 0,070</b> (F = 1,9843), alcanzado consistentemente con n = 10 y T ≥ 30.</li>
    <li><b>Benchmark:</b> 7 métodos (LP, RP, DWT, DTCWT, CVT, Top-Hat clásico y la propuesta) × 20 pares
        TNO × 12 métricas sin referencia.</li>
    <li><b>Estadística:</b> Friedman por métrica y Wilcoxon-Holm pareado de la propuesta contra cada
        rival, con ranking promedio global.</li>
  </ol>
  <h3>Resultados clave</h3>
  <ul>
    <li>La propuesta es el método más limpio y estructuralmente fiel del benchmark
        (Nabf {means.loc[PROP, "Nabf"]:.3f} y SSIM {means.loc[PROP, "SSIM"]:.3f}, mejores de los 7
        métodos) y segunda en Qabf ({means.loc[PROP, "Qabf"]:.3f}), SCD ({means.loc[PROP, "SCD"]:.3f})
        y VIF ({means.loc[PROP, "VIF"]:.3f}).</li>
    <li>En los contrastes de Wilcoxon-Holm la propuesta es significativamente mejor en {w_mejor} de
        {len(wtab)} comparaciones (peor en {w_peor}, sin diferencia en {w_emp}).</li>
    <li>Frente al Top-Hat clásico, el banco disco + líneas con suma de ramas y el ajuste (r, m) por PSO
        aportan una mejora consistente en todas las métricas de calidad de fusión.</li>
  </ul>
  <h3>Próximos pasos</h3>
  <ul>
    <li>Extender la evaluación de detección a otros detectores y a los conjuntos completos de
        LLVIP y M3FD.</li>
    <li>Complementar con una validación perceptual por observadores.</li>
  </ul>
  {pie(pg)}
</div>
""")

html = f"""<!DOCTYPE html><html lang="es"><head><meta charset="utf-8">
<title>Presentación de avances — Fusión IR/VIS</title><style>{css}</style></head>
<body>{''.join(H)}</body></html>"""
with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("HTML:", HTML_OUT, f"{os.path.getsize(HTML_OUT)/1e6:.1f} MB")

# ------------------------------------------------------------------ HTML -> PDF (Edge headless)
import subprocess
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE):
    EDGE = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if os.path.exists(EDGE):
    subprocess.run([EDGE, "--headless", "--disable-gpu",
                    f"--print-to-pdf={PDF_OUT}", "--no-pdf-header-footer",
                    HTML_OUT], capture_output=True, timeout=300)
    if os.path.exists(PDF_OUT):
        print("PDF:", PDF_OUT, f"{os.path.getsize(PDF_OUT)/1e6:.1f} MB")
    else:
        print("AVISO: Edge no genero el PDF; reintentar o imprimir el HTML con Ctrl+P.")
else:
    print("AVISO: Edge no encontrado; imprimir el HTML a PDF manualmente (Ctrl+P, A4).")
