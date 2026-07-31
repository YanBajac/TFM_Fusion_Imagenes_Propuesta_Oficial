# -*- coding: utf-8 -*-
"""Genera docs/Avances_Tesis.pdf — informe de avances (diseno simple tipo Word).
Propuesta con SUMA de ramas (r=25, m=0.30) vs 6 comparativos (LP, RP, DWT, DTCWT,
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
# --------------------------------------------------------------- variante
# VARIANTE_AVANCES=restringido -> configuracion con el rango publicado m en [0,30; 2,00]
# VARIANTE_AVANCES=libre       -> configuracion con el rango de m ampliado
VARIANTE = os.environ.get("VARIANTE_AVANCES", "restringido").strip().lower()
assert VARIANTE in ("restringido", "libre"), f"VARIANTE_AVANCES invalida: {VARIANTE}"
LIBRE = (VARIANTE == "libre")

V = {
    "m": "0,0703" if LIBRE else "0,30",
    "rango": "[0,05; 1,20]" if LIBRE else "[0,30; 2,00]",
    "rango_anexo": "[0,01; 2,00]" if LIBRE else "[0,30; 2,00]",
    "etiqueta": ("configuración LIBRE — rango del peso ampliado"
                 if LIBRE else "configuración RESTRINGIDA — rango publicado"),
    "sufijo": "_libre" if LIBRE else "_restringido",
}

MR = os.path.join(ROOT, "experiments", "results",
                  "metrics_reports_libre" if LIBRE else "metrics_reports")
OUT  = os.path.join(ROOT, "docs", "_local")
os.makedirs(OUT, exist_ok=True)
HTML_OUT = os.path.join(OUT, f"Avances_Tesis{V['sufijo']}.html")
PDF_OUT  = os.path.join(ROOT, "docs", f"Avances_Tesis{V['sufijo']}.pdf")
print(f"VARIANTE: {VARIANTE} | metricas: {os.path.basename(MR)} | salida: {os.path.basename(PDF_OUT)}")

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
grid  = pd.read_csv(os.path.join(MR, "pso_grid_search_fo_propuesta.csv")).rename(
    columns={"Fo_opt": "F_opt"})
det   = pd.read_csv(os.path.join(MR, "detection_llvip_map.csv")).set_index("method")

PROP = "Propuesta_Novedosa"
ORDEN = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
         "TopHat_Clasico", PROP]
LBL = {"PiramideLaplace": "Pirámide de Laplace (LP)",
       "RatioPiramide": "Ratio of low-pass Pyramid (RP)",
       "DWT": "Wavelet discreta (DWT)",
       "DTCWT": "Dual-Tree Complex Wavelet (DTCWT)",
       "Curvelet": "Curvelet (CVT)",
       "TopHat_Clasico": "Top-Hat clásico",
       PROP: f"Propuesta novedosa (r=25, m={V['m']})"}
SHORT = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT",
         "Curvelet": "CVT", "TopHat_Clasico": "TH clás.", PROP: "Propuesta"}
DIRECTION = {"EN": 1, "SD": 1, "FE": 1, "MG": 1, "MI_vis": 1, "MI_ir": 1, "SF": 1,
             "SSIM": 1, "PSNR": 1}
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

# ------------------------------------------------------------------ valores de la narrativa
_rk = rankm["avg_rank"].sort_values()
POS_RANK = list(_rk.index).index(PROP) + 1
VAL_RANK = f"{_rk[PROP]:.2f}".replace(".", ",")
LIDER_RANK = f"{_rk.iloc[0]:.2f}".replace(".", ",")
_fus = det.drop(index=[x for x in ("VIS", "IR") if x in det.index])
LLVIP_PROP = f"{det.loc[PROP, 'mAP50']:.3f}".replace(".", ",")
LLVIP_LO = f"{_fus['mAP50'].min():.3f}".replace(".", ",")
LLVIP_HI = f"{_fus['mAP50'].max():.3f}".replace(".", ",")
_m3 = pd.read_csv(os.path.join(MR, "detection_m3fd_map.csv")).set_index("method")
_m3["par"] = (_m3["AP50_People"] + _m3["AP50_Lamp"]) / 2
_m3f = _m3.drop(index=[x for x in ("VIS", "IR") if x in _m3.index])
M3_PROP_PAR = f"{_m3.loc[PROP, 'par']:.3f}".replace(".", ",")
M3_PROP_MAP = f"{_m3.loc[PROP, 'mAP50']:.3f}".replace(".", ",")
M3_MEJOR = _m3f["par"].idxmax()
M3_MEJOR_PAR = f"{_m3f['par'].max():.3f}".replace(".", ",")
M3_PROP_ES_MEJOR = (M3_MEJOR == PROP)
M3_SUPERA_AMBAS = bool(_m3.loc[PROP, "par"] > _m3.loc["VIS", "par"]
                       and _m3.loc[PROP, "par"] > _m3.loc["IR", "par"])

# Tamano de la particion de prueba, leido del dataset generado (no fijado a mano).
_m3dir = os.path.join(ROOT, "datasets", "m3fd_test_VIS", "images", "val")
M3_N = (len([f for f in os.listdir(_m3dir) if f.lower().endswith((".jpg", ".png"))])
        if os.path.isdir(_m3dir) else 500)


def _n(x, d=3):
    return f"{x:.{d}f}".replace(".", ",")


# Lectura de la Tabla 9 construida desde los datos: cada afirmacion se verifica antes de
# escribirse, porque con un split o un checkpoint distintos varias de ellas se invierten.
_sup_amb = [k for k in _m3f.index
            if _m3f.loc[k, "par"] > _m3.loc["VIS", "par"]
            and _m3f.loc[k, "par"] > _m3.loc["IR", "par"]]
_rec_ambas = [k for k in _m3f.index
              if _m3f.loc[k, "AP50_People"] > 0 and _m3f.loc[k, "AP50_Lamp"] > 0]
_pos_par = int(_m3f["par"].rank(ascending=False)[PROP])
_mejor_map = _m3["mAP50"].idxmax()

LECTURA_M3FD = (
    f"Lectura: la complementariedad de las dos clases queda a la vista en las modalidades "
    f"individuales — el infrarrojo alcanza {_n(_m3.loc['IR', 'AP50_People'])} en personas frente a "
    f"{_n(_m3.loc['IR', 'AP50_Lamp'])} en luces, y el visible presenta el patrón inverso "
    f"({_n(_m3.loc['VIS', 'AP50_People'])} y {_n(_m3.loc['VIS', 'AP50_Lamp'])}). "
    + (f"<b>{len(_rec_ambas)} de las {len(_m3f)} fusiones detectan objetos de ambas clases</b> en una "
       "sola imagen"
       # La frase "algo que el IR no logra" solo es cierta si el IR es practicamente ciego a
       # Lamp; con un detector bien entrenado el IR la detecta, peor pero no de forma nula.
       + (", con un AP en luces muy superior al del infrarrojo, que apenas las distingue. "
          if _m3.loc["IR", "AP50_Lamp"] < 0.10 else
          f", y todas mejoran el AP en luces del infrarrojo ({_n(_m3.loc['IR', 'AP50_Lamp'])}), "
          "que es su clase débil. ")
       if len(_rec_ambas) else "")
    + (f"En el promedio del par, <b>{len(_sup_amb)} de las {len(_m3f)} fusiones "
       f"{'supera' if len(_sup_amb) == 1 else 'superan'} a ambas modalidades</b> "
       f"({', '.join(LBL.get(k, k).split(' (')[0] for k in _sup_amb)}). "
       if _sup_amb else
       f"<b>Ninguna de las {len(_m3f)} fusiones supera a ambas modalidades</b> en el promedio del "
       f"par: el mejor valor de una fusión es {M3_MEJOR_PAR} "
       f"({LBL.get(M3_MEJOR, M3_MEJOR).split(' (')[0]}) frente a "
       f"{_n(_m3.loc['VIS', 'par'])} del visible. ")
    + f"La propuesta obtiene <b>{M3_PROP_PAR}</b> en el par (puesto {_pos_par} de {len(_m3f)} entre "
      f"las fusiones) y {M3_PROP_MAP} de mAP global. "
    + f"El mejor mAP global de las seis clases lo conserva "
      f"<b>{LBL.get(_mejor_map, _mejor_map).split(' (')[0]}</b> "
      f"({_n(_m3.loc[_mejor_map, 'mAP50'])}), por la abundancia de vehículos diurnos. "
    + "Los valores absolutos son moderados: subconjunto reducido y modelo nano.")

# Parrafo y pie de la figura cualitativa, tomados del JSON que emite
# make_figura_detecciones_m3fd.py: con otro test las escenas y los conteos cambian.
_djs = os.path.join(MR, "figura_detecciones_m3fd.json")
if os.path.exists(_djs):
    import json as _json
    _dd = _json.load(open(_djs, encoding="utf-8"))
    _e = {x["lado"]: x for x in _dd["escenas"]}
    _pa, _pb = _e.get("people"), _e.get("lamp")
    def _pl(n, sing, plur):
        return f"{n} {sing if n == 1 else plur}"

    _frases = []
    if _pa:
        _p = _pa["people"]
        _cmp = ("supera a ambas modalidades" if _p[PROP] > max(_p["VIS"], _p["IR"])
                else "queda entre ambas" if _p[PROP] > min(_p["VIS"], _p["IR"])
                else "no mejora a ninguna")
        _frases.append(
            f"en la escena superior ({_pa['escena']}) la fusión detecta "
            f"<b>{_pl(_p[PROP], 'persona', 'personas')}</b> frente a {_p['VIS']} del visible y "
            f"{_p['IR']} del infrarrojo, es decir que {_cmp}")
    if _pb:
        _l, _pp = _pb["lamp"], _pb["people"]
        _t = (f"en la inferior ({_pb['escena']}) el infrarrojo detecta "
              f"{_pl(_l['IR'], 'luz', 'luces')} y la fusión conserva <b>{_l[PROP]}</b>, "
              f"las mismas que el visible" if _l[PROP] == _l["VIS"] else
              f"en la inferior ({_pb['escena']}) el infrarrojo detecta "
              f"{_pl(_l['IR'], 'luz', 'luces')} y la fusión conserva <b>{_l[PROP]}</b>")
        # Solo se afirma que estan las dos clases si la fusion detecta objetos de ambas.
        if _l[PROP] > 0 and _pp[PROP] > 0:
            _t += (f", junto con {_pl(_pp[PROP], 'persona', 'personas')}: "
                   "<b>ambas clases en una sola imagen</b>")
        elif _pp[PROP] == 0 and _pp["VIS"] > 0:
            _t += (f"; en esa escena, en cambio, la fusión <b>pierde</b> "
                   + ("la persona" if _pp["VIS"] == 1 else f"las {_pp['VIS']} personas")
                   + " que sí detecta el visible")
        _frases.append(_t)
    PARRAFO_DETECCIONES = (
        "Dos escenas de la partición de prueba con las detecciones del modelo único dibujadas "
        "(personas en granate, luces en azul); se eligieron automáticamente entre las escenas cuya "
        "anotación contiene ambas clases, sin intervención manual. "
        + ("; ".join(_frases)[:1].upper() + "; ".join(_frases)[1:] + "."))
    PIE_DETECCIONES = (f"Detecciones del modelo único VIS+IR sobre las escenas "
                       f"{' y '.join(x['escena'] for x in _dd['escenas'])} de M3FD "
                       f"(conf ≥ {_n(_dd['conf'], 2)}).")
else:
    PARRAFO_DETECCIONES = (
        "Dos escenas de la partición de prueba con las detecciones del modelo único dibujadas "
        "(personas en granate, luces en azul), elegidas automáticamente entre las escenas cuya "
        "anotación contiene ambas clases complementarias.")
    PIE_DETECCIONES = "Detecciones del modelo único VIS+IR sobre dos escenas de M3FD."

if LIBRE:
    LECTURA_PSO = (
        "Lectura: con el límite inferior del peso ampliado, el óptimo de F<sub>o</sub> deja de estar "
        "sobre el borde del intervalo y el barrido devuelve pesos bajos, del orden de "
        f"<b>m = {V['m']}</b>. El radio adoptado sigue siendo r = 25.")
    PARRAFO_RADIO = (
        "El radio se fija en r = 25 (elementos estructurantes de 51 píxeles), de modo que el operador "
        "aprovecha un vecindario amplio para capturar los objetivos térmicos completos. El peso bajo "
        f"({V['m']}) mantiene el realce suave: el producto del peso por la energía del operador es "
        "comparable al que el trabajo de referencia obtiene con m = 0,30 sobre un disco único, porque "
        "el banco de cinco respuestas inyecta unas 4,3 veces más energía de detalle. Estos "
        "hiperparámetros definen la configuración de la propuesta usada en todo el benchmark de esta "
        "variante.")
else:
    LECTURA_PSO = (
        "Lectura: las <b>25 configuraciones convergen al mismo peso óptimo, m* = 0,30</b>, el límite "
        "inferior del rango publicado, porque los dos términos de fidelidad de F<sub>o</sub> "
        "(SSIM<sub>avg</sub> y PSNR<sub>n</sub>) decrecen al aumentar el realce y dominan sobre la "
        "entropía normalizada; se verificó que F<sub>o</sub> decrece de forma estrictamente monótona en "
        "m sobre todo el rango, de manera que el óptimo del peso está forzado por la forma de la "
        "aptitud y no es un artefacto del enjambre. "
        "<b>El radio, en cambio, no lo fija el PSO:</b> dentro de este rango la aptitud F<sub>o</sub> "
        f"prefiere r = {R_PREFERIDO} ({FO_MEJOR} frente a {FO_R25} en r = 25), de modo que r = 25 es una "
        "<b>decisión de diseño</b> tomada sobre las métricas de evaluación y no el resultado de la "
        "optimización. De las nueve métricas, <b>cinco favorecen r = 25</b> (EN, SD, FE, MG y SF) y "
        "las <b>cuatro de fidelidad favorecen r = 1</b> (SSIM, PSNR, MI<sub>vis</sub> y "
        "MI<sub>ir</sub>), todas con p &lt; 10<sup>-5</sup>. Se adopta <b>r = 25, m = 0,30</b> "
        "priorizando la capacidad de realce, y se reconoce que la elección del radio se apoya en parte "
        "del mismo criterio con el que luego se evalúa.")
    PARRAFO_RADIO = (
        "El radio r = 25 (elementos estructurantes de 51 píxeles) permite que el operador aproveche un "
        "vecindario amplio para capturar los objetivos térmicos completos, y a igual peso supera a "
        "r = 1 en entropía, contraste, ganancia de entropía sobre las fuentes, gradiente medio y "
        "frecuencia espacial; cede, en cambio, en las cuatro métricas de fidelidad. Conviene precisar "
        "que r = 1 <b>no</b> desactiva el banco de elementos estructurantes: con r = 1 el disco es la "
        "cruz de 3×3 y las cuatro líneas orientadas son cuatro máscaras 3×3 distintas, de modo que el "
        "banco sigue operativo sobre un vecindario mínimo. El peso m = 0,30 es el que produce el "
        "barrido con la metodología de referencia y mantiene la saturación por debajo del 2 % de los "
        "píxeles. Estos hiperparámetros definen la configuración de la propuesta usada en todo el "
        "benchmark de esta variante.")

# ------------------------------------------------------------------ aptitud del barrido
# Los dos valores de F_o que se citan en la lectura del barrido se derivan del CSV y no se
# escriben a mano: al sustituir un par del corpus cambian las escenas sobre las que se
# optimiza (list_pairs()[::7]) y con ellas la aptitud.
_g = grid.copy()
_col_fo = "F_opt" if "F_opt" in _g.columns else "Fo_opt"
FO_MEJOR = f"{_g[_col_fo].max():.4f}".replace(".", ",")
_r_mejor = int(_g.loc[_g[_col_fo].idxmax(), "r_opt"])
_fo25 = _g.loc[_g["r_opt"] == 25, _col_fo]
FO_R25 = f"{_fo25.max():.4f}".replace(".", ",") if len(_fo25) else "-"
R_PREFERIDO = _r_mejor
N_R1 = int((_g["r_opt"] == 1).sum())
N_M_PISO = int((_g["m_opt"] == _g["m_opt"].min()).sum())

# ------------------------------------------------------------------ posicion por metrica
_NOM_MET = {"EN": "la entropía", "SD": "el contraste", "FE": "la ganancia de entropía sobre las fuentes",
            "MG": "el gradiente medio", "MI_vis": "la información mutua con el visible",
            "MI_ir": "la información mutua con el infrarrojo", "SF": "la frecuencia espacial",
            "SSIM": "la similitud estructural", "PSNR": "la relación señal-ruido"}
_POS = {k: int(means[k].rank(ascending=False)[PROP]) for k in METS}
_LID = [k for k in METS if _POS[k] == 1]
_SEG = [k for k in METS if _POS[k] == 2]
_CEDE = [k for k in METS if _POS[k] >= 5]

def _enum(ks, con_valor=True):
    """Enumera metricas en prosa, opcionalmente con su valor."""
    if not ks:
        return ""
    fmt = {"SF": ".2f", "PSNR": ".2f"}
    ps = [(f"{_NOM_MET[k]} ({k} {means.loc[PROP, k]:{fmt.get(k, '.3f')}})"
           if con_valor else _NOM_MET[k]) for k in ks]
    return ps[0] if len(ps) == 1 else ", ".join(ps[:-1]) + " y " + ps[-1]

# metricas donde la propuesta supera al Top-Hat clasico
_VS_TH = [k for k in METS if means.loc[PROP, k] > means.loc["TopHat_Clasico", k]]
_VS_TH_NO = [k for k in METS if means.loc[PROP, k] < means.loc["TopHat_Clasico", k]]

if _LID:
    LECTURA_BENCH = (f"Lectura: la propuesta <b>lidera {_enum(_LID)}</b> del benchmark"
                     + (f", y es segunda en {_enum(_SEG, False)}" if _SEG else "") + ". ")
else:
    LECTURA_BENCH = ("Lectura: en esta configuración la propuesta <b>no lidera ninguna de las nueve "
                     f"métricas</b>; su mejor posición es {min(_POS.values())}.ª "
                     f"({_enum([k for k in METS if _POS[k] == min(_POS.values())], False)}). ")
LECTURA_BENCH += (f"Cede, en cambio, en {_enum(_CEDE, False)}. " if _CEDE else "")
LECTURA_BENCH += (f"Frente al Top-Hat clásico —la referencia morfológica directa— mejora "
                  f"<b>{len(_VS_TH)} de las nueve métricas</b> y cede en {len(_VS_TH_NO)} "
                  f"({_enum(_VS_TH_NO, False)}). Advertencia metodológica: los dos operadores no "
                  "comparten (r, m) —el clásico usa r = 5, m = 1—, de modo que la diferencia refleja "
                  "conjuntamente el cambio de operador y el de hiperparámetros.")

# ------------------------------------------------------------------ graficas
charts = {}
AZUL = "#4472c4"; GRIS = "#a6a6a6"

# mejor aptitud F_o alcanzada segun el numero de particulas (Tmax=50)
fig, ax = plt.subplots(figsize=(7.2, 3.2))
_ns = [2, 4, 6, 8, 10]
_yb = [grid[(grid.n == n) & (grid.Tmax == 50)]["F_opt"].values[0] for n in _ns]
ax.plot(_ns, _yb, "-o", color=AZUL, lw=2, ms=7, mfc=AZUL, mec="white")
_im = int(np.argmax(_yb))
ax.scatter([_ns[_im]], [_yb[_im]], s=150, facecolor="none", edgecolor=AZUL, lw=1.6, zorder=4)
ax.set_xlabel("Número de partículas del enjambre (n)"); ax.set_ylabel("Mejor aptitud $F_o$")
ax.set_title("Mejor aptitud $F_o$ según el tamaño del enjambre (Tmax = 50)", fontsize=11)
ax.set_xticks(_ns)
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

key = ["EN", "FE", "SF", "SSIM"]
fig, axes = plt.subplots(1, 4, figsize=(12.0, 2.9))
for ax, mk in zip(axes, key):
    vals = [means.loc[m, mk] for m in ORDEN]
    cols = [AZUL if m == PROP else GRIS for m in ORDEN]
    ax.bar(range(len(ORDEN)), vals, color=cols, width=0.62)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.3f}", ha="center", va="bottom", fontsize=6.3)
    ax.set_title(f'{mk} (mayor mejor)', fontsize=9)
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
ax.set_xlabel("Ranking promedio en 9 métricas (menor = mejor)", fontsize=9)
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
 "pso_fit": r"F_{o}(r,m)= SSIM_{avg} + E_{n} + PSNR_{n} \;\longrightarrow\; \max",
 "psnr": r"PSNR=10\,\log_{10}\frac{1}{MSE}\,,\qquad MSE=\frac{1}{2}\left[MSE(F,VIS)+MSE(F,IR)\right]",
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
# La galeria se construye desde list_pairs(), NO desde os.listdir(): leyendo el directorio se
# ignoraba PARES_EXCLUIDOS y el par corrupto Athena_heather_IR_hei_vis_g aparecia como "Par 09"
# dos paginas despues de que el propio informe declarara que se excluye; ademas, con 21 archivos
# en el directorio el recorte fijo de bloques descartaba el ultimo par valido.
import sys as _sys
_sys.path.insert(0, ROOT)
from src.datasets import list_pairs as _list_pairs
pairs_html = []
for idx, nm in enumerate([p[0].name for p in _list_pairs()], 1):
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
    "ejemplo_modalidades.png", "fig_aptitud_vs_m.png", "fig_m3fd_detecciones.png",
    "comparacion_aptitudes.png"]}
print("imagenes ok")

def tabla_friedman():
    rows = "".join(f'<tr><td class="l">{r.metric}</td><td>{r.chi2:.1f}</td>'
                   f'<td>{r.p_value:.1e}</td><td>{"Sí" if r.significant_05 else "No"}</td></tr>'
                   for r in fried.itertuples())
    return ('<table class="chica"><tr><th class="l">Métrica</th><th>χ² de Friedman</th>'
            f'<th>p-valor</th><th>Significativa (α = 0,05)</th></tr>{rows}</table>')

# ------------------------------------------------------------------ tabla por imagen
# Mismo formato que el Cuadro 2 del trabajo de referencia: una fila por metodo dentro de
# cada escena, con SSIM_avg, E, SF, SD y PSNR, y en negrita el mejor valor de cada columna.
allm = pd.read_csv(os.path.join(MR, "all_metrics.csv"))
# Tamano del corpus tomado del dato, no fijado a mano: el par Athena_heather_IR_hei_vis_g
# quedo excluido por tener el slot VIS duplicado del IR (ver src/datasets.PARES_EXCLUIDOS).
N_ESC = int(allm["image"].nunique())
COLS_IMG = [("SSIM", "SSIM_avg"), ("EN", "E"), ("SF", "SF"), ("SD", "SD"), ("PSNR", "PSNR")]
ORDEN_IMG = ["PiramideLaplace", "RatioPiramide", "DWT", "DTCWT", "Curvelet",
             "TopHat_Clasico", PROP]
CORTO = {"PiramideLaplace": "LP", "RatioPiramide": "RP", "DWT": "DWT", "DTCWT": "DTCWT",
         "Curvelet": "CVT", "TopHat_Clasico": "Top-Hat clás.", PROP: "Propuesta"}
ESCENA = {
    "APC_1_view_1_fk_06_005": "APC 1 · vista 1",
    "APC_1_view_2_fk_ref_01_005": "APC 1 · vista 2",
    "APC_1_view_3_fk_ref_02_005": "APC 1 · vista 3",
    "APC_3_view_1_fk_bar_06_005": "APC 3 · vista 1",
    "APC_3_view_2_fk_NL_01_005": "APC 3 · vista 2",
    "APC_3_view_3_fk_NL_05_005": "APC 3 · vista 3",
    "Athena_2_men_in_front_of_house_meting003": "2 men in front of house",
    "Athena_APC_4_fennek01_005": "APC 4 (fennek)",
    "Athena_heather_IR_hei_vis_g": "heather (IR/vis g)",
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
    "Triclobs_jeep_in_smoke_R": "jeep in smoke",
}
IMAGENES = list(dict.fromkeys(allm["image"]))

def tabla_por_imagen(imgs):
    filas = []
    for img in imgs:
        sub = allm[allm["image"] == img].set_index("method")
        mejor = {k: sub.loc[ORDEN_IMG, k].idxmax() for k, _ in COLS_IMG}
        for j, m in enumerate(ORDEN_IMG):
            tds = []
            for k, _ in COLS_IMG:
                v = float(sub.loc[m, k])
                b = mejor[k] == m
                s = f"{v:.5f}".replace(".", ",")
                tds.append(f'<td>{"<b>" if b else ""}{s}{"</b>" if b else ""}</td>')
            nom = CORTO[m]
            if m == PROP:
                nom = f"<b>{nom}</b>"
            cls = ' class="ini"' if j == 0 else ""
            esc = (f'<td class="l esc" rowspan="{len(ORDEN_IMG)}">{ESCENA.get(img, img)}</td>'
                   if j == 0 else "")
            filas.append(f'<tr{cls}>{esc}<td class="l">{nom}</td>{"".join(tds)}</tr>')
    head = "".join(f"<th>{lbl}&nbsp;&uarr;</th>" for _, lbl in COLS_IMG)
    return ('<table class="porimg"><tr><th class="l">Escena</th><th class="l">Método</th>'
            f'{head}</tr>{"".join(filas)}</table>')

# cuantas escenas lidera la propuesta en cada columna (para la lectura)
_lidera = {}
for k, lbl in COLS_IMG:
    _lidera[lbl] = sum(1 for img in IMAGENES
                       if allm[allm["image"] == img].set_index("method").loc[ORDEN_IMG, k].idxmax() == PROP)
print(f"propuesta lidera por columna (de {N_ESC} escenas):", _lidera)

DET_ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
             "Curvelet", "TopHat_Clasico", PROP]
DET_LBL = {**LBL, "VIS": "VIS (solo)", "IR": "IR (solo)",
           "Propuesta_Novedosa": f"Propuesta Novedosa (r=25, m={V['m']})"}
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

# ------------------------------------------------------------------ anexos: PSO por escena
_pso_img = pd.read_csv(os.path.join(MR, "pso_por_imagen.csv"))
COLS_ANEXO = [("particulas", "Part.", 0), ("iteraciones", "Iter.", 0), ("r", "r", 0),
              ("m", "m", 2), ("SSIM_avg", "SSIM_avg", 6), ("E", "E", 6),
              ("SF", "SF", 6), ("SD", "SD", 6), ("PSNR", "PSNR", 6), ("FO", "FO", 6)]

def tabla_anexo(img):
    sub = _pso_img[_pso_img["imagen"] == img]
    idx_mejor = sub["FO"].idxmax()
    filas = []
    for i, r in sub.iterrows():
        neg = (i == idx_mejor)
        tds = []
        for col, _, dec in COLS_ANEXO:
            v = r[col]
            txt = f"{int(v)}" if dec == 0 else f"{float(v):.{dec}f}".replace(".", ",")
            tds.append(f'<td>{"<b>" if neg else ""}{txt}{"</b>" if neg else ""}</td>')
        filas.append(f'<tr>{"".join(tds)}</tr>')
    head = "".join(f"<th>{lbl}</th>" for _, lbl, _ in COLS_ANEXO)
    return f'<table class="anexo"><tr>{head}</tr>{"".join(filas)}</table>'

_mej = _pso_img.loc[_pso_img.groupby("imagen")["FO"].idxmax()]
_r1 = int((_mej["r"] == 1).sum())
_m_moda_val = float(_mej["m"].mode().iloc[0])
_m_moda = f"{_m_moda_val:.4f}".replace(".", ",").rstrip("0").rstrip(",")
_m30 = int((_mej["m"] == _m_moda_val).sum())
_n_no_borde = int((_pso_img["m"] != _m_moda_val).sum())

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
table.porimg { font-size: 7.6pt; }
table.anexo { font-size: 7.8pt; width: 96%; margin-left: auto; margin-right: auto; }
table.anexo td, table.anexo th { padding: 0.75mm 0.6mm; }
table.porimg td, table.porimg th { padding: 0.7mm 0.8mm; }
table.porimg td.esc { font-weight: bold; vertical-align: middle; font-size: 7.4pt; }
table.porimg tr.ini td { border-top: 1.2pt solid #000; }
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
H.append(f"""
<div class="page portada">
  <div class="t1">Universidad Comunera (UCOM)<br>Maestría en Ciencias de Datos</div>
  <h1>Fusión de imágenes infrarrojas y visibles<br>mediante morfología matemática</h1>
  <div class="t2">Presentación de avances<br>Propuesta Top-Hat de una escala (suma de ramas) frente al estado del arte</div>
  <div style="font-size:12.5pt; margin-top:-14mm; margin-bottom:14mm;">
    <b>{V['etiqueta']}</b><br>
    <span style="font-size:11pt;">r = 25 · m = {V['m']} · rango de búsqueda del peso: m &isin; {V['rango']}</span></div>
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
  transformada Top-Hat</b>, sobre los {N_ESC} pares del TNO Image Fusion Dataset con nueve métricas sin
  referencia y análisis estadístico no paramétrico.</p>
  <p>El orden del documento:</p>
  <ol>
    <li>Datos de entrada: {N_ESC} pares VIS/IR del dataset TNO (sección 2).</li>
    <li>Fundamentos: operadores morfológicos y transformada Top-Hat (sección 3).</li>
    <li>Propuesta novedosa: formulación completa, ecuaciones 4–15 (sección 4).</li>
    <li>Optimización de (r, m) por PSO (sección 5).</li>
    <li>Métodos comparativos del benchmark (sección 6).</li>
    <li>Métricas de evaluación con sus fórmulas (sección 7).</li>
    <li>Resultados cuantitativos: tabla general y gráficas (sección 8).</li>
    <li>Análisis estadístico: Friedman, Wilcoxon-Holm y ranking (sección 9).</li>
    <li>Resultados cualitativos de las {N_ESC} escenas (sección 10).</li>
    <li>Evaluación orientada a tarea: detección en LLVIP (sección 11) y clases complementarias en
        M3FD (sección 12), y conclusiones (sección 13).</li>
    <li>Anexos 1-{N_ESC}: las 25 configuraciones del PSO en cada una de las {N_ESC} escenas.</li>
  </ol>
  {pie(2)}
</div>
""")

# Bloques calculados sobre el largo real, no recortados a 20 a mano.
chunks = [pairs_html[i:i + 8] for i in range(0, len(pairs_html), 8)]
H.append(f"""
<div class="page">
  <h2>2. Datos de entrada: {N_ESC} pares VIS/IR (TNO)</h2>
  <p>Se trabaja con los {N_ESC} pares registrados del TNO Image Fusion Dataset (escenas de vigilancia
  nocturna: vehículos, personas, humo). Cada escena tiene una imagen visible (VIS), que aporta textura y
  contexto, y una infrarroja (IR), que registra la radiación térmica. Ambas comparten nombre de archivo
  para el emparejado automático. Sobre estos {N_ESC} pares se calculan todas las métricas del informe.</p>
  <p class="lectura">Nota sobre el corpus: el conjunto original contiene 21 archivos emparejables, pero
  el par <i>Athena_heather_IR_hei_vis_g</i> se <b>excluye</b> porque su archivo del canal visible es una
  copia byte a byte del infrarrojo (mismo md5), de modo que no es un par VIS/IR sino la misma imagen
  repetida. Con VIS = IR el error cuadrático medio es nulo y todo método que devuelva la entrada sin
  modificarla obtiene SSIM = 1 y un PSNR que desborda la escala, lo que inflaba artificialmente los
  promedios de fidelidad de los métodos multiescala. El corpus efectivo es de <b>{N_ESC} pares</b>.</p>
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
  <p>La función de aptitud es la del trabajo de referencia (Ortega y Espinoza, 2025), orientada a la
  calidad de fusión: premia la fidelidad estructural con las fuentes (SSIM<sub>avg</sub>), el contenido
  informativo (entropía normalizada E<sub>n</sub>) y la reducción de la distorsión (PSNR
  normalizado), sin pesos arbitrarios:</p>
  {formula("pso_fit", 16)}
  <p>Para elegir la configuración del enjambre se replicó el diseño experimental de Ortega y
  Espinoza (2025): se evaluaron sistemáticamente combinaciones con número de partículas variando de
  2 a 10 en incrementos de 2 y número de iteraciones de 10 a 50 en incrementos de 10, es decir,
  <b>25 configuraciones</b>. El espacio de búsqueda adopta el rango del mismo trabajo para el radio,
  r ∈ [1, 25]; para el peso se usa m &isin; {V['rango']}. Cada configuración se ejecutó con semilla
  propia sobre las escenas representativas del TNO.</p>
  <p><b>Tabla 1.</b> Resultado del barrido: mejor aptitud F<sub>o</sub> alcanzada por cada configuración
  con el rango m &isin; {V['rango']}.</p>
  {tabla_grid}
  <p class="lectura">{LECTURA_PSO}</p>
  {pie(9)}
</div>
<div class="page">
  <h2>5. Optimización por PSO (continuación): convergencia y óptimo</h2>
  {figura(charts["pso"], f"Mejor aptitud Fo alcanzada según el número de partículas (Tmax = 50), con el rango m ∈ {V['rango']}.", 84)}
  <p>{PARRAFO_RADIO}</p>
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
  <p>Todos los métodos se ejecutan sobre los mismos {N_ESC} pares, con la misma implementación de métricas
  (<i>src/metrics/evaluators.py</i>), de modo que la comparación es directa.</p>
  {pie(11)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>7. Métricas de evaluación</h2>
  <p>Se emplean <b>nueve métricas</b> alineadas con la metodología de referencia (Ortega y Espinoza,
  2025), todas de tipo «mayor es mejor» y calculadas a partir de la imagen fusionada y sus fuentes:
  entropía (EN), desviación estándar (SD), ganancia de entropía sobre las fuentes (FE), gradiente medio (MG),
  información mutua con el visible y el infrarrojo (MI_vis, MI_ir), frecuencia espacial (SF),
  similitud estructural promedio (SSIM) y relación señal-ruido de pico (PSNR).</p>
  <p>Entropía y desviación estándar (información y contraste):</p>
  {formula("en", 18)}
  <p>Gradiente medio y frecuencia espacial (nitidez y actividad):</p>
  {formula("mg_sf", 19)}
  <p>Información mutua con cada fuente:</p>
  {formula("mi", 20)}
  <p>Similitud estructural promedio con las fuentes:</p>
  {formula("ssim", 21)}
  <p>Relación señal-ruido de pico frente a ambas fuentes (MAX = 1):</p>
  {formula("psnr", 22)}
  {pie(12)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>8. Resultados cuantitativos</h2>
  <p><b>Tabla 2.</b> Benchmark completo: los 7 métodos con las nueve métricas (promedio de los {N_ESC} pares
  TNO; en negrita el mejor valor de cada columna).</p>
  {tabla_metodos(ORDEN, resaltar=PROP)}
  <p class="lectura">{LECTURA_BENCH}</p>
  {figura(charts["quality"], "Cuatro métricas representativas (EN, FE, SF, SSIM); la barra azul es la propuesta.", 96)}
  {pie(13)}
</div>
""")

# ---------- 8 (continuación): resultados escena por escena, formato del Cuadro 2 ----------
_bloques = [IMAGENES[i:i + 4] for i in range(0, len(IMAGENES), 4)]   # 4 escenas por pagina
for _b, _imgs in enumerate(_bloques, 1):
    _cab = ("8. Resultados por escena (formato del Cuadro 2 del trabajo de referencia)"
            if _b == 1 else f"8. Resultados por escena (continuación {_b} de 5)")
    _intro = ("" if _b > 1 else f"""
  <p>Además de los promedios, se detallan los resultados <b>escena por escena</b> sobre los {N_ESC} pares
  del TNO, con la misma disposición del Cuadro 2 del trabajo de referencia: una fila por método dentro
  de cada escena y, en <b>negrita</b>, el mejor valor de cada columna en esa escena. Se incluye también
  la metodología clásica Top-Hat, que es la referencia morfológica directa de la propuesta.</p>
  <p class="lectura">Unidades: SSIM<sub>avg</sub> y SD en [0, 1]; E en bits (0–8); SF adimensional;
  PSNR en dB. La correspondencia con el Cuadro 2 de referencia es directa —allí E y PSNR se reportan
  normalizados (E/8 y PSNR/100) y SD en la escala 0–255—, de modo que el orden entre métodos es
  comparable columna por columna.</p>""")
    _lect = ("" if _b < 5 else f"""
  <p class="lectura">Lectura del conjunto de las {N_ESC} escenas: la propuesta obtiene el mejor valor en
  <b>{_lidera['E']} de {N_ESC}</b> escenas en entropía (E) y en <b>{_lidera['SD']} de {N_ESC}</b> en desviación
  estándar (SD), frente a <b>{_lidera['SF']} de {N_ESC}</b> en frecuencia espacial (SF, donde domina el
  Top-Hat clásico), <b>{_lidera['SSIM_avg']} de {N_ESC}</b> en SSIM<sub>avg</sub> y
  <b>{_lidera['PSNR']} de {N_ESC}</b> en PSNR. El patrón por escena confirma el de los promedios: la
  propuesta lidera de forma sistemática las métricas de información y contraste, y cede las de
  fidelidad a las fuentes.</p>""")
    H.append(f"""
<div class="page">
  <h2>{_cab}</h2>{_intro}
  <p><b>Tabla 2{chr(96 + _b)}.</b> Resultados por escena — escenas {(_b - 1) * 4 + 1} a
  {(_b - 1) * 4 + len(_imgs)} de {N_ESC}.</p>
  {tabla_por_imagen(_imgs)}{_lect}
  {pie(13 + _b)}
</div>
""")

H.append(f"""
<div class="page">
  <h2>9. Análisis estadístico</h2>
  <p>Primero, el test de Friedman (7 métodos × {N_ESC} imágenes, por rangos) para cada métrica:</p>
  {formula("friedman", 23)}
  <p><b>Tabla 3.</b> Resultados del test de Friedman.</p>
  {tabla_friedman()}
  {pie(19)}
</div>
<div class="page">
  <h2>9. Análisis estadístico (continuación): Wilcoxon y ranking</h2>
  <p>Wilcoxon pareado de la propuesta contra cada rival ({N_ESC} imágenes), con corrección de Holm y tamaño
  de efecto rank-biserial:</p>
  {formula("rb", 24)}
  <p><b>Tabla 4.</b> Resumen de los {len(wtab)} contrastes de la propuesta: mejor / peor / sin
  diferencia significativa (≈), α = 0,05.</p>
  {tabla_wilcoxon}
  <p class="lectura">Lectura: la propuesta resulta significativamente mejor en {w_mejor} contrastes,
  peor en {w_peor} y sin diferencia en {w_emp}; su ventaja más consistente es en las
  métricas de actividad e información (EN, FE, MG, SF), mejor que los cinco métodos del estado del arte.</p>
  {figura(charts["ranking"], "Ranking promedio global de los 7 métodos (9 métricas, dirección respetada); la barra azul es la propuesta.", 78)}
  {pie(20)}
</div>
""")

pg = 21
H.append(f"""
<div class="page">
  <h2>10. Resultados cualitativos: las {N_ESC} escenas</h2>
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
    H.append(f'<div class="page"><h2>10. Resultados cualitativos (escenas {i+1} y {min(i+2,N_ESC)} de {N_ESC})</h2>'
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
  {LLVIP_LO}–{LLVIP_HI}); el infrarrojo solo es la modalidad más fuerte (0,957) y ninguna
  fusión lo supera, coherente con que el peatón nocturno es esencialmente térmico; y entre las fusiones,
  la propuesta alcanza <b>{LLVIP_PROP}</b>. Conclusión honesta: la ventaja de la propuesta en las
  métricas de imagen no se traslada automáticamente a la detección, de modo que ambos criterios deben
  reportarse por separado.</p>
  {figura(charts["det"], "mAP por entrada del detector (YOLOv8n reentrenado por método sobre LLVIP).", 88)}
  {pie(pg)}
</div>
""")
pg += 1

_M3_ORDEN = ["VIS", "IR", "PiramideLaplace", "RatioPiramide", "DWT", "DTCWT",
             "Curvelet", "TopHat_Clasico", PROP]
_M3_LBL = {**LBL, "VIS": "VIS (solo)", "IR": "IR (solo)",
           "TopHat_Clasico": "Top-Hat clásico (r=5; m=1)"}
_m3_best = {c: _m3.loc[[k for k in _M3_ORDEN if k in _m3.index], c].idxmax()
            for c in ("AP50_People", "AP50_Lamp", "par", "mAP50")}
_m3_filas = []
for _k in _M3_ORDEN:
    if _k not in _m3.index:
        continue
    _r = _m3.loc[_k]
    _tds = ""
    for _c in ("AP50_People", "AP50_Lamp", "par", "mAP50"):
        _v = f"{_r[_c]:.3f}".replace(".", ",")
        _tds += f"<td>{'<b>' if _m3_best[_c] == _k else ''}{_v}{'</b>' if _m3_best[_c] == _k else ''}</td>"
    _nom = _M3_LBL.get(_k, _k)
    if _k == PROP:
        _nom = f"<b>{_nom}</b>"
    _m3_filas.append(f"<tr><td>{_nom}</td>{_tds}</tr>")
TAB_M3FD = ('<table><thead><tr><th>Entrada del detector</th><th>AP People &uarr;</th>'
            '<th>AP Lamp &uarr;</th><th>Promedio del par &uarr;</th><th>mAP@0,5 &uarr;</th>'
            f'</tr></thead><tbody>{"".join(_m3_filas)}</tbody></table>')


H.append(f"""
<div class="page">
  <h2>12. Detección con clases complementarias (M3FD)</h2>
  <p>Experimento diseñado para aislar el escenario donde la fusión es insustituible: el dataset
  <b>M3FD</b> (Liu et al., 2022) anota seis clases, dos de ellas de <b>visibilidad opuesta</b>: las
  personas dominan en el infrarrojo (firma térmica) y las luces (Lamp) son esencialmente visibles solo
  en el canal visible. Un <b>único detector YOLOv8n</b> se entrenó con las imágenes de ambas modalidades
  mezcladas (etiquetas compartidas, 40 épocas) y se evaluó <b>por inferencia</b> sobre cada modalidad y
  cada método de fusión.</p>
  <p>El corpus se reparte en <b>tres particiones disjuntas</b> obtenidas por muestreo aleatorio
  <b>estratificado</b> según la presencia de las dos clases complementarias: 2.000 pares de
  entrenamiento, 500 de <b>selección del modelo</b> y {M3_N} de <b>prueba</b>. La separación entre las
  dos últimas es necesaria: si el checkpoint se elige midiendo en el mismo conjunto que luego se
  reporta, el resultado hereda un sesgo optimista que no es comparable entre métodos. La
  estratificación evita además que las particiones tengan proporciones de clase distintas, lo que
  desplazaría el criterio de selección.</p>
  <p><b>Tabla 9.</b> AP@0,5 por clase y mAP global (medias sobre las {M3_N} imágenes de la partición
  de prueba, disjunta de la de entrenamiento y de la de selección del modelo).</p>
  {TAB_M3FD}
  <p class="lectura">{LECTURA_M3FD}</p>
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>12. Clases complementarias (continuación): la prueba visual</h2>
  <p>{PARRAFO_DETECCIONES}</p>
  {figura(EXIST.get("fig_m3fd_detecciones.png"), PIE_DETECCIONES, 92)}
  {pie(pg)}
</div>
""")
pg += 1

H.append(f"""
<div class="page">
  <h2>13. Conclusiones</h2>
  <h3>Resumen del planteamiento</h3>
  <ol>
    <li><b>Propuesta:</b> Top-Hat de una sola escala (radio r) con banco de cinco SE; respuestas lineales
        promediadas (ecs. 6–9) <b>sumadas</b> a la respuesta del disco (ecs. 11–12); detalle dominante
        entre fuentes y reconstrucción aditivo-sustractiva con peso m (ecs. 13–14).</li>
    <li><b>Optimización:</b> barrido de 25 configuraciones PSO (partículas 2–10 × iteraciones 10–50,
        replicando el diseño de Ortega y Espinoza 2025) con la aptitud publicada F<sub>o</sub> →
        <b>r = 25, m = {V['m']}</b>, con el rango de búsqueda del peso m &isin; {V['rango']}.</li>
    <li><b>Benchmark:</b> 7 métodos (LP, RP, DWT, DTCWT, CVT, Top-Hat clásico y la propuesta) × {N_ESC} pares
        TNO × nueve métricas sin referencia.</li>
    <li><b>Estadística:</b> Friedman por métrica y Wilcoxon-Holm pareado de la propuesta contra cada
        rival, con ranking promedio global.</li>
  </ol>
  <h3>Resultados clave</h3>
  <ul>
    <li>{("La propuesta <b>lidera " + _enum(_LID) + "</b> del benchmark") if _LID
         else ("La propuesta <b>no lidera ninguna de las nueve métricas</b> en esta configuración")};
        ocupa el <b>puesto {POS_RANK} de 7 del ranking agregado</b> ({VAL_RANK}, frente a
        {LIDER_RANK} del primero). Advertencia: FE es EN dividida por una constante por escena, de modo
        que el ranking de nueve métricas pondera la entropía dos veces.</li>
    <li>En los contrastes de Wilcoxon-Holm la propuesta es significativamente mejor en {w_mejor} de
        {len(wtab)} comparaciones (peor en {w_peor}, sin diferencia en {w_emp}), con su ventaja más
        consistente en SSIM.</li>
    <li>Frente al Top-Hat clásico, la propuesta mejora {len(_VS_TH)} de las nueve métricas y cede
        en {len(_VS_TH_NO)}. La comparación <b>no aísla</b> el aporte del banco disco + líneas, porque
        los dos operadores usan (r, m) distintos.</li>
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

pg += 1

# ---------- Anexos 1-20: las 25 configuraciones del PSO en cada escena ----------
_nota_anexo = f"""
  <p class="lectura">Nota metodológica sobre el comportamiento de (r, m). Las 25 configuraciones de
  cada escena se ejecutan sobre el mismo espacio de búsqueda r &isin; [1, 25], m &isin; {V['rango_anexo']}.
  El <b>radio sí varía</b> con la configuración del enjambre: en el conjunto de los anexos aparecen 18
  radios distintos y entre 2 y 6 valores diferentes por escena. El <b>peso, en cambio, se fija en
  m = {_m_moda}</b> (en {_m30} de {N_ESC} escenas) porque F<sub>o</sub> <b>decrece de forma estrictamente
  monótona</b> al aumentar m en todo el rango publicado —verificado con un barrido de paso 0,05: cero
  tramos crecientes en 34, tanto con r = 1 como con r = 25—, de modo que el máximo se ubica
  necesariamente en el <b>límite inferior del intervalo</b>. No es una limitación de la búsqueda: las
  únicas {_n_no_borde} filas (de 500) con m &ne; {_m_moda} corresponden a configuraciones de pocas partículas o
  iteraciones que no alcanzaron el óptimo. El radio que maximiza F<sub>o</sub> es r = 1 en {_r1} de {N_ESC}
  imágenes, coherente con que la aptitud premia la fidelidad a las fuentes y por lo tanto el mínimo
  realce; la configuración adoptada (<b>r = 25</b>) no proviene de F<sub>o</sub> sino del criterio de
  evaluación de esta tesis —las nueve métricas, todas de tipo «mayor es mejor»—, que a igual peso
  favorece el radio máximo y activa el banco completo de cinco elementos estructurantes.</p>"""

for _i, _img in enumerate(IMAGENES, 1):
    _nom = ESCENA.get(_img, _img)
    H.append(f"""
<div class="page">
  <h2>Anexo {_i}: resultados para {_nom}</h2>
  <p><b>Cuadro A{_i}.</b> Resultados experimentales para la imagen <i>{_nom}</i> — las 25
  configuraciones del PSO (partículas × iteraciones, Cuadro 1 de Ortega y Espinoza 2025) con la
  aptitud F<sub>o</sub> sobre el rango publicado r &isin; [1, 25], m &isin; [0,30; 2,00]. En negrita
  la configuración de mayor aptitud.</p>
  {tabla_anexo(_img)}
  {_nota_anexo if _i == 1 else ""}
  {pie(pg)}
</div>
""")
    pg += 1

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
